from flask import request, send_file
from flask_restful import Resource
from backend.modelos import db, Certificado, CertificadoSchema, OrdenServicio, TipoServicio, DetalleServicio, FichaTecnica, Usuario
from flasgger.utils import swag_from
from marshmallow import ValidationError
from docx import Document
import traceback
import os

certificado_schema = CertificadoSchema()
certificados_schema = CertificadoSchema(many=True)

class VistaCertificados(Resource):
    @swag_from({
        'tags': ['Certificados'],
        'responses': {
            200: {
                'description': 'Lista de certificados',
                'schema': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/Certificado'
                    }
                }
            }
        }
    })
    def get(self):
        certificados = Certificado.query.all()
        return certificados_schema.dump(certificados), 200

    @swag_from({
        'tags': ['Certificados'],
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    '$ref': '#/definitions/Certificado'
                }
            }
        ],
        'responses': {
            201: {'description': 'Certificado creado exitosamente'},
            400: {'description': 'Datos inválidos o usuario no existe'},
            500: {'description': 'Error interno al guardar'}
        }
    })
    def post(self):
        try:
            data = request.json
            usuario = Usuario.query.get(data.get('usuario_id'))
            if not usuario:
                return {"message": f"Usuario con id {data.get('usuario_id')} no existe"}, 400

            usuario_orden = Usuario.query.get(data['orden_servicio'].get('usuario_id'))
            if not usuario_orden:
                return {"message": f"Usuario en orden_servicio con id {data['orden_servicio'].get('usuario_id')} no existe"}, 400

            tipo_servicio = TipoServicio(**data['orden_servicio']['tipo_servicio'])
            db.session.add(tipo_servicio)
            db.session.flush()

            orden_servicio = OrdenServicio(
                fecha=data['orden_servicio']['fecha'],
                hora=data['orden_servicio']['hora'],
                precaucion=data['orden_servicio']['precaucion'],
                usuario_id=data['orden_servicio']['usuario_id'],
                tipo_servicio_id=tipo_servicio.id
            )
            db.session.add(orden_servicio)
            db.session.flush()

            detalle_servicio = DetalleServicio(
                precio=data['detalle_servicio']['precio'],
                nombre_operario=data['detalle_servicio']['nombre_operario'],
                cantidad_producto=data['detalle_servicio']['cantidad_producto'],
                fin_servicio=data['detalle_servicio']['fin_servicio'],
                orden_servicio_id=orden_servicio.id
            )
            db.session.add(detalle_servicio)

            certificado = Certificado(
                fecha=data['fecha'],
                estado=data['estado'],
                usuario_id=data['usuario_id'],
                orden_servicio_id=orden_servicio.id
            )
            db.session.add(certificado)
            db.session.flush()

            for ficha in data['fichas_tecnicas']:
                ficha_tecnica = FichaTecnica(
                    producto_aplicado=ficha['producto_aplicado'],
                    dosis=ficha['dosis'],
                    ingrediente_activo=ficha['ingrediente_activo'],
                    certificado_id=certificado.id
                )
                db.session.add(ficha_tecnica)

            db.session.commit()

            # Generación del archivo DOCX - RUTA CORREGIDA
            datos_docx = {
                'fecha': certificado.fecha.strftime('%Y-%m-%d'),
                'cliente': usuario.nombre,
                'representante': getattr(usuario.rep_legal, 'nombre', 'N/A') if hasattr(usuario, 'rep_legal') else 'N/A',
                'telefono': getattr(usuario, 'telefono', 'N/A'),
                'nit': getattr(usuario, 'nit', 'N/A'),
                'direccion': getattr(usuario, 'direccion', 'N/A'),
                'descripcion_servicio': data['orden_servicio']['tipo_servicio'].get('descripcion', 'N/A')
            }

            for i, ficha in enumerate(data['fichas_tecnicas'][:3], start=1):
                datos_docx[f'producto_{i}'] = ficha['producto_aplicado']
                datos_docx[f'ingrediente_{i}'] = ficha['ingrediente_activo']
                datos_docx[f'dosis_{i}'] = ficha['dosis']
                datos_docx[f'categoria_{i}'] = ficha.get('categoria_toxica', 'N/A')
                datos_docx[f'lugar_{i}'] = ficha.get('lugar_aplicado', 'N/A')
                datos_docx[f'presentacion_{i}'] = ficha.get('presentacion', 'N/A')

            # CORRECCIÓN: Ruta correcta para encontrar la plantilla
            # Debugging: Imprimir rutas para verificar
            current_file = os.path.abspath(__file__)
            print(f"Archivo actual: {current_file}")
            
            # Desde vista_certificado.py (backend/vistas/) hacia plantillas (backend/plantillas/)
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Esto lleva a 'backend/'
            print(f"BASE_DIR: {BASE_DIR}")
            
            plantilla_path = os.path.join(BASE_DIR, 'plantillas', 'plantilla_certificado.docx')
            print(f"Ruta de plantilla: {plantilla_path}")
            print(f"¿Existe la plantilla? {os.path.exists(plantilla_path)}")
            
            # Listar contenido del directorio plantillas para debugging
            plantillas_dir = os.path.join(BASE_DIR, 'plantillas')
            if os.path.exists(plantillas_dir):
                print(f"Contenido de plantillas: {os.listdir(plantillas_dir)}")
            else:
                print(f"El directorio plantillas no existe: {plantillas_dir}")
            
            # Verificar si el archivo existe antes de intentar abrirlo
            if not os.path.exists(plantilla_path):
                return {"message": f"Plantilla no encontrada en: {plantilla_path}. Directorio base: {BASE_DIR}"}, 500
            
            # Crear directorio de salida si no existe
            salida_path = f"certificados_generados/Certificado_{certificado.id}.docx"
            os.makedirs("certificados_generados", exist_ok=True)

            # Generar el documento
            doc = Document(plantilla_path)
            for p in doc.paragraphs:
                for key, val in datos_docx.items():
                    if f"{{{{{key}}}}}" in p.text:
                        for run in p.runs:
                            run.text = run.text.replace(f"{{{{{key}}}}}", str(val))
            doc.save(salida_path)

            return certificado_schema.dump(certificado), 201

        except ValidationError as err:
            return {"message": "Datos inválidos", "errors": err.messages}, 400
        except Exception as e:
            print("Error al guardar:", traceback.format_exc())
            db.session.rollback()
            return {"message": "Error al guardar en base de datos", "error": str(e)}, 500

