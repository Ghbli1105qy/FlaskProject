from flask import render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.models import User, db
import bcrypt

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_auth(app):
    login_manager.init_app(app)
    login_manager.login_view = 'login_page'

    @app.route('/login', methods=['GET', 'POST'], endpoint='login_page')
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard_page'))
            return render_template('login.html', error='用户名或密码错误')
        return render_template('login.html')

    @app.route('/logout', endpoint='logout_page')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login_page'))

    @app.route('/register', methods=['GET', 'POST'], endpoint='register_page')
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                return render_template('register.html', error='用户名已存在')
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login_page'))
        return render_template('register.html')