# -*- coding: utf-8 -*-
"""
    NCP Rates  Test Job
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2022 by Roman Morozov.
    :license: MIT, see LICENSE for more details.
"""
import logging
import os
import time
from logging.config import dictConfig

from flask import Flask, has_request_context, request

from extensions import db


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)
logging_config = dict(
    version=1,
    formatters={
        'default': {'format': '%(asctime)s | %(funcName)s | %(levelname)s | %(module)s:%(lineno)d}: %(message)s'}
    },
    handlers={
        'h': {'class': 'logging.handlers.RotatingFileHandler',
              'filename': 'console.log',
              'maxBytes': 1024 * 1024 * 10,
              'backupCount': 25,
              'level': 'DEBUG',
              'encoding': 'utf8'},
        'l': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    root={
        'handlers': ['h', 'l'],
        'level': logging.DEBUG,
    },
    disable_existing_loggers=False
)


def create_app() -> Flask:
    """
    Creates app
    :return:
    """
    app = Flask(__name__)

    # TimeZone Configure
    os.environ['TZ'] = 'Europe/Minsk'
    time.tzset()

    dictConfig(logging_config)

    configure_app(app)
    configure_extensions(app)
    configure_blueprints(app)
    return app


def configure_app(app: Flask) -> None:
    """
    Set env static config's
    :param app:
    :return:
    """
    # App config's
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    # Database config's
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "database.sqlite3")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False


def configure_extensions(app: Flask) -> None:
    """
    Configures extensions
    :param app:
    :return:
    """

    # Flask-SqlAlchemy
    db.init_app(app)


def configure_blueprints(app: Flask) -> None:
    """
    Configure views
    :param app:
    :return:
    """

    from views import bp
    app.register_blueprint(bp)

