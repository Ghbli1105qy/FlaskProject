# flask_app.py
from flask import Flask
from app.config import Config
from app.models import db
from app.routes import init_routes
from app.auth import init_auth
from datetime import datetime, timedelta
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # 初始化路由
    init_routes(app)

    # 初始化认证
    init_auth(app)
    app.jinja_env.globals.update(datetime=datetime, timedelta=timedelta)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)