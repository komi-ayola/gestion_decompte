from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Charge la config

    db.init_app(app)
    migrate.init_app(app, db)  # Initialise Flask-Migrate après SQLAlchemy

    from app.routes import bp
    from app.models import Responsable  # Assure-toi que Responsable est bien importé

    app.register_blueprint(bp)

    def format_montant(value):
        if isinstance(value, (int, float)):
            return f"{int(value):,}".replace(",", " ")  # Remplace les virgules par des espaces
        return value

    app.jinja_env.filters['nombre_sans_decimale'] = format_montant  # Enregistrer le filtre dans Jinja

    return app


