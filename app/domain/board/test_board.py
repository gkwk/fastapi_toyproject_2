from pytest import MonkeyPatch
import pytest
import json

from fastapi.testclient import TestClient
from httpx import Response


from main import app
from domain.admin.admin_crud import create_admin_with_terminal
from models import User, Board, Post, Comment
from database import session_local
from auth import validate_and_decode_user_access_token
import v1_urn
from domain.user.test_user import user_test_methods
from domain.admin.test_admin import admin_test_methods
from test_main import main_test_methods


client = TestClient(app)


url_dict = {
    "URL_USER_CREATE_USER": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.USER_PREFIX,
        v1_urn.USER_CREATE_USER,
    ],
    "URL_USER_LOGIN_USER": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.USER_PREFIX,
        v1_urn.USER_LOGIN_USER,
    ],
    "URL_ADMIN_CREATE_BOARD": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.ADMIN_PREFIX,
        v1_urn.ADMIN_CREATE_BOARD,
    ],
    "URL_BOARD_CREATE_POST": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_CREATE_POST,
    ],
    "URL_BOARD_GET_POST": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_GET_POST,
    ],
    "URL_BOARD_GET_POSTS": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_GET_POSTS,
    ],
    "URL_BOARD_UPDATE_POST": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_UPDATE_POST,
    ],
    "URL_BOARD_DELETE_POST": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_DELETE_POST,
    ],
    "URL_BOARD_CREATE_COMMNET": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_CREATE_COMMNET,
    ],
    "URL_BOARD_GET_COMMENT": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_GET_COMMENT,
    ],
    "URL_BOARD_GET_COMMENTS": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_GET_COMMENTS,
    ],
    "URL_BOARD_UPDATE_COMMENT": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_UPDATE_COMMENT,
    ],
    "URL_BOARD_DELETE_COMMENT": [
        v1_urn.API_V1_ROUTER_PREFIX,
        v1_urn.BOARD_PREFIX,
        v1_urn.BOARD_DELETE_COMMENT,
    ],
}

URL_USER_CREATE_USER = "".join(url_dict.get("URL_USER_CREATE_USER"))
URL_USER_LOGIN_USER = "".join(url_dict.get("URL_USER_LOGIN_USER"))
URL_ADMIN_CREATE_BOARD = "".join(url_dict.get("URL_ADMIN_CREATE_BOARD"))
URL_BOARD_CREATE_POST = "".join(url_dict.get("URL_BOARD_CREATE_POST"))
URL_BOARD_GET_POST = "".join(url_dict.get("URL_BOARD_GET_POST"))
URL_BOARD_GET_POSTS = "".join(url_dict.get("URL_BOARD_GET_POSTS"))
URL_BOARD_UPDATE_POST = "".join(url_dict.get("URL_BOARD_UPDATE_POST"))
URL_BOARD_DELETE_POST = "".join(url_dict.get("URL_BOARD_DELETE_POST"))
URL_BOARD_CREATE_COMMNET = "".join(url_dict.get("URL_BOARD_CREATE_COMMNET"))
URL_BOARD_GET_COMMENT = "".join(url_dict.get("URL_BOARD_GET_COMMENT"))
URL_BOARD_GET_COMMENTS = "".join(url_dict.get("URL_BOARD_GET_COMMENTS"))
URL_BOARD_UPDATE_COMMENT = "".join(url_dict.get("URL_BOARD_UPDATE_COMMENT"))
URL_BOARD_DELETE_COMMENT = "".join(url_dict.get("URL_BOARD_DELETE_COMMENT"))


def parameter_data_loader(path):
    test_data = {"argnames": None, "argvalues": []}

    with open(path, "r", encoding="UTF-8") as f:
        json_data: dict = json.load(f)

    test_data["argnames"] = "pn," + json_data.get("argnames")

    for value in json_data.get("argvalues_pass", []):
        test_data["argvalues"].append(tuple([1, *value]))

    for value in json_data.get("argvalues_fail", []):
        value_temp = pytest.param(
            0, *value[:-1], marks=pytest.mark.xfail(reason=value[-1])
        )
        test_data["argvalues"].append(value_temp)

    return test_data


