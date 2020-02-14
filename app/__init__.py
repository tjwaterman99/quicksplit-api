from flask import Flask

from app.views import root

def create_app():
    app = Flask(__name__)
    app.register_blueprint(root)
    return app
