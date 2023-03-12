from gevent import monkey  # type: ignore
from src.db.postgres import patch_psycopg2

monkey.patch_all()
patch_psycopg2()   # type: ignore

from contextlib import closing

import flask_admin as admin  # type: ignore
import psycopg2
from authlib.integrations.flask_client import OAuth
from flasgger import Swagger
from flask import Flask
from flask_admin.menu import MenuLink  # type: ignore
from flask_limiter import Limiter   # type: ignore
from flask_limiter.util import get_remote_address   # type: ignore
from flask_wtf.csrf import CSRFProtect  # type: ignore
from loguru import logger
from psycopg2.errors import DuplicateDatabase
from src.api.v1.api import auth_api
from src.cli.commands import cli_bp
from src.core.admin import (
    RoleAdmin,
    RoleInfo,
    SocialAccountAdmin,
    SocialAccountInfo,
    UserAdmin,
    UserInfo,
    UserRolesAdmin,
    UserRolesInfo,
)
from src.core.config import POSTGRES_CONFIG, REDIS_CONFIG, settings
from src.core.jaeger import tracer_init
from src.core.jwt import jwt
from src.core.models import LoginEvent, Role, SocialAccount, User, UserRoles
from src.core.routers import not_auth
from src.core.security import hash_password
from src.core.views import auth_views
from src.db.datastore import datastore
from src.db.postgres import db
from src.social_services.oauth_services import create_oauth_services

# Create app
app = Flask(__name__)
app.config |= settings.APP_CONFIG
csrf = CSRFProtect(app)
oauth = OAuth(app)
oauth.init_app(app)
create_oauth_services(oauth)


admin = admin.Admin(
    app, name='Admin Panel', url='/auth/admin', template_mode='bootstrap3'
)
admin.add_link(MenuLink(name='Back to auth', url='/auth/profile'))

if __name__ == '__main__':

    # Create the database if it doesn't exist
    conn = psycopg2.connect(
        database='postgres',
        user=POSTGRES_CONFIG.user,
        password=POSTGRES_CONFIG.password,
        host=POSTGRES_CONFIG.host,
        port=POSTGRES_CONFIG.port,
    )
    conn.autocommit = True
    with closing(conn.cursor()) as cursor:
        try:
            cursor.execute('CREATE DATABASE users_database')
        except DuplicateDatabase:
            pass

    # Setup app and db
    with app.app_context():
        swagger = Swagger(app, template_file='schema/swagger.json')
        db.init(**dict(POSTGRES_CONFIG))
        logger.info('Connected to database {}', POSTGRES_CONFIG.database)
        app.register_blueprint(auth_api)
        app.register_blueprint(auth_views)
        app.register_blueprint(not_auth)
        app.register_blueprint(cli_bp)
        jwt.init_app(app)
        limiter = Limiter(
            get_remote_address,
            app=app,
            default_limits=[settings.DAYS_LIMIT, settings.HOURS_LIMIT],
            storage_uri=f'redis://{REDIS_CONFIG.host}:{REDIS_CONFIG.port}',
        )

        db.create_tables(
            [
                User,
                Role,
                UserRoles,
                UserRolesInfo,
                UserInfo,
                RoleInfo,
                LoginEvent,
                SocialAccount,
                SocialAccountInfo,
            ],
            safe=True,
        )
        # Create roles
        datastore.find_or_create_role(
            name='admin',
            permissions={
                'admin-read',
                'admin-write',
                'user-read',
                'user-write',
            },
        )
        datastore.find_or_create_role(
            name='monitor', permissions={'admin-read', 'user-read'}
        )
        datastore.find_or_create_role(
            name='user', permissions={'user-read', 'user-write'}
        )
        datastore.find_or_create_role(name='reader', permissions={'user-read'})
        admin_view = UserAdmin(User, endpoint='users')
        admin.add_view(admin_view)
        admin.add_view(RoleAdmin(Role, endpoint='roles'))
        admin.add_view(UserRolesAdmin(UserRoles, endpoint='user_roles'))
        admin.add_view(
            SocialAccountAdmin(SocialAccount, endpoint='social_account')
        )
        csrf.exempt(admin_view.blueprint)
        if settings.ENABLE_TRACER:
            tracer_init(app)

    app.run(host=settings.APP_HOST, port=settings.APP_PORT)
