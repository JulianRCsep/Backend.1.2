from flask import request, jsonify
from ..modelos.modelos import rep_legal
from flask_restful import Resource
from ..modelos import db, RepLegalSchema
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from backend.vistas.auth import auth_blueprint

rep_legal_schema = RepLegalSchema()


@auth_blueprint.route('/registro', methods=['POST'])
def registro():
    """
    Registro de nuevo representante legal
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nombre:
              type: string
            nombreusuario:
              type: string
            direccion:
              type: string
            telefono:
              type: string
            contrasena:
              type: string
            rol_id:
              type: integer
    responses:
      201:
        description: Usuario registrado exitosamente
    """
    data = request.get_json()
    nuevo_usuario = rep_legal(
        rep_nombre=data['nombre'],
        rep_nombreusuario=data['nombreusuario'],
        rep_direccion=data['direccion'],
        rep_telefono=data['telefono'],
        contrasena_hash=generate_password_hash(data['contrasena']),
        rol_id_rol=data['rol_id']
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario registrado"}), 201


class VistaRepLegal(Resource):
    def get(self):
        """
        Obtener todos los representantes legales
        ---
        tags:
          - Usuarios
        responses:
          200:
            description: Lista de representantes legales
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  nombre:
                    type: string
                  usuario:
                    type: string
                  direccion:
                    type: string
                  telefono:
                    type: string
                  rol_id:
                    type: integer
        """
        usuarios = rep_legal.query.all()
        return jsonify([
            {
                'id': usuario.rep_id,
                'nombre': usuario.rep_nombre,
                'usuario': usuario.rep_nombreusuario,
                'direccion': usuario.rep_direccion,
                'telefono': usuario.rep_telefono,
                'rol_id': usuario.rol_id_rol
            }
            for usuario in usuarios
        ])

    def post(self):
        """
        Crear nuevo usuario o iniciar sesión
        ---
        tags:
          - Usuarios
        parameters:
          - in: body
            name: body
            schema:
              type: object
              properties:
                nombre_usuario:
                  type: string
                contrasena:
                  type: string
        responses:
          201:
            description: Usuario creado exitosamente
          200:
            description: Inicio de sesión exitoso
          401:
            description: Usuario o contraseña incorrectos
        """
        if 'nombre_usuario' in request.json:
            nuevo_rep_legal = rep_legal(
                rep_nombreusuario=request.json['nombre_usuario'],
                contrasena_hash=generate_password_hash(request.json['contrasena'])
            )
            db.session.add(nuevo_rep_legal)
            db.session.commit()
            access_token = create_access_token(identity=nuevo_rep_legal.rep_id)
            return {'mensaje': 'Usuario creado exitosamente', 'token_de_acceso': access_token}, 201
        else:
            rep_nombre_usuario = request.json["nombre_usuario"]
            rep_contrasena = request.json["contrasena"]
            usuario = rep_legal.query.filter_by(rep_nombreusuario=rep_nombre_usuario).first()
            if usuario and check_password_hash(usuario.contrasena_hash, rep_contrasena):
                access_token = create_access_token(identity=usuario.rep_id)
                return {'mensaje': 'Inicio de sesión exitoso', 'token_de_acceso': access_token}, 200
            else:
                return {'mensaje': 'Nombre de usuario o contraseña incorrectos'}, 401

    def put(self, id):
        """
        Actualizar un representante legal por ID
        ---
        tags:
          - Usuarios
        parameters:
          - name: id
            in: path
            type: integer
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                nombre:
                  type: string
                direccion:
                  type: string
                telefono:
                  type: string
        responses:
          200:
            description: Representante actualizado
          404:
            description: No encontrado
        """
        rep = rep_legal.query.get(id)
        if not rep:
            return {'mensaje': 'Representante legal no encontrado'}, 404

        # Aquí agregarías actualización de campos si deseas

        db.session.commit()
        return rep_legal_schema.dump(rep)

    def delete(self, id):
        """
        Eliminar representante legal por ID
        ---
        tags:
          - Usuarios
        parameters:
          - name: id
            in: path
            type: integer
            required: true
        responses:
          204:
            description: Eliminado exitosamente
          404:
            description: No encontrado
        """
        rep = rep_legal.query.get(id)
        if not rep:
            return {'mensaje': 'Representante legal no encontrado'}, 404

        db.session.delete(rep)
        db.session.commit()
        return {'mensaje': 'Representante legal eliminado exitosamente'}, 204
