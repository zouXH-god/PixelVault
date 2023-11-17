from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 注册蓝图
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
