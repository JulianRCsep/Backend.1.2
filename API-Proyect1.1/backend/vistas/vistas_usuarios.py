from flask import request, jsonify, current_app
from flask_restful import Resource, Api
from ..modelos import db, Usuario, UsuarioSchema, Rol
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from backend.vistas.auth import auth_blueprint
from functools import wraps
import logging

logging.basicConfig(level=logging.DEBUG)

vistas_usuarios_schema = UsuarioSchema()
ADMIN_ROLE = 'admin'  


def admin_required():
    """
    Decorador para restringir acceso a rutas solo a usuarios con rol de administrador.
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if not claims or claims.get('rol', '').lower() != ADMIN_ROLE:
                return {'mensaje': 'No tienes permisos de administrador para realizar esta acción.'}, 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@auth_blueprint.route('/registro', methods=['POST'])
@admin_required()
def registrar_usuario():
    """
    Registro de nuevo usuario (solo para administradores).
    Requiere un JSON con los campos: nombre, direccion, telefono, contrasena y rol_id.
    """
    data = request.get_json()
    try:
        rol_id = data['rol_id']
        rol = Rol.query.get(rol_id)
        if not rol:
            return {"mensaje": f"No existe el rol con ID {rol_id}"}, 400

        nuevo_usuario = Usuario(
            nombre=data['nombre'],
            direccion=data['direccion'],
            telefono=data['telefono'],
            rol_id=rol.id,
            contrasena_hash=generate_password_hash(data['contrasena'])
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return {
            "mensaje": "Usuario registrado exitosamente",
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "direccion": nuevo_usuario.direccion,
            "telefono": nuevo_usuario.telefono,
            "rol_id": nuevo_usuario.rol_id
        }, 201
    except KeyError as e:
        return {"mensaje": f"Falta el campo: {e}"}, 400
    except Exception as e:
        db.session.rollback()
        return {"mensaje": "Error al registrar el usuario", "error": str(e)}, 500


class UsuariosResource(Resource):

    @jwt_required()
    def get(self):
        """
        Obtener todos los usuarios (solo administradores).
        """
        claims = get_jwt()
        if claims.get('rol', '').lower() != ADMIN_ROLE:
            logging.debug("Acceso no autorizado: Rol no es administrador")
            return {'mensaje': 'No tienes permisos de administrador'}, 403
        try:
            usuarios = Usuario.query.all()
            resultado = [{
                'id': u.id,
                'nombre': u.nombre,
                'direccion': u.direccion,
                'telefono': u.telefono,
                'rol_id': u.rol_id
            } for u in usuarios]
            logging.debug(f"Resultado a devolver: {resultado}")
            return resultado, 200
        except Exception as e:
            logging.error(f"Error al obtener usuarios: {e}")
            return {'mensaje': 'Error al obtener la lista de usuarios'}, 500


class UsuarioResource(Resource):
    @jwt_required()
    def get(self, usuario_id):
        """
        Obtener usuario por ID (solo administradores).
        """
        claims = get_jwt()
        if claims.get('rol', '').lower() != ADMIN_ROLE:
            return {'mensaje': 'No tienes permisos de administrador'}, 403
        usuario = Usuario.query.get_or_404(usuario_id)
        return jsonify({
            'id': usuario.id,
            'nombre': usuario.nombre,
            'direccion': usuario.direccion,
            'telefono': usuario.telefono,
            'rol_id': usuario.rol_id
        })

    @admin_required()
    def put(self, usuario_id):
        """
        Editar un usuario existente (solo administradores).
        """
        data = request.get_json()
        usuario = Usuario.query.get_or_404(usuario_id)
        if 'nombre' in data:
            usuario.nombre = data['nombre']
        if 'direccion' in data:
            usuario.direccion = data['direccion']
        if 'telefono' in data:
            usuario.telefono = data['telefono']
        if 'rol_id' in data:
            usuario.rol_id = data['rol_id']
        db.session.commit()
        return jsonify({
            'id': usuario.id,
            'nombre': usuario.nombre,
            'direccion': usuario.direccion,
            'telefono': usuario.telefono,
            'rol_id': usuario.rol_id
        })

    @admin_required()
    def delete(self, usuario_id):
        """
        Eliminar un usuario existente por ID (solo administradores).
        """
        usuario = Usuario.query.get_or_404(usuario_id)
        db.session.delete(usuario)
        db.session.commit()
        return {"mensaje": f"Usuario con ID {usuario_id} eliminado exitosamente"}


# --------------------------
# Nuevas funcionalidades para el usuario autenticado
# --------------------------

@auth_blueprint.route('/perfil', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def obtener_perfil():
    if request.method == 'OPTIONS':
        return '', 200

    identidad = get_jwt_identity()
    usuario = Usuario.query.get_or_404(identidad)
    return jsonify({
        'id': usuario.id,
        'nombre': usuario.nombre,
        'direccion': usuario.direccion,
        'telefono': usuario.telefono,
        'rol_id': usuario.rol_id
    })



@auth_blueprint.route('/perfil', methods=['PUT', 'OPTIONS'])
@jwt_required(optional=True)
def actualizar_perfil():
    if request.method == 'OPTIONS':
        return '', 200

    identidad = get_jwt_identity()
    data = request.get_json()
    usuario = Usuario.query.get_or_404(identidad)

    if 'nombre' in data:
        usuario.nombre = data['nombre']
    if 'direccion' in data:
        usuario.direccion = data['direccion']
    if 'telefono' in data:
        usuario.telefono = data['telefono']

    db.session.commit()
    return jsonify({
        "mensaje": "Perfil actualizado exitosamente",
        "usuario": {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'direccion': usuario.direccion,
            'telefono': usuario.telefono,
            'rol_id': usuario.rol_id
        }
    })



@auth_blueprint.route('/cambiar-contrasena', methods=['PUT'])
@jwt_required()
def cambiar_contrasena():
    """
    Permite al usuario autenticado cambiar su contraseña.
    Se requiere el campo 'nueva_contrasena' en el JSON de entrada.
    """
    identidad = get_jwt_identity()
    data = request.get_json()
    nueva_contrasena = data.get('nueva_contrasena')

    if not nueva_contrasena:
        return {"mensaje": "La nueva contraseña es requerida"}, 400

    usuario = Usuario.query.get_or_404(identidad)
    usuario.contrasena_hash = generate_password_hash(nueva_contrasena)
    db.session.commit()
    return {"mensaje": "Contraseña actualizada exitosamente"}