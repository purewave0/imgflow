from flask import render_template

from app.main import bp


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login')
def login():
    return render_template('login/index.html')

@bp.route('/signup')
def signup():
    return render_template('signup/index.html')
