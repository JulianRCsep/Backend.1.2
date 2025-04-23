from flask import request
from flask_restful import Resource
from backend.modelos import db, rol, RolSchema
from flasgger.utils import swag_from

rol_Schema = RolSchema()
rols_Schema = RolSchema(many=True)

class Vista_rol(Resource):
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
        roles = rol.query.all()
        return rols_Schema.dump(roles), 200

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
        rol_existente = rol.query.get(id)
        if not rol_existente:
            return {'message': 'Rol no encontrado'}, 404

        data = request.get_json()
        rol_existente.nombre_rol = data.get('nombre_rol', rol_existente.nombre_rol)
        db.session.commit()
        return rol_Schema.dump(rol_existente), 200
