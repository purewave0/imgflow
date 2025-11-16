import random
import string

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.extensions import db
from app.models.util import utcnow


class User(UserMixin, db.Model):
    """A registered user."""
    __tablename__ = 'User'
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 32
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 100
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(MAX_NAME_LENGTH), nullable=False, unique=True, index=True
    )
    """The name of the user, used in URLs."""
    password_hash = db.Column(db.String(256))
    """The hashed password."""
    created_on = db.Column(db.DateTime, server_default=utcnow())
    """When the user was created."""
    score = db.Column(db.Integer, nullable=False, default=0)
    """How many times this user's post and comments were upvoted."""
    # TODO: profile picture (avatar)
    # avatar_url = db.Column(db.String(128), nullable=True)

    def __init__(
        self,
        name: str,
        password: str
    ):
        self.name = name
        self.password_hash = generate_password_hash(
            password
        )
        self.score = 0

    def __repr__(self):
        return f'<User "{self.name}">'

    def set_password(self, password: str):
        """Set the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return True if the given password matches the stored one."""
        return check_password_hash(self.password_hash, password)
