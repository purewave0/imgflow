from flask import render_template
from flask_login import current_user

from app.user import bp
from app.dbapi import get_user_by_name


@bp.route('/<username>')
def show_user(username):
    user = get_user_by_name(username)
    if not user:
        return render_template('user/404.html')

    return render_template(
        'user/index.html',
        username=user.name,
        user_created_on=user.created_on,
        # TODO: avatar, score...
    )
