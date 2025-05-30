import random
import string

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.extensions import db
from app.models.util import utcnow


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 32
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 100
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(MAX_NAME_LENGTH), nullable=False, unique=True, index=True
    )
    password_hash = db.Column(db.String(256))
    created_on = db.Column(db.DateTime, server_default=utcnow())
    # TODO: profile picture (avatar)
    # avatar_url = db.Column(db.String(128), nullable=True)
    # TODO: score
    # score = db.Column(db.Integer, nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password_hash = generate_password_hash(
            password
        )

    def __repr__(self):
        return f'<User "{self.name}">'


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
