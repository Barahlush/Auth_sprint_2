import click
from flask import Blueprint
from loguru import logger

from src.core.security import hash_password
from src.db.datastore import datastore

cli_bp = Blueprint('create', __name__)


@cli_bp.cli.command('admin')
@click.argument('email')
@click.argument('password')
def admin(email, password):
    """ Create an admin """
    datastore.create_user(
        email=email,
        password_hash=hash_password(password, 'text'),
        fs_uniquifier=email,
        roles=['admin'],
    )
    logger.info('create admin with email {}', email)
