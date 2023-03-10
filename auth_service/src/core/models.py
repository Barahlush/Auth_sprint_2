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

    class Meta:
        database = db
