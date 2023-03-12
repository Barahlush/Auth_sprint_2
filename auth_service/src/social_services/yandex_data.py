from src.core.config import settings
from src.social_services.base import BaseDataParser, SocialUserModel


class YandexDataParser(BaseDataParser):
    def get_user_info(self) -> SocialUserModel:
        userinfo = self.client.get(settings.YANDEX_USERINFO_URL)
        userinfo_dict = userinfo.json()
        return SocialUserModel(
            open_id=userinfo_dict.get('id'),
            email=userinfo_dict.get('default_email'),
            name=userinfo_dict.get('login'),
        )
