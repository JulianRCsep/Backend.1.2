from flask import request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from ..modelos.modelos import Usuario, Rol
from backend.vistas.auth import auth_blueprint
from flask import current_app 
from flask import jsonify


@auth_blueprint.route('/login', methods=['POST'])
def login():
    """
    Iniciar sesión de usuario.
    ---
    tags:
      - Autenticación
    ...
    """
    data = request.get_json()

    if not data or 'nombre' not in data or 'contrasena' not in data:
        return {"mensaje": "Faltan nombre o contraseña"}, 400

    nombre = data["nombre"]
    contrasena = data["contrasena"]

    usuario = Usuario.query.filter_by(nombre=nombre).first()

    if usuario and check_password_hash(usuario.contrasena_hash, contrasena):
        rol_nombre = usuario.get_rol_nombre()
        print(f"vista_login.py: JWT_SECRET_KEY = {current_app.config['JWT_SECRET_KEY']}")
        token = create_access_token(identity=str(usuario.id),
                                    additional_claims={'rol': rol_nombre})
        print("DEBUG usuario.id:", usuario.id)

        return jsonify({
        'mensaje': 'Inicio de sesión exitoso',
        'token': token,
        'rol': rol_nombre,
        'nombre': usuario.nombre,
        'usuario_id': str(usuario.id)
         }), 200
    else:
        return jsonify({'mensaje': 'Nombre o contraseña incorrectos'}), 401
