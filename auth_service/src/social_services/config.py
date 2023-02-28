import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_OAUTH_SETTINGS = {"scope": "openid email profile"}
GOOGLE_DISCOVERY_URL = os.getenv("GOOGLE_DISCOVERY_URL")

YANDEX_APP_ID = os.getenv("YANDEX_APP_ID")
YANDEX_APP_SECRET = os.getenv("YANDEX_APP_SECRET")
YANDEX_API_BASE_URL = "https://login.yandex.ru/"
YANDEX_ACCESS_TOKEN_URL = "https://oauth.yandex.com/token"
YANDEX_AUTHORIZE_URL = "https://oauth.yandex.com/authorize"
YANDEX_USERINFO_URL = "https://login.yandex.ru/info?format=json"

USE_NGINX = int(os.getenv("USE_NGINX", 0))
