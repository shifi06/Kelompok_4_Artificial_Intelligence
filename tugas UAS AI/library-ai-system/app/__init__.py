from flask import Flask
from config import Config
from app.routes.main import main_bp
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import dan register blueprint dari routes
   
    app.register_blueprint(main_bp)

    return app