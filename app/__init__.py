from flask import Flask

from db import db


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 初始化数据库
    db.init_app(app)  # 初始化应用
    with app.app_context():
        db.create_all()

    # 注册蓝图
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
