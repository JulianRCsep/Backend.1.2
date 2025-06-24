from flask import request
from flask_restful import Resource
from backend.modelos import db, Rol, RolSchema
from flasgger.utils import swag_from

rol_schema = RolSchema()
roles_schema = RolSchema(many=True)

class VistaRol(Resource):
    def get(self):
        """
        Obtener todos los roles
        ---
        tags:
          - Roles
        responses:
          200:
            description: Lista de roles
            schema:
              type: array
              items:
                type: object
                properties:
                  id_rol:
                    type: integer
                    example: 1
                  nombre_rol:
                    type: string
                    example: Administrador
        """
        roles = Rol.query.all()
        return roles_schema.dump(roles), 200

    def put(self, id):
        """
        Actualizar el nombre de un rol por ID
        ---
        tags:
          - Roles
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID del rol a actualizar
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                nombre_rol:
                  type: string
                  example: Nuevo nombre de rol
        responses:
          200:
            description: Rol actualizado exitosamente
          404:
            description: Rol no encontrado
        """
        rol_existente = Rol.query.get(id)
        if not rol_existente:
            return {'message': 'Rol no encontrado'}, 404

        data = request.get_json()
        rol_existente.nombre_rol = data.get('nombre_rol', rol_existente.nombre_rol)
        db.session.commit()
        return rol_schema.dump(rol_existente), 200
