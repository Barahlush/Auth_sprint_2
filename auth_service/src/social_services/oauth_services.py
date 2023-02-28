from enum import Enum

from authlib.integrations.flask_client import OAuth
from src.social_services.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_OAUTH_SETTINGS,
    YANDEX_ACCESS_TOKEN_URL,
    YANDEX_API_BASE_URL,
    YANDEX_APP_ID,
    YANDEX_APP_SECRET,
    YANDEX_AUTHORIZE_URL,
)


class Services(Enum):
    GOOGLE = 'google'
    YANDEX = 'yandex'


def google_register(oauth: OAuth, GOOGLE_DISCOVERY_URL=None) -> None:
    """
    Регистрирует гугл как сервис в котором можно пройти oauth
    После регистрации oauth получает атрибут с именем указанным в name

    :param oauth:
    :return:
    """
    oauth.register(
        name=Services.GOOGLE.value,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=GOOGLE_DISCOVERY_URL,
        client_kwargs=GOOGLE_OAUTH_SETTINGS,
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
        client_id=YANDEX_APP_ID,
        client_secret=YANDEX_APP_SECRET,
        api_base_url=YANDEX_API_BASE_URL,
        access_token_url=YANDEX_ACCESS_TOKEN_URL,
        authorize_url=YANDEX_AUTHORIZE_URL,
    )


def create_oauth_services(oauth: OAuth) -> None:
    google_register(oauth)
    yandex_register(oauth)
