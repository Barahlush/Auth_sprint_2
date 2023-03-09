import random
import string
from datetime import datetime
from typing import Any

from loguru import logger
from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    TextField,
)

from src.db.postgres import db


class Role(Model):
    __tablename__ = 'role'

    name = CharField(unique=True)

    class Meta:
        database = db


class User(Model):
    __tablename__ = 'user'

    email = TextField(unique=True, null=False)
    password_hash = TextField(null=False)
    fs_uniquifier = TextField(null=False)
    active = BooleanField(default=True)

    class Meta:
        database = db


class UserRoles(Model):
    __tablename__ = 'user_roles'

    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)

    def get_permissions(self) -> Any:
        return self.role.get_permissions()

    class Meta:
        database = db


class LoginEvent(Model):
    __tablename__ = 'login_event'
    history = TextField()
    registered = DateTimeField(default=datetime.now)
    user = ForeignKeyField(User, null=True)

    class Meta:
        database = db


class SocialAccount(Model):
    __tablename__ = 'social_account'

    user_is_active = BooleanField(default=True)
    user = ForeignKeyField(User, related_name='social_account')

    social_id = TextField(null=False)
    social_name = TextField(null=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}>'

    @classmethod
    def create_social_connect(
        cls,
        social_id: str,
        social_name: str,
        user_id: str = None,
        user_fields: dict[str, str] = {},
    ) -> Model | None:
        """
        Создаёт связку пользователь - соц сеть.
        Если пользователя нет - создаёт и добавляет связку.
        :param user_id:
        :param social_id:
        :param social_name:
        :param user_fields:
        :return:
        """
        logger.info('user_fields {}', user_fields)
        if not user_id:
            user_id = cls.create_user_from_social_account(**user_fields)
        if cls.is_social_exist(social_id):
            return None

        social_account = SocialAccount(
            user_id=user_id, social_id=social_id, social_name=social_name
        )
        return social_account

    @classmethod
    def create_user_from_social_account(
        cls,
        email: str | None = '*@*',
        **kwargs,
    ) -> str:
        """
        Создание нового пользователя
        :param email:
        :return:
        """
        user = User(email=email)
        if user.get_id():
            logger.info('find user {}', user)
        else:
            fs_uniquifier = cls.random_generator()
            password = cls.random_generator()
            user = User.create(
                password_hash=password,
                email=email,
                fs_uniquifier=fs_uniquifier,
            )
            user.save()
            logger.info('create user {}', user)
        return user.get_id()

    @classmethod
    def is_social_exist(cls, social_id: str) -> bool:
        """
        Проверка на существование пользователя по логину

        :param social_id:
        :return:
        """
        social_account = SocialAccount.select().where(
            SocialAccount.social_id == social_id
        )
        return bool(social_account)

    @staticmethod
    def random_generator(
        size: int = 2,
        chars: str = string.ascii_uppercase + string.digits,
    ) -> str:
        str_time = str(datetime.now().timestamp())
        return str_time.join(random.choice(chars) for _ in range(size))

    class Meta:
        database = db