ID_DICT_ADMIN_ID = "admin_id"
ID_DICT_USER_ID = "user_id"
ID_DICT_BOARD_ID = "board_id"
ID_DICT_POST_ID = "post_id"
ID_DICT_COMMENT_ID = "comment_id"


id_list_dict = {
    ID_DICT_ADMIN_ID: [],
    ID_DICT_USER_ID: [],
    ID_DICT_BOARD_ID: [],
    ID_DICT_POST_ID: [],
    ID_DICT_COMMENT_ID: [],
}

id_iterator_dict = {
    ID_DICT_ADMIN_ID: iter([]),
    ID_DICT_USER_ID: iter([]),
    ID_DICT_BOARD_ID: iter([]),
    ID_DICT_POST_ID: iter([]),
    ID_DICT_COMMENT_ID: iter([]),
}


def id_list_append(id_dict_str, value):
    id_list_dict[id_dict_str].append(value)


def id_iterator_next(pn, id_dict_str) -> int | None:
    if pn:
        try:
            next_id = id_iterator_dict[id_dict_str].__next__()
        except StopIteration:
            id_iterator_dict[id_dict_str] = iter(id_list_dict[id_dict_str])
            next_id = id_iterator_dict[id_dict_str].__next__()

        return next_id

    return None


def id_list_clear(id_dict_str):
    id_list_dict[id_dict_str] = []


def id_iterator_clear(id_dict_str):
    id_iterator_dict[id_dict_str] = iter(id_list_dict[id_dict_str])


