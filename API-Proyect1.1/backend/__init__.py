from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager  

db = SQLAlchemy()


def create_app(config_name=None):
    app = Flask(__name__)

    USER_DB = 'root'
    PASS_DB = ''
    URL_DB = 'localhost'
    NAME_DB = 'cmc'
    FULL_URL_DB = f'mysql+pymysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

    app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWT
    app.config['JWT_SECRET_KEY'] = 'Camilo1006'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    db.init_app(app)

    # Inicializar JWTManager después de configurar la clave secreta
    JWTManager(app)  # Inicializar JWTManager aquí
    print(f"__init__.py: JWT_SECRET_KEY = {app.config['JWT_SECRET_KEY']}")

    return app