from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    app.run(Config.HOST, Config.PORT, debug=Config.DEBUG)
