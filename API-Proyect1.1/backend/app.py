from flask import Flask, send_file
from flask_restful import Api
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger

from . import create_app
from .modelos import db, crear_superusuario
from .vistas.auth import auth_blueprint
from .vistas.vista_certificado import VistaCertificado, VistaCertificados
from .vistas.vista_rol import VistaRol
from .vistas.vistas_usuarios import UsuariosResource, UsuarioResource 
from docx2pdf import convert

import os

app = create_app()

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})

Swagger(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_blueprint)

api = Api(app)
api.add_resource(VistaCertificados, '/certificados')
api.add_resource(VistaCertificado, '/certificados/<int:id>')
api.add_resource(VistaRol, '/roles')
api.add_resource(UsuariosResource, '/usuarios')
api.add_resource(UsuarioResource, '/usuarios/<int:usuario_id>')

@app.route('/certificados/<int:id>/archivo', methods=['GET'])
def descargar_certificado(id):
    ruta_docx = f"certificados_generados/Certificado_{id}.docx"
    ruta_pdf = f"certificados_generados/Certificado_{id}.pdf"

    if not os.path.exists(ruta_docx):
        return {'message': 'Archivo .docx no encontrado'}, 404

    if not os.path.exists(ruta_pdf):
        try:
            convert(ruta_docx, ruta_pdf)
        except Exception as e:
            return {'message': 'Error al convertir a PDF', 'error': str(e)}, 500

    return send_file(ruta_pdf, as_attachment=True)

with app.app_context():
    db.create_all()
    crear_superusuario()

if __name__ == '__main__':
    app.run(debug=True)
