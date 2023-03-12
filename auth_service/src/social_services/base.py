from abc import ABC, abstractmethod

from authlib.integrations.flask_client import FlaskRemoteApp
from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from pydantic import BaseModel


class SocialUserModel(BaseModel):
    open_id: str = None
    email: str = None
    name: str = None


class BaseDataParser(ABC):
    def __init__(self, client: FlaskRemoteApp, token: OAuth2Token):
        self.client = client
        self.token = token

    @abstractmethod
    def get_user_info(self) -> SocialUserModel:
        pass
