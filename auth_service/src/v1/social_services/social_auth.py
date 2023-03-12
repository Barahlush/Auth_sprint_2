from http import HTTPStatus
from typing import Any, cast

from authlib.integrations.flask_client import (  # type: ignore
    FlaskRemoteApp,
    OAuth,
)
from flask import (
    Request,
    Response,
    redirect,
    request,
    url_for,
)
from flask_restful import Resource, reqparse  # type: ignore
from loguru import logger
from src.v1.core.config import settings

from src.v1.core.controllers import BaseController
from src.v1.core.jwt import create_token_pair, set_token_cookies
from src.v1.core.models import LoginEvent, SocialAccount, User
from src.v1.core.security import generate_salt, hash_password
from src.v1.db.datastore import datastore
from src.v1.social_services.base import BaseDataParser, SocialUserModel
from src.v1.social_services.google_data import GoogleDataParser
from src.v1.social_services.yandex_data import YandexDataParser

sign_in_parser = reqparse.RequestParser()
sign_in_parser.add_argument(
    'User-Agent', dest='fingerprint', location='headers'
)


def social_login_factory(oauth: OAuth, name: str) -> type:
    class SocialLogin(Resource, BaseController): # type: ignore
        """
        Класс логина в соц сети, на вход принимает имя соцсети.
        В случае успеха - переход на класс авторизации через соцсеть.
        """

        def __init__(self):
            super().__init__()
            self.__qualname__ = self.__class__.__name__

        def get(self, _request: Request) -> Response:
            client = oauth.create_client(name)
            if not client:
                return {
                    'message': 'invalid social service'
                }, HTTPStatus.UNAUTHORIZED

            if settings.USE_NGINX:
                scheme = 'https'
            else:
                scheme = 'http'
            if name == 'google':
                endpoint = 'views.social_'
            else:
                endpoint = 'views.social'
            redirect_uri = url_for(
                endpoint=endpoint,
                social_name=name,
                _external=True,
                _scheme=scheme,
            )
            return client.authorize_redirect(redirect_uri)
    return SocialLogin


def social_auth_factory(oauth: OAuth, name: str) -> type:
    class CallBack(Resource, BaseController):  # type: ignore
        """
        Класс авторизации через соцсеть. На вход принимает имя соцсети.
        Получает данные о пользователе после авторизации в соцсети.
        Создаём нового пользователя, если не находят его.
        Добавляем привязку соцсети к пользователю (опять же если её не было)

        В самом конце логируем заход пользователя с access и refresh jwt
        """
        def __init__(self):
            super().__init__()
            self.__qualname__ = self.__class__.__name__

        def get(self, _request: Request) -> Response:
            sign_in_parser.parse_args()
            client: FlaskRemoteApp = oauth.create_client(name)

            if not client:
                return {
                    'message': 'invalid social service'
                }, HTTPStatus.UNAUTHORIZED

            token = client.authorize_access_token()
            user_data_parser = self.get_user_data_parser(client.name)
            user_data = user_data_parser(client, token).get_user_info()
            user = self.get_user_id_from_social_account(
                social_name=client.name, user_data=user_data
            )
            logger.info('user_data {}', user_data)
            logger.info('user {}', user)

            user_agent = request.headers.get('User-Agent')

            user_history = LoginEvent(
                history=user_agent,
                user=user,
            )
            user_history.save()

            response = cast(Response, redirect(url_for('views.index')))

            access_token, refresh_token = create_token_pair(user)

            set_token_cookies(
                response,
                access_token,
                refresh_token,
            )

            return response

        def get_user_id_from_social_account(
            self, social_name: str, user_data: SocialUserModel
        ) -> Any:
            """
            Получения user_id из SocialAccount.
            Если social_account не создан - он создается.
            """
            logger.info('user_data.open_id: {}', user_data.open_id)
            user = User.get_or_none(email=user_data.email)

            if user is None:
                user = datastore.create_user(
                    email=user_data.email,
                    password_hash=hash_password(user_data.email, 'text'),
                    fs_uniquifier=generate_salt(),
                    roles=['user'],
                )

            if account := SocialAccount.get_or_none(
                    SocialAccount.social_id == user_data.open_id
            ):
                logger.info('find_account: {}', account)
            else:
                account = SocialAccount(
                    social_id=user_data.open_id,
                    social_name=social_name,
                    user=user
                )
                account.save()
                logger.info('create account: {}', account)

            return user

        def get_user_data_parser(
                self, client_name: str
        ) -> type[BaseDataParser]:
            """
            Метод возвращает класс для парсинга данных полученных от сервиса
            """
            parsers = {'yandex': YandexDataParser, 'google': GoogleDataParser}
            return parsers[client_name]
    return CallBack
