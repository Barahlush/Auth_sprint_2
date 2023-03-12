from flask import Blueprint
from src.core.controllers import controllers
from src.core.jwt import roles_required
from src.core.views import add_route

auth_api = Blueprint('auth_api', __name__, url_prefix='/api/v1/auth')


# Add POST routes to auth_api blueprint
add_route(
    auth_api,
    '/logout',
    ['POST'],
    'logout',
    roles_required('user', 'admin'),
    controllers['logout'],
)
add_route(
    auth_api,
    '/logout_all',
    ['POST'],
    'logout_all',
    roles_required('user', 'admin'),
    controllers['logout_all'],
)
add_route(
    auth_api,
    '/refresh',
    ['POST'],
    'refresh',
    roles_required('user', 'admin'),
    controllers['refresh'],
)
add_route(auth_api, '/login', ['POST'], 'login', controllers['login'])
add_route(auth_api, '/register', ['POST'], 'register', controllers['register'])
