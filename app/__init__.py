from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from flask.ext.babel import Babel

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
babel = Babel(app)

from app import controller
from app.helpers.util import Util
from app.models import User, UserRegisterForm
from mod_consultas import controller
from mod_operaciones import controller
from mod_reportes import controller

db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app, password_validator=Util.user_password_validator, register_form=UserRegisterForm)


@babel.localeselector
def get_locale():
    return 'es'
