from enum import Enum

from authlib.integrations.flask_client import OAuth  # type: ignore
from src.v1.core.config import settings

from src.v1.core.views import add_route
from src.v1.social_services.social_auth import (
    social_auth_factory,
    social_login_factory,
)


class Services(Enum):
    GOOGLE = 'google'
    YANDEX = 'yandex'


def google_register(oauth: OAuth) -> None:
    """
    Регистрирует гугл как сервис в котором можно пройти oauth
    После регистрации oauth получает атрибут с именем указанным в name

    :param oauth:
    :return:
    """
    oauth.register(
        name=Services.GOOGLE.value,
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url=settings.GOOGLE_DISCOVERY_URL,
        client_kwargs=settings.GOOGLE_OAUTH_SETTINGS,
    )


def yandex_register(oauth: OAuth) -> None:
    """
    Регистрирует yandex как сервис в котором можно пройти oauth
    После регистрации oauth получает атрибут с именем указанным в name

    :param oauth:
    :return:
    """
    oauth.register(
        name=Services.YANDEX.value,
        client_id=settings.YANDEX_APP_ID,
        client_secret=settings.YANDEX_APP_SECRET,
        api_base_url=settings.YANDEX_API_BASE_URL,
        access_token_url=settings.YANDEX_ACCESS_TOKEN_URL,
        authorize_url=settings.YANDEX_AUTHORIZE_URL,
    )


def create_oauth_services(oauth: OAuth) -> None:
    google_register(oauth)
    yandex_register(oauth)
    add_route(
        '/google', ['GET'], 'google', social_login_factory(oauth, 'google')
    )
    add_route(
        '/google/auth',
        ['GET'],
        'social_',
        social_auth_factory(oauth, 'google'),
    )

    add_route(
        '/yandex', ['GET'], 'yandex', social_login_factory(oauth, 'yandex')
    )
    add_route(
        '/yandex/auth', ['GET'], 'social', social_auth_factory(oauth, 'yandex')
    )

