from app import db
from flask_user import UserMixin
from flask_user.forms import RegisterForm
from wtforms import StringField, validators


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    program = db.Column(db.String)
    tx = db.Column(db.Text)
    rx = db.Column(db.Text)
    ip = db.Column(db.String)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    is_enabled = db.Column(db.Boolean(), nullable=False, server_default='1')
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

    roles = db.relationship('Role', secondary='user_roles')


class UserRegisterForm(RegisterForm):
    first_name = StringField('Nombre', [validators.required()])
    last_name = StringField('Apellido', [validators.required()])


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# db.create_all()
