from flask_restful import Api

from src.social_services.routers import social
from src.social_services.social_auth import SocialLogin, Social

api_urls = [
    (SocialLogin, '/login/<string:name>'),
    (Social, '/login/<string:social_name>')
]

# подключение постоянных ручек
api = Api(social)
for resource, url in api_urls:
    api.add_resource(resource, url)
