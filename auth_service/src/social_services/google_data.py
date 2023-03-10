from src.social_services.base import BaseDataParser, SocialUserModel


class GoogleDataParser(BaseDataParser):
    def get_user_info(self) -> SocialUserModel:
        userinfo_dict = self.client.parse_id_token(self.token)
        return SocialUserModel(
            open_id=userinfo_dict.get('sub'),
            email=userinfo_dict.get('email'),
            name=userinfo_dict.get('family_name'),
        )
