from pytest import MonkeyPatch
import pytest

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

test_parameter_dict = {
    "test_create_admin": {
        "argnames": "name, password1, password2, email",
        "argvalues": [
            (f"admin{i}", "12345678", "12345678", f"admin{i}@test.com")
            for i in range(10)
        ],
    },
    "test_create_user": {
        "argnames": "name, password1, password2, email",
        "argvalues": [
            (f"user{i}", "12345678", "12345678", f"user{i}@test.com") for i in range(20)
        ],
    },
    "test_create_board": {
        "argnames": "admin_name, admin_password1, board_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "board_name": f"board_{i}_{j}",
                        "board_information": f"board_{i}_{j}_information",
                        "board_is_visible": True,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_create_post": {
        "argnames": "admin_name, admin_password1, post_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "post_name": f"post_admin{i}_board{1 + (i * 2) + j}",
                        "post_content": f"post_admin{i}_board{1 + (i * 2) + j}_content",
                        "board_id": 1 + (i * 2) + j,
                        "post_is_file_attached": True,
                        "post_is_visible": True,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_post": {
        "argnames": "name, password1, post_ids, board_ids, ailog_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [1 + (i * 2) + j for j in range(2)],
                [1 + (i * 2) + j for j in range(2)],
                [
                    "id",
                    "name",
                    "content",
                    "board_id",
                    "create_date",
                    "number_of_view",
                    "number_of_comment",
                    "number_of_like",
                    "is_file_attached",
                    "is_visible",
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_posts": {
        "argnames": "name, password1, posts_params, post_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                {
                    "board_id": 1,
                    "post_skip": None,
                    "post_limit": 100,
                },
                [
                    "id",
                    "name",
                    "content",
                    "board_id",
                    "create_date",
                    "number_of_view",
                    "number_of_comment",
                    "number_of_like",
                    "is_file_attached",
                    "is_visible",
                ],
            )
            for i in range(10)
        ],
    },
    "test_update_post": {
        "argnames": "name, password1, post_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "post_id": 1 + (i * 2) + j,
                        "post_name": f"post_admin{i}_board{1 + (i * 2) + j}_update",
                        "post_content": f"post_admin{i}_board{1 + (i * 2) + j}_content_update",
                        "board_id": 1 + (i * 2) + j,
                        "post_is_file_attached": None,
                        "post_is_visible": None,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_delete_post": {
        "argnames": "name, password1, post_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "post_id": 1 + (i * 2) + j,
                        "board_id": 1 + (i * 2) + j,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_create_comment": {
        "argnames": "name, password1, comment_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "comment_content": f"comment_admin{i}_post{1 + (i * 2) + j}_content",
                        "post_id": 1 + (i * 2) + j,
                        "comment_is_file_attached": True,
                        "comment_is_visible": True,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_comment": {
        "argnames": "name, password1, comment_id ,post_id, comment_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [1 + (i * 2) + j for j in range(2)],
                [1 + (i * 2) + j for j in range(2)],
                [
                    "id",
                    "content",
                    "post_id",
                    "create_date",
                    "update_date",
                    "is_file_attached",
                    "is_visible",
                ],
            )
            for i in range(10)
        ],
    },
    "test_get_comments": {
        "argnames": "name, password1, comments_params, comment_columns",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                {
                    "post_id": 1,
                    "comment_skip": None,
                    "comment_limit": 100,
                },
                [
                    "id",
                    "content",
                    "post_id",
                    "create_date",
                    "is_file_attached",
                    "is_visible",
                ],
            )
            for i in range(10)
        ],
    },
    "test_update_comment": {
        "argnames": "name, password1, comment_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "comment_id": 1 + (i * 2) + j,
                        "comment_content": f"comment_admin{i}_post{1 + (i * 2) + j}_content_update",
                        "post_id": 1 + (i * 2) + j,
                        "comment_is_file_attached": None,
                        "comment_is_visible": None,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
    "test_delete_comment": {
        "argnames": "name, password1, comment_args",
        "argvalues": [
            (
                f"admin{i}",
                "12345678",
                [
                    {
                        "comment_id": 1 + (i * 2) + j,
                        "post_id": 1 + (i * 2) + j,
                    }
                    for j in range(2)
                ],
            )
            for i in range(10)
        ],
    },
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
        assert response_test.json() == {"result": "success"}

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")
        post = (
            data_base.query(Post).filter_by(name=post_name, board_id=board_id).first()
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

        for post_column in post_columns:
            assert post_column in response_test_json

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

            for ailog_column in post_columns:
                assert ailog_column in post
        data_base.close()

    def update_post(
        self,
        post_id,
        post_name,
        post_content,
        board_id,
        post_is_file_attached,
        post_is_visible,
        access_token: str,
    ):
        response_test = client.put(
            URL_BOARD_UPDATE_POST,
            json={
                "id": post_id,
                "name": post_name,
                "content": post_content,
                "board_id": board_id,
                "is_file_attached": post_is_file_attached,
                "is_visible": post_is_visible,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_post_test(
        self,
        post_id,
        post_name,
        post_content,
        board_id,
        post_is_file_attached,
        post_is_visible,
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
        assert response_test.json() == {"result": "success"}

        user_id = validate_and_decode_user_access_token(
            data_base=data_base, token=access_token
        ).get("user_id")
        comment = (
            data_base.query(Comment)
            .filter_by(user_id=user_id, post_id=post_id, content=comment_content)
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

        for comment_column in comment_columns:
            assert comment_column in response_test_json

        data_base.close()

    def get_comments(self, post_id, comment_skip, comment_limit, access_token: str):
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

            for comment_column in comment_columns:
                assert comment_column in comment

        data_base.close()

    def update_comment(
        self,
        comment_id,
        comment_content,
        post_id,
        comment_is_file_attached,
        comment_is_visible,
        access_token: str,
    ):
        response_test = client.put(
            URL_BOARD_UPDATE_COMMENT,
            json={
                "id": comment_id,
                "content": comment_content,
                "post_id": post_id,
                "is_file_attached": comment_is_file_attached,
                "is_visible": comment_is_visible,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        return response_test

    def update_comment_test(
        self,
        comment_id,
        comment_content,
        post_id,
        comment_is_file_attached,
        comment_is_visible,
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

    @pytest.mark.parametrize(**test_parameter_dict["test_create_admin"])
    def test_create_admin(self, name, password1, password2, email):
        admin_test_methods.create_admin(name, password1, password2, email)
        admin_test_methods.create_admin_test(name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_user"])
    def test_create_user(self, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test(
            response_test, name, password1, email
        )

    @pytest.mark.parametrize(**test_parameter_dict["test_create_board"])
    def test_create_board(self, admin_name, admin_password1, board_args):
        for board_arg in board_args:
            response_login = user_test_methods.login_user(admin_name, admin_password1)
            response_login_json: dict = response_login.json()
            access_token = response_login_json.get("access_token")

            response_test = admin_test_methods.create_board(
                **board_arg, access_token=access_token
            )
            admin_test_methods.create_board_test(
                **board_arg, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_create_post"])
    def test_create_post(self, admin_name, admin_password1, post_args):
        response_login = user_test_methods.login_user(admin_name, admin_password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for post_arg in post_args:
            response_test = post_test_methods.create_post(
                **post_arg, access_token=access_token
            )
            post_test_methods.create_post_test(
                **post_arg, access_token=access_token, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_get_post"])
    def test_get_post(self, name, password1, post_ids, board_ids, ailog_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for post_id, board_id in zip(post_ids, board_ids):
            response_test = post_test_methods.get_post(
                post_id, board_id, access_token=access_token
            )
            post_test_methods.get_post_test(ailog_columns, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_get_posts"])
    def test_get_posts(self, name, password1, posts_params, post_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = post_test_methods.get_posts(
            **posts_params, access_token=access_token
        )
        post_test_methods.get_posts_test(post_columns, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_update_post"])
    def test_update_post(
        self,
        name,
        password1,
        post_args,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for post_arg in post_args:
            response_test = post_test_methods.update_post(
                **post_arg, access_token=access_token
            )
            post_test_methods.update_post_test(**post_arg, response_test=response_test)

    @pytest.mark.parametrize(**test_parameter_dict["test_delete_post"])
    def test_delete_post(self, name, password1, post_args):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for post_arg in post_args:
            response_test = post_test_methods.delete_post(
                **post_arg, access_token=access_token
            )
            post_test_methods.delete_post_test(**post_arg, response_test=response_test)


class TestComment:
    def test_data_base_init(self):
        main_test_methods.data_base_init()

    @pytest.mark.parametrize(**test_parameter_dict["test_create_admin"])
    def test_create_admin(self, name, password1, password2, email):
        admin_test_methods.create_admin(name, password1, password2, email)
        admin_test_methods.create_admin_test(name, password1, email)

    @pytest.mark.parametrize(**test_parameter_dict["test_create_user"])
    def test_create_user(self, name, password1, password2, email):
        response_test = user_test_methods.create_user(name, password1, password2, email)
        user_test_methods.create_user_test(
            response_test, name, password1, email
        )

    @pytest.mark.parametrize(**test_parameter_dict["test_create_board"])
    def test_create_board(self, admin_name, admin_password1, board_args):
        for board_arg in board_args:
            response_login = user_test_methods.login_user(admin_name, admin_password1)
            response_login_json: dict = response_login.json()
            access_token = response_login_json.get("access_token")

            response_test = admin_test_methods.create_board(
                **board_arg, access_token=access_token
            )
            admin_test_methods.create_board_test(
                **board_arg, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_create_post"])
    def test_create_post(self, admin_name, admin_password1, post_args):
        response_login = user_test_methods.login_user(admin_name, admin_password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for post_arg in post_args:
            response_test = post_test_methods.create_post(
                **post_arg, access_token=access_token
            )
            post_test_methods.create_post_test(
                **post_arg, access_token=access_token, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_create_comment"])
    def test_create_comment(self, name, password1, comment_args):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for comment_arg in comment_args:
            response_test = comment_test_methods.create_comment(
                **comment_arg, access_token=access_token
            )
            comment_test_methods.create_comment_test(
                **comment_arg, access_token=access_token, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_get_comment"])
    def test_get_comment(self, name, password1, comment_id, post_id, comment_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for post_id, board_id in zip(comment_id, post_id):
            response_test = comment_test_methods.get_comment(
                post_id, board_id, access_token=access_token
            )
            comment_test_methods.get_comment_test(
                comment_columns, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_get_comments"])
    def test_get_comments(self, name, password1, comments_params, comment_columns):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        response_test = comment_test_methods.get_comments(
            **comments_params, access_token=access_token
        )
        comment_test_methods.get_comments_test(
            comment_columns, response_test=response_test
        )

    @pytest.mark.parametrize(**test_parameter_dict["test_update_comment"])
    def test_update_comment(
        self,
        name,
        password1,
        comment_args,
    ):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for comment_arg in comment_args:
            response_test = comment_test_methods.update_comment(
                **comment_arg, access_token=access_token
            )
            comment_test_methods.update_comment_test(
                **comment_arg, response_test=response_test
            )

    @pytest.mark.parametrize(**test_parameter_dict["test_delete_comment"])
    def test_delete_comment(self, name, password1, comment_args):
        response_login = user_test_methods.login_user(name, password1)
        response_login_json: dict = response_login.json()
        access_token = response_login_json.get("access_token")

        for comment_arg in comment_args:
            response_test = comment_test_methods.delete_comment(
                **comment_arg, access_token=access_token
            )
            comment_test_methods.delete_comment_test(
                **comment_arg, response_test=response_test
            )
