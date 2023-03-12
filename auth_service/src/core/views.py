from collections.abc import Callable
from typing import Any

from flask import Blueprint, request
from flask_jwt_extended import get_current_user, verify_jwt_in_request
from flask_wtf.csrf import generate_csrf  # type: ignore
from loguru import logger

from src.core.controllers import controllers
from src.core.jwt import roles_required
from src.utils.template_utils import navbar_items

auth_views = Blueprint('auth_views', __name__, url_prefix='/auth')


def add_route(
    blueprint: Blueprint,
    rule: str,
    methods: list[str],
    endpoint: str,
    *controller_components: Callable[..., Callable[..., Any]],
) -> None:
    route_processor = controller_components[-1]
    for decorator in controller_components[-2::-1]:
        route_processor = decorator(route_processor)
    route_processor.required_methods = methods   # type: ignore

    logger.info(f'Add route: {rule}')
    blueprint.add_url_rule(
        rule,
        endpoint=endpoint,
        view_func=route_processor,
    )


# Add GET routes to auth_views blueprint
add_route(
    auth_views,
    '/',
    ['GET'],
    'index',
    roles_required('user', 'admin'),
    controllers['index'],
)
add_route(
    auth_views,
    '/profile',
    ['GET'],
    'profile',
    roles_required('user', 'admin'),
    controllers['profile'],
)
add_route(
    auth_views,
    '/history',
    ['GET'],
    'history',
    roles_required('user', 'admin'),
    controllers['history'],
)
add_route(
    auth_views,
    '/change_login',
    ['GET'],
    'change_login',
    roles_required('user', 'admin'),
    controllers['change_login'],
)
add_route(
    auth_views,
    '/change_password',
    ['GET'],
    'change_password',
    roles_required('user', 'admin'),
    controllers['change_password'],
)
add_route(auth_views, '/login', ['GET'], 'login', controllers['login'])
add_route(
    auth_views, '/register', ['GET'], 'register', controllers['register']
)


@auth_views.context_processor
def inject_navbar() -> dict[str, list[str]]:
    verify_jwt_in_request(optional=True)
    current_user = get_current_user()
    csrf_token = generate_csrf()

    navbar = []
    if not current_user:
        logger.info('ANONIM')
        for item in navbar_items:
            item.init()
            if 'anon' in item.roles:
                is_active = item.href == request.path
                navbar.append(item.to_html(csrf_token, is_active))
        return {'navbar_items': navbar}
    logger.info('AUTHORIZED')
    for item in navbar_items:
        item.init()
        for role in current_user.roles:
            if role.name in item.roles:
                is_active = item.href == request.path
                navbar.append(item.to_html(csrf_token, is_active))
    return {'navbar_items': navbar}