class PostTestMethods:
    def create_post(
        self,
        post_name,
        post_content,
        board_id,
        post_is_file_attached,
        post_is_visible,
        access_token: str,
    ):

        response_test = client.post(
            URL_BOARD_CREATE_POST,
            data={
                "name": post_name,
                "content": post_content,
                "board_id": board_id,
                "is_file_attached": post_is_file_attached,
                "is_visible": post_is_visible,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def create_post_test(
        self,
        post_name,
        post_content,
        board_id,
        post_is_file_attached,
        post_is_visible,
        access_token: str,
        response_test: Response,
    ):
        data_base = session_local()
        assert response_test.status_code == 201
        response_test_json: dict = response_test.json()
        assert response_test_json.get("result")
        assert response_test_json.get("id") > 0

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")
        post = (
            data_base.query(Post)
            .filter_by(id=response_test_json.get("id"), board_id=board_id)
            .first()
        )

        assert post.user_id == user_id
        assert post.board_id == board_id
        assert post.name == post_name
        assert post.content == post_content
        assert post.create_date != None
        assert post.update_date == None
        assert post.number_of_comment == 0
        assert post.number_of_view == 0
        assert post.number_of_like == 0
        assert post.is_file_attached == post_is_file_attached
        assert post.is_visible == post_is_visible
        data_base.close()

    def get_post(self, post_id, board_id, access_token: str):

        response_test = client.get(
            URL_BOARD_GET_POST,
            params={
                "id": post_id,
                "board_id": board_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_post_test(self, post_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert set(post_columns) == set(response_test_json.keys())

        data_base.close()

    def get_posts(self, board_id, post_skip, post_limit, access_token: str):
        params = {}
        if board_id != None:
            params["board_id"] = board_id
        if post_skip != None:
            params["skip"] = post_skip
        if post_limit != None:
            params["limit"] = post_limit

        response_test = client.get(
            URL_BOARD_GET_POSTS,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_posts_test(self, post_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for post in response_test_json.get("posts"):
            post: dict
            assert set(post_columns) == set(post.keys())
        data_base.close()

    def update_post(
        self,
        *,
        post_id,
        post_name=None,
        post_content=None,
        board_id,
        post_is_file_attached=None,
        post_is_visible=None,
        access_token: str,
    ):
        params = {}
        if post_name != None:
            params["name"] = post_name
        if post_content != None:
            params["content"] = post_content
        if post_is_file_attached != None:
            params["is_file_attached"] = post_is_file_attached
        if post_is_visible != None:
            params["is_visible"] = post_is_visible

        response_test = client.put(
            URL_BOARD_UPDATE_POST,
            json={"name": post_name, "board_id": board_id, "id": post_id, **params},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_post_test(
        self,
        *,
        post_id,
        post_name=None,
        post_content=None,
        board_id,
        post_is_file_attached=None,
        post_is_visible=None,
        response_test: Response,
    ):
        data_base = session_local()

        assert response_test.status_code == 204

        post = data_base.query(Post).filter_by(id=post_id, board_id=board_id).first()

        if post_name != None:
            assert post.name == post_name
        if post_content != None:
            assert post.content == post_content
        if post_is_file_attached != None:
            assert post.is_file_attached == post_is_file_attached
        if post_is_visible != None:
            assert post.is_visible == post_is_visible

        data_base.close()

    def delete_post(self, post_id, board_id, access_token: str):

        response_test = client.delete(
            URL_BOARD_DELETE_POST,
            params={
                "id": post_id,
                "board_id": board_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def delete_post_test(self, post_id, board_id, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 204

        post = data_base.query(Post).filter_by(id=post_id, board_id=board_id).first()
        assert post == None

        data_base.close()


class CommentTestMethods:
    def create_comment(
        self,
        comment_content,
        post_id,
        comment_is_file_attached,
        comment_is_visible,
        access_token: str,
    ):

        response_test = client.post(
            URL_BOARD_CREATE_COMMNET,
            data={
                "content": comment_content,
                "post_id": post_id,
                "is_file_attached": comment_is_file_attached,
                "is_visible": comment_is_visible,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def create_comment_test(
        self,
        comment_content,
        post_id,
        comment_is_file_attached,
        comment_is_visible,
        access_token: str,
        response_test: Response,
    ):
        data_base = session_local()
        assert response_test.status_code == 201
        response_test_json: dict = response_test.json()
        assert response_test_json.get("result")
        assert response_test_json.get("id") > 0

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")
        comment = (
            data_base.query(Comment)
            .filter_by(
                user_id=user_id, post_id=post_id, id=response_test_json.get("id")
            )
            .first()
        )

        assert comment.user_id == user_id
        assert comment.post_id == post_id
        assert comment.content == comment_content
        assert comment.create_date != None
        assert comment.update_date == None
        assert comment.is_file_attached == comment_is_file_attached
        assert comment.is_visible == comment_is_visible

        data_base.close()

    def get_comment(self, comment_id, post_id, access_token: str):
        response_test = client.get(
            URL_BOARD_GET_COMMENT,
            params={
                "id": comment_id,
                "post_id": post_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_comment_test(self, comment_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert set(comment_columns) == set(response_test_json.keys())

        data_base.close()

    def get_comments(
        self, *, post_id, comment_skip=None, comment_limit=None, access_token: str
    ):
        params = {}
        if post_id != None:
            params["post_id"] = post_id
        if comment_skip != None:
            params["skip"] = comment_skip
        if comment_limit != None:
            params["limit"] = comment_limit

        response_test = client.get(
            URL_BOARD_GET_COMMENTS,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def get_comments_test(self, comment_columns, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 200

        response_test_json: dict = response_test.json()

        assert response_test_json.get("total") >= 0

        for comment in response_test_json.get("comments"):
            comment: dict
            assert set(comment_columns) == set(comment.keys())

        data_base.close()

    def update_comment(
        self,
        *,
        comment_id,
        comment_content=None,
        post_id,
        comment_is_file_attached=None,
        comment_is_visible=None,
        access_token: str,
    ):
        params = {}
        if comment_content != None:
            params["content"] = comment_content
        if comment_is_file_attached != None:
            params["is_file_attached"] = comment_is_file_attached
        if comment_is_visible != None:
            params["is_visible"] = comment_is_visible

        response_test = client.put(
            URL_BOARD_UPDATE_COMMENT,
            json={"id": comment_id, "post_id": post_id, **params},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_comment_test(
        self,
        *,
        comment_id,
        comment_content=None,
        post_id,
        comment_is_file_attached=None,
        comment_is_visible=None,
        response_test: Response,
    ):
        data_base = session_local()

        assert response_test.status_code == 204

        comment = (
            data_base.query(Comment).filter_by(id=comment_id, post_id=post_id).first()
        )

        if comment_content != None:
            assert comment.content == comment_content
        if comment_is_file_attached != None:
            assert comment.is_file_attached == comment_is_file_attached
        if comment_is_visible != None:
            assert comment.is_visible == comment_is_visible

        data_base.close()

    def delete_comment(self, comment_id, post_id, access_token: str):
        response_test = client.delete(
            URL_BOARD_DELETE_COMMENT,
            params={
                "id": comment_id,
                "post_id": post_id,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def delete_comment_test(self, comment_id, post_id, response_test: Response):
        data_base = session_local()

        assert response_test.status_code == 204

        comment = (
            data_base.query(Comment).filter_by(id=comment_id, post_id=post_id).first()
        )

        assert comment == None

        data_base.close()


post_test_methods = PostTestMethods()
comment_test_methods = CommentTestMethods()


class TestPost:
    def test_data_base_init(self):
        main_test_methods.data_base_init()
        for id in id_list_dict:
            id_list_clear(id)
            id_iterator_clear(id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_admin.json")
    )
    def test_create_admin(self, pn, name, password1, password2, email):
        admin_id = admin_test_methods.create_admin(name, password1, password2, email)
        id_list_append(ID_DICT_ADMIN_ID, admin_id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_user.json")
    )
    def test_create_user(self, pn, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        id_list_append(ID_DICT_USER_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_board.json")
    )
    def test_create_board(self, pn, admin_name, admin_password1, board_arg):
        response_login = user_test_methods.login_user(admin_name, admin_password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = admin_test_methods.create_board(
            **board_arg, access_token=access_token
        )
        admin_test_methods.create_board_test(**board_arg, response_test=response_test)
        id_list_append(ID_DICT_BOARD_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_post.json")
    )
    def test_create_post(self, pn, name, password1, post_arg):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        board_id = id_iterator_next(pn, ID_DICT_BOARD_ID)

        response_test = post_test_methods.create_post(
            board_id=board_id, **post_arg, access_token=access_token
        )
        post_test_methods.create_post_test(
            board_id=board_id,
            **post_arg,
            access_token=access_token,
            response_test=response_test,
        )
        id_list_append(ID_DICT_POST_ID, (board_id, response_test.json().get("id")))

    @pytest.mark.parametrize(**parameter_data_loader("domain/board/test_get_post.json"))
    def test_get_post(self, pn, name, password1, post_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        board_id, post_id = id_iterator_next(pn, ID_DICT_POST_ID)

        response_test = post_test_methods.get_post(
            post_id, board_id, access_token=access_token
        )
        post_test_methods.get_post_test(post_columns, response_test=response_test)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_get_posts.json")
    )
    def test_get_posts(self, pn, name, password1, posts_params, post_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")
        board_id = id_iterator_next(pn, ID_DICT_BOARD_ID)

        response_test = post_test_methods.get_posts(
            board_id=board_id, **posts_params, access_token=access_token
        )
        post_test_methods.get_posts_test(post_columns, response_test=response_test)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_update_post.json")
    )
    def test_update_post(
        self,
        pn,
        name,
        password1,
        post_arg,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        board_id, post_id = id_iterator_next(pn, ID_DICT_POST_ID)

        response_test = post_test_methods.update_post(
            board_id=board_id, post_id=post_id, **post_arg, access_token=access_token
        )
        post_test_methods.update_post_test(
            board_id=board_id, post_id=post_id, **post_arg, response_test=response_test
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_delete_post.json")
    )
    def test_delete_post(self, pn, name, password1):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        board_id, post_id = id_iterator_next(pn, ID_DICT_POST_ID)

        response_test = post_test_methods.delete_post(
            post_id, board_id, access_token=access_token
        )
        post_test_methods.delete_post_test(
            post_id, board_id, response_test=response_test
        )


class TestComment:
    def test_data_base_init(self):
        main_test_methods.data_base_init()
        for id in id_list_dict:
            id_list_clear(id)
            id_iterator_clear(id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_admin.json")
    )
    def test_create_admin(self, pn, name, password1, password2, email):
        admin_id = admin_test_methods.create_admin(name, password1, password2, email)
        id_list_append(ID_DICT_ADMIN_ID, admin_id)

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_user.json")
    )
    def test_create_user(self, pn, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        id_list_append(ID_DICT_USER_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_board.json")
    )
    def test_create_board(self, pn, admin_name, admin_password1, board_arg):
        response_login = user_test_methods.login_user(admin_name, admin_password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = admin_test_methods.create_board(
            **board_arg, access_token=access_token
        )
        admin_test_methods.create_board_test(**board_arg, response_test=response_test)
        id_list_append(ID_DICT_BOARD_ID, response_test.json().get("id"))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_post.json")
    )
    def test_create_post(self, pn, name, password1, post_arg):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        board_id = id_iterator_next(pn, ID_DICT_BOARD_ID)

        response_test = post_test_methods.create_post(
            board_id=board_id, **post_arg, access_token=access_token
        )
        post_test_methods.create_post_test(
            board_id=board_id,
            **post_arg,
            access_token=access_token,
            response_test=response_test,
        )
        id_list_append(ID_DICT_POST_ID, (board_id, response_test.json().get("id")))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_create_comment.json")
    )
    def test_create_comment(self, pn, name, password1, comment_arg):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        board_id, post_id = id_iterator_next(pn, ID_DICT_POST_ID)

        response_test = comment_test_methods.create_comment(
            post_id=post_id, **comment_arg, access_token=access_token
        )
        comment_test_methods.create_comment_test(
            post_id=post_id,
            **comment_arg,
            access_token=access_token,
            response_test=response_test,
        )
        id_list_append(ID_DICT_COMMENT_ID, (post_id, response_test.json().get("id")))

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_get_comment.json")
    )
    def test_get_comment(self, pn, name, password1, comment_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        post_id, comment_id = id_iterator_next(pn, ID_DICT_COMMENT_ID)

        response_test = comment_test_methods.get_comment(
            comment_id, post_id, access_token=access_token
        )
        comment_test_methods.get_comment_test(
            comment_columns, response_test=response_test
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_get_comments.json")
    )
    def test_get_comments(self, pn, name, password1, comments_params, comment_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        post_id, comment_id = id_iterator_next(pn, ID_DICT_COMMENT_ID)

        response_test = comment_test_methods.get_comments(
            post_id=post_id, **comments_params, access_token=access_token
        )
        comment_test_methods.get_comments_test(
            comment_columns, response_test=response_test
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_update_comment.json")
    )
    def test_update_comment(
        self,
        pn,
        name,
        password1,
        comment_arg,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        post_id, comment_id = id_iterator_next(pn, ID_DICT_COMMENT_ID)

        response_test = comment_test_methods.update_comment(
            comment_id=comment_id,
            post_id=post_id,
            **comment_arg,
            access_token=access_token,
        )
        comment_test_methods.update_comment_test(
            comment_id=comment_id,
            post_id=post_id,
            **comment_arg,
            response_test=response_test,
        )

    @pytest.mark.parametrize(
        **parameter_data_loader("domain/board/test_delete_comment.json")
    )
    def test_delete_comment(self, pn, name, password1):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        post_id, comment_id = id_iterator_next(pn, ID_DICT_COMMENT_ID)

        response_test = comment_test_methods.delete_comment(
            comment_id=comment_id, post_id=post_id, access_token=access_token
        )
        comment_test_methods.delete_comment_test(
            comment_id=comment_id, post_id=post_id, response_test=response_test
        )
