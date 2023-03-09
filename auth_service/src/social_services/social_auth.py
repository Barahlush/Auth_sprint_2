from http import HTTPStatus

from authlib.integrations.flask_client import (  # type: ignore
    FlaskRemoteApp,
    OAuth,
)
from flask import Request, Response, jsonify, make_response, url_for
from flask_restful import Resource, reqparse  # type: ignore
from loguru import logger

from src.core.controllers import BaseController
from src.core.jwt import create_token_pair
from src.core.models import SocialAccount
from src.db.datastore import datastore
from src.social_services.base import BaseDataParser, SocialUserModel
from src.social_services.config import USE_NGINX
from src.social_services.google_data import GoogleDataParser
from src.social_services.yandex_data import YandexDataParser

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

        def get(self, _request: Request) -> Response:
            client = oauth.create_client(name)
            if not client:
                return {
                    'message': 'invalid social service'
                }, HTTPStatus.UNAUTHORIZED

            if USE_NGINX:
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
            user_id = self.get_user_id_from_social_account(
                social_name=client.name, user_data=user_data
            )
            logger.info('user_data {}', user_data)
            user = datastore.find_user(id=user_id)
            datastore.add_role_to_user(user=user, role='user')
            access_token, refresh_token = create_token_pair(user)
            return make_response(
                jsonify(access_token=access_token, refresh_token=refresh_token),
                HTTPStatus.OK,
            )

        def get_user_id_from_social_account(
            self, social_name: str, user_data: SocialUserModel
        ) -> str:
            """
            Получения user_id из SocialAccount.
            Если social_account не создан - он создается.
            """
            if not SocialAccount.is_social_exist(user_data.open_id):

                social_account = SocialAccount.create_social_connect(
                    social_id=user_data.open_id,
                    social_name=social_name,
                    user_fields=user_data.dict(),
                )
                datastore.create_social_account(social_account)
            return SocialAccount.select().where(
                SocialAccount.social_id == user_data.open_id
            )

        def get_user_data_parser(self, client_name: str) -> type[BaseDataParser]:
            """
            Метод, возвращающий класс для парсинга данных полученных от сервиса.
            """
            parsers = {'yandex': YandexDataParser, 'google': GoogleDataParser}
            return parsers[client_name]
    return CallBack
