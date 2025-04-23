from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


detalle_servicio_has_orden_servicio = db.Table(
    'detalle_servicio_has_orden_servicio',
    db.Column('id_detalle_servicio', db.Integer, db.ForeignKey('detalle_servicio.id_detalle_servicio'), primary_key=True),
    db.Column('id_orden_servicio', db.Integer, db.ForeignKey('orden_servicio.id_orden_servicio'), primary_key=True)
)

class rol(db.Model):
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(45))

class rep_legal(db.Model):
    rep_id = db.Column(db.Integer, primary_key=True)
    rep_nombre = db.Column(db.String(45))
    rep_nombreusuario = db.Column(db.String(45), unique=True, nullable=False)
    rep_direccion = db.Column(db.String(45))
    rep_telefono = db.Column(db.Integer)
    rep_contrasena = db.Column(db.String(255))
    rol_id_rol = db.Column(db.Integer, db.ForeignKey(rol.id_rol))

    @property
    def contrasena(self):
        raise AttributeError("La contraseña no es un atributo legible.")
    
    @contrasena.setter
    def contrasena(self, password):
        self.rep_contrasena = generate_password_hash(password)

    def verificar_contrasena(self, password):
        return check_password_hash(self.rep_contrasena, password)

class categoria(db.Model):
    id_categoria = db.Column(db.Integer, primary_key=True)
    cat_descripcion = db.Column(db.String(45))
    rep_legal_rep_id = db.Column(db.Integer, db.ForeignKey(rep_legal.rep_id))

class establecimiento(db.Model):
    id_establecimiento = db.Column(db.Integer, primary_key=True)
    correo_est = db.Column(db.String(45))
    direccion_est = db.Column(db.String(45))
    nombre_est = db.Column(db.String(45))
    rep_legal_rep_id = db.Column(db.Integer, db.ForeignKey(rep_legal.rep_id))

class orden_servicio(db.Model):
    id_orden_servicio = db.Column(db.Integer, primary_key=True)
    orden_serv_fecha = db.Column(db.Date)
    orden_serv_hora = db.Column(db.String(45))
    orden_serv_precaucion = db.Column(db.String(255))
    rep_legal_rep_id = db.Column(db.Integer, db.ForeignKey(rep_legal.rep_id))

class tipo_servicio(db.Model):
    id_tipo_servicio = db.Column(db.Integer, primary_key=True)
    tipo_serv_suministro_emergencia = db.Column(db.String(45))
    tipo_serv_control_roedores = db.Column(db.String(45))
    tipo_serv_lavado_tanques = db.Column(db.String(45))
    tipo_serv_capacitacionSST = db.Column(db.String(45))
    tipo_serv_descripcion = db.Column(db.String(45))
    orden_servicio_id_orden_servicio = db.Column(db.Integer, db.ForeignKey(orden_servicio.id_orden_servicio))

class detalle_servicio(db.Model):
    id_detalle_servicio = db.Column(db.Integer, primary_key=True)
    det_serv_precio = db.Column(db.Integer)
    det_serv_nombre_operario = db.Column(db.String(45))
    def_serv_cantidad_producto = db.Column(db.String(45))
    det_fin_servicio = db.Column(db.String(45))

class certificado(db.Model):
    id_certificado = db.Column(db.Integer, primary_key=True)
    fecha_certificado = db.Column(db.String(8))
    estado_certificado = db.Column(db.String(45))
    orden_servicio_id_orden_servicio = db.Column(db.Integer, db.ForeignKey(orden_servicio.id_orden_servicio))

class ficha_tecnica(db.Model):
    fct_producto_aplicado = db.Column(db.String(45), primary_key=True)
    fct_dosis = db.Column(db.String(45))
    fct_ingrediente_activo = db.Column(db.String(45))
    certificado_id_certificado = db.Column(db.Integer)
    detalle_servicio_id_detalle_servicio = db.Column(db.Integer, db.ForeignKey(detalle_servicio.id_detalle_servicio))

# Esquemas de Serialización
class RolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = rol
        include_relationships = False

class RepLegalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = rep_legal
        include_relationships = True

class CategoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = categoria
        include_relationships = True

class EstablecimientoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = establecimiento
        include_relationships = True

class OrdenServicioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = orden_servicio
        include_relationships = True

class TipoServicioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = tipo_servicio
        include_relationships = True

class DetalleServicioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = detalle_servicio
        include_relationships = True

class CertificadoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = certificado
        include_relationships = True

class FichaTecnicaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ficha_tecnica
        include_relationships = True

def crear_superusuario():
    # Verificar si ya existe el rol "superusuario"
    superuser_role = rol.query.filter_by(nombre_rol="superusuario").first()
    if not superuser_role:
        superuser_role = rol(nombre_rol="superusuario")
        db.session.add(superuser_role)
        db.session.commit()
    
    # veriuficacion
    if rep_legal.query.filter_by(rep_nombreusuario="admin").first():
        print("El admin ya existe.")
        return

    # superadmin
    superuser = rep_legal(
        rep_nombre="superAdministrador",
        rep_nombreusuario="superadmin",
        rep_direccion="sena complejo sur",
        rep_telefono=123456789,
        contrasena="cmc123456",  
        rol_id_rol=superuser_role.id_rol
    )

    db.session.add(superuser)
    db.session.commit()
    print("Superusuario creado exitosamente.")