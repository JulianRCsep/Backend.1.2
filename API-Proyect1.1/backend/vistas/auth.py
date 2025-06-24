from flask import request, jsonify, Blueprint, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..modelos import db, Usuario, Rol

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    try:
        rol_nombre = data['rol']
        rol = Rol.query.filter_by(nombre=rol_nombre).first()
        if not rol:
            return {"mensaje": f"No existe el rol {rol_nombre}"}, 400

        nuevo = Usuario(
            nombre=data['nombre'],
            direccion=data['direccion'],
            telefono=data['telefono'],
            contrasena_hash=generate_password_hash(data['contrasena']),
            rol_id=rol.id
        )
        db.session.add(nuevo)
        db.session.commit()

        return {"mensaje": "Usuario registrado exitosamente"}, 201
    except KeyError as e:
        return {"mensaje": f"Falta el campo: {e}"}, 400
    except Exception as e:
        db.session.rollback()
        return {"mensaje": "Error al registrar", "error": str(e)}, 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'nombre' not in data or 'contrasena' not in data:
        return {"mensaje": "Faltan nombre o contraseña"}, 400

    usuario = Usuario.query.filter_by(nombre=data['nombre']).first()

    if usuario and check_password_hash(usuario.contrasena_hash, data['contrasena']):
        rol_nombre = usuario.get_rol_nombre()
        token = create_access_token(identity=str(usuario.id),
                                    additional_claims={'rol': rol_nombre})
        return jsonify({
            'mensaje': 'Inicio de sesión exitoso',
            'token': token,
            'rol': rol_nombre,
            'nombre': usuario.nombre,
            'usuario_id': str(usuario.id)
        }), 200
    else:
        return {"mensaje": "Nombre o contraseña incorrectos"}, 401
