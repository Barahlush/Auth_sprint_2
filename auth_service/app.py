from gevent import monkey
from src.v1.db.postgres import patch_psycopg2

monkey.patch_all()
patch_psycopg2()

from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.v1.core.jaeger import tracer_init
from src.v1.core.models import User, Role, UserRoles, LoginEvent, SocialAccount

from src.v1.social_services.oauth_services import create_oauth_services
from src.v1.core.config import POSTGRES_CONFIG, settings, REDIS_CONFIG
from src.v1.core.jwt import jwt
from src.v1.core.views import views
from src.v1.core.security import hash_password

monkey.patch_all()
patch_psycopg2()

from authlib.integrations.flask_client import OAuth

from contextlib import closing

import flask_admin as admin  # type: ignore
import psycopg2
from flask import Flask
from flask_admin.menu import MenuLink  # type: ignore
from flask_wtf.csrf import CSRFProtect  # type: ignore
from loguru import logger
from psycopg2.errors import DuplicateDatabase
from src.v1.core.routers import not_auth
from src.v1.core.admin import (
    RoleAdmin,
    RoleInfo,
    UserRolesInfo,
    SocialAccountAdmin,
    SocialAccountInfo,
    UserAdmin,
    UserInfo,
    UserRolesAdmin,
)
from src.v1.db.datastore import datastore
from src.v1.db.postgres import db

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

import peeweedbevolve
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
        app.register_blueprint(views)
        app.register_blueprint(not_auth)
        jwt.init_app(app)
        limiter = Limiter(
            get_remote_address,
            app=app,
            default_limits=[settings.DAYS_LIMIT, settings.HOURS_LIMIT],
            storage_uri=f'redis://{REDIS_CONFIG.host}:{REDIS_CONFIG.port}'
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
        # Create a user to test with
        if admin_user := datastore.find_user(email='test@me.com'):
            datastore.delete_user(admin_user)
        datastore.create_user(
            user_id=1,
            email='test@me.com',
            password_hash=hash_password('password', 'text'),  # noqa
            fs_uniquifier='text',
            roles=['admin'],
        )
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
