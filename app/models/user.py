import random
import string

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.util import utcnow


class User(db.Model):
    __tablename__ = 'User'
    MIN_USERNAME_LENGTH = 2
    MAX_USERNAME_LENGTH = 32
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 100
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(MAX_USERNAME_LENGTH), nullable=False, unique=True, index=True
    )
    password_hash = db.Column(db.String(256))
    created_on = db.Column(db.DateTime, server_default=utcnow())
    # TODO: profile picture (avatar)
    # avatar_url = db.Column(db.String(128), nullable=True)
    # TODO: score
    # score = db.Column(db.Integer, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(
            password
        )

    def __repr__(self):
        return f'<User "{self.username}">'
