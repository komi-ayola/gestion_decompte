from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  

    db.init_app(app)
    migrate.init_app(app, db)  

    from app.routes import bp
    from app.models import Responsable  

    app.register_blueprint(bp)

    def format_montant(value):
        if isinstance(value, (int, float)):
            return f"{int(value):,}".replace(",", " ")  
        return value

    app.jinja_env.filters['nombre_sans_decimale'] = format_montant  

    return app


