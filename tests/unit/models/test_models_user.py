from werkzeug.security import check_password_hash

from app.models.user import User
from app.extensions import db


def test_model(app):
    with app.app_context():
        user = User('testuser1', 'password1')
        db.session.add(user)
        db.session.commit()

        stored_user: User | None = db.session.execute(
            db.select(
                User
            ).where(
                User.id == user.id
            )
        ).scalar_one_or_none()

        assert stored_user
        assert stored_user == user
        # should be hashed
        assert stored_user.password_hash != 'password1'


def test_check_password_correct(app, user: User):
    with app.app_context():
        assert user.check_password('password1')

def test_check_password_incorrect(app, user: User):
    with app.app_context():
        assert not user.check_password('password2')


def test_set_password_persistence(app, user: User):
    with app.app_context():
        user.set_password('newpassword')
        assert check_password_hash(user.password_hash, 'newpassword')
        # old password should not work
        assert not check_password_hash(user.password_hash, 'password1')
