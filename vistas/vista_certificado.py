from flask import request
from flask_restful import Resource
from backend.modelos import db, certificado, CertificadoSchema
from flasgger.utils import swag_from

certificado_Schema = CertificadoSchema()
certificados_Schema = CertificadoSchema(many=True)

class Vista_certificado(Resource):
    def get(self):
        """
        Obtener todos los certificados
        ---
        tags:
          - Certificados
        responses:
          200:
            description: Lista de certificados
            schema:
              type: array
              items:
                type: object
                properties:
                  id_certificado:
                    type: integer
                    example: 101
                  fecha_certificado:
                    type: string
                    example: "2025-04-20"
                  estado_certificado:
                    type: string
                    example: "Aprobado"
                  orden_servicio_id_orden_servicio:
                    type: integer
                    example: 202
        """
        certificados = certificado.query.all()
        return certificados_Schema.dump(certificados), 200

    def post(self):
        """
        Crear un nuevo certificado
        ---
        tags:
          - Certificados
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                id_certificado:
                  type: integer
                  example: 103
                fecha_certificado:
                  type: string
                  example: "2025-04-23"
                estado_certificado:
                  type: string
                  example: "Pendiente"
                orden_servicio_id_orden_servicio:
                  type: integer
                  example: 205
        responses:
          201:
            description: Certificado creado exitosamente
        """
        nuevo_certificado = certificado(
            id_certificado=request.json['id_certificado'],
            fecha_certificado=request.json['fecha_certificado'],
            estado_certificado=request.json['estado_certificado'],
            orden_servicio_id_orden_servicio=request.json['orden_servicio_id_orden_servicio']
        )
        db.session.add(nuevo_certificado)
        db.session.commit()
        return certificado_Schema.dump(nuevo_certificado), 201

    def delete(self, id):
        """
        Eliminar un certificado por ID
        ---
        tags:
          - Certificados
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID del certificado a eliminar
        responses:
          204:
            description: Certificado eliminado exitosamente
          404:
            description: Certificado no encontrado
        """
        cert = certificado.query.get(id)
        if cert:
            db.session.delete(cert)
            db.session.commit()
            return {'message': 'Certificado eliminado'}, 204
        return {'message': 'Certificado no encontrado'}, 404