class VistaCertificado(Resource):
    @swag_from({
        'tags': ['Certificados'],
        'parameters': [
            {
                'name': 'id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID del certificado'
            }
        ],
        'responses': {
            200: {'description': 'x'},
            404: {'description': 'Certificado no encontrado'}
        }
    })
    def get(self, id):
        cert = Certificado.query.get(id)
        if cert:
            return certificado_schema.dump(cert), 200
        return {'message': 'Certificado no encontrado'}, 404

    @swag_from({
        'tags': ['Certificados'],
        'parameters': [
            {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
        ],
        'responses': {
            204: {'description': 'Certificado eliminado exitosamente'},
            404: {'description': 'Certificado no encontrado'}
        }
    })
    def delete(self, id):
        cert = Certificado.query.get(id)
        if cert:
            # Eliminar manualmente fichas técnicas relacionadas
            FichaTecnica.query.filter_by(certificado_id=cert.id).delete()
            db.session.delete(cert)
            db.session.commit()
            return {'message': 'Certificado eliminado'}, 204
        return {'message': 'Certificado no encontrado'}, 404

    @swag_from({
        'tags': ['Certificados'],
        'parameters': [
            {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'estado': {'type': 'string'},
                        'fecha': {'type': 'string'},
                        'usuario_id': {'type': 'integer'}
                    }
                }
            }
        ],
        'responses': {
            200: {'description': 'Certificado actualizado correctamente'},
            400: {'description': 'Datos inválidos'},
            404: {'description': 'Certificado no encontrado'}
        }
    })
    def put(self, id):
        certificado = Certificado.query.get(id)
        if not certificado:
            return {'message': 'Certificado no encontrado'}, 404

        data = request.get_json()
        try:
            if 'estado' in data:
                certificado.estado = data['estado']
            if 'fecha' in data:
                certificado.fecha = data['fecha']
            if 'usuario_id' in data:
                nuevo_usuario = Usuario.query.get(data['usuario_id'])
                if not nuevo_usuario:
                    return {'message': f'Usuario con id {data["usuario_id"]} no existe'}, 400
                certificado.usuario_id = data['usuario_id']

            db.session.commit()
            return {'message': 'Certificado actualizado correctamente'}, 200

        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al actualizar certificado', 'error': str(e)}, 500

class VistaDescargaCertificado(Resource):
    @swag_from({
        'tags': ['Certificados'],
        'parameters': [
            {
                'name': 'id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID del certificado a descargar'
            }
        ],
        'responses': {
            200: {'description': 'Archivo DOCX generado del certificado'},
            404: {'description': 'Archivo no encontrado'}
        }
    })
    def get(self, id):
        ruta = f"certificados_generados/Certificado_{id}.docx"
        if os.path.exists(ruta):
            return send_file(ruta, as_attachment=True)
        return {'message': 'Archivo no encontrado'}, 404