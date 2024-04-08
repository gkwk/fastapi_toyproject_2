from models import Post, PostViewIncrement
from database import get_data_base_decorator
from sqlalchemy.orm import Session

from celery_app.celery import celery_app


@celery_app.task(name="update_post_view_counts")
@get_data_base_decorator
def update_post_view_counts(data_base: Session):
    increments = data_base.query(PostViewIncrement).all()

    post_view_counts = dict()
    for increment in increments:
        post_view_counts[increment.post_id] = (
            post_view_counts.get(increment.post_id, 0) + 1
        )

    for post_id, count in post_view_counts.items():
        data_base.query(Post).filter(Post.id == post_id).update(
            {Post.number_of_view: Post.number_of_view + count},
            synchronize_session=False,
        )

    data_base.query(PostViewIncrement).delete()

    data_base.commit()
