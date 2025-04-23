from backend.modelos import db
from backend.vistas import vistas_usuarios, auth
from backend import create_app
from backend.vistas.auth import auth_blueprint
from flask_restful import Api
from flask_cors import CORS
from .vistas.vistas_usuarios import VistaRepLegal
from .vistas.vista_certificado import Vista_certificado
from .vistas.vista_rol import Vista_rol
from flask_migrate import Migrate
from flasgger import Swagger



app = create_app('default')
app_context = app.app_context()
app_context.push()

#swagger
swagger = Swagger(app)

db.init_app(app)
db.create_all()
migrate = Migrate(app, db)
CORS(app)

app.register_blueprint(auth_blueprint, url_prefix="/api")


from flask import Flask, request

api=Api(app)

api.add_resource(VistaRepLegal,'/usuarios')

api.add_resource(Vista_certificado,'/certificados')

api.add_resource(Vista_rol, '/roles')





