# backend/vistas/auth.py

from flask import Blueprint, request, jsonify
from backend.modelos import rep_legal, db
from werkzeug.security import check_password_hash

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('rep_nombreusuario')
    password = data.get('Contrasena_hash')

    user = rep_legal.query.filter_by(rep_nombreusuario=username).first()

    if user and user.verificar_contrasena(password):
        return jsonify({
            'message': 'Login exitoso',
            'rep_id': user.rep_id,
            'nombre': user.rep_nombre,
            'rol': user.rol_id_rol,
            'access_token': f"TOKEN-DE-EJEMPLO-{user.rep_id}"  # Aquí podrías usar JWT si quieres
        }), 200
    else:
        return jsonify({'message': 'Nombre de usuario o contraseña incorrectos'}), 401
