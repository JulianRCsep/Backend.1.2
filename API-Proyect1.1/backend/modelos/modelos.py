from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields

db = SQLAlchemy()

detalle_servicio_has_orden_servicio = db.Table(
    'detalle_servicio_has_orden_servicio',
    db.Column('detalle_servicio_id', db.Integer, db.ForeignKey('detalle_servicio.id'), primary_key=True),
    db.Column('orden_servicio_id', db.Integer, db.ForeignKey('orden_servicio.id'), primary_key=True)
)

class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45))
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __repr__(self):
        return f'<Rol {self.nombre}>'

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(45))
    direccion = db.Column(db.String(45))
    telefono = db.Column(db.String(15))
    contrasena_hash = db.Column(db.String(255))
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))
    categorias = db.relationship('Categoria', backref='usuario', lazy=True)
    ordenes_servicio = db.relationship('OrdenServicio', backref='usuario', lazy=True)

    @property
    def contrasena(self):
        raise AttributeError("La contraseña no es un atributo legible.")

    @contrasena.setter
    def contrasena(self, password):
        self.contrasena_hash = generate_password_hash(password)

    def verificar_contrasena(self, password):
        return check_password_hash(self.contrasena_hash, password)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'
    
    def get_rol_nombre(self):
        return self.rol.nombre

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(45))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    def __repr__(self):
        return f'<Categoria {self.descripcion}>'

class OrdenServicio(db.Model):
    __tablename__ = 'orden_servicio'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date)
    hora = db.Column(db.String(45))
    precaucion = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    tipo_servicio_id = db.Column(db.Integer, db.ForeignKey('tipo_servicio.id'), nullable=False)  

    tipo_servicio = db.relationship('TipoServicio', backref='ordenes_servicio', lazy=True, foreign_keys=[tipo_servicio_id])  # nombre singular, más claro

    certificados = db.relationship('Certificado', backref='orden_servicio', lazy=True)

    def __repr__(self):
        return f'<OrdenServicio {self.id}>'

class TipoServicio(db.Model):
    __tablename__ = 'tipo_servicio'
    id = db.Column(db.Integer, primary_key=True)
    suministro_emergencia = db.Column(db.String(45))
    control_roedores = db.Column(db.String(45))
    lavado_tanques = db.Column(db.String(45))
    capacitacion_sst = db.Column(db.String(45))
    descripcion = db.Column(db.String(45))
    orden_servicio_id = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'))

    def __repr__(self):
        return f'<TipoServicio {self.descripcion}>'

class DetalleServicio(db.Model):
    __tablename__ = 'detalle_servicio'
    id = db.Column(db.Integer, primary_key=True)
    precio = db.Column(db.Integer)
    nombre_operario = db.Column(db.String(100))
    cantidad_producto = db.Column(db.String(100))
    fin_servicio = db.Column(db.String(50))

    orden_servicio_id = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=False)
    orden_servicio = db.relationship('OrdenServicio', backref='detalles_servicio', lazy=True)
    fichas_tecnicas = db.relationship('FichaTecnica', backref='detalle_servicio', lazy=True)


    def __repr__(self):
        return f'<DetalleServicio Operario={self.nombre_operario}>'

class Certificado(db.Model):
    __tablename__ = 'certificado'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date)
    estado = db.Column(db.String(45))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    orden_servicio_id = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=False)

    fichas_tecnicas = db.relationship('FichaTecnica', backref='certificado', lazy=True)
    usuario = db.relationship('Usuario', backref='certificados', lazy=True)

    def __repr__(self):
        return f'<Certificado {self.id}>'


class FichaTecnica(db.Model):
    __tablename__ = 'ficha_tecnica'
    id = db.Column(db.Integer, primary_key=True)  # clave primaria real
    producto_aplicado = db.Column(db.String(45), nullable=False)
    dosis = db.Column(db.String(45))
    ingrediente_activo = db.Column(db.String(45))

    certificado_id = db.Column(db.Integer, db.ForeignKey('certificado.id'), nullable=False)
    detalle_servicio_id = db.Column(db.Integer, db.ForeignKey('detalle_servicio.id'))

    def __repr__(self):
        return f'<FichaTecnica {self.id}: {self.producto_aplicado}>'

# ----------------- Esquemas de serialización -----------------

class CategoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Categoria
        include_fk = True
        load_instance = True

class DetalleServicioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DetalleServicio
        include_fk = True
        load_instance = True

class FichaTecnicaSchema(SQLAlchemyAutoSchema):
    detalle_servicio = fields.Nested(DetalleServicioSchema)

    class Meta:
        model = FichaTecnica
        include_fk = True
        load_instance = True

class TipoServicioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TipoServicio
        include_fk = True
        load_instance = True

class UsuarioSchema(SQLAlchemyAutoSchema):
    categorias = fields.Nested(CategoriaSchema, many=True)

    class Meta:
        model = Usuario
        include_fk = True
        load_instance = True

class OrdenServicioSchema(SQLAlchemyAutoSchema):
    tipos_servicio = fields.Nested(TipoServicioSchema, many=True)
    usuario = fields.Nested(UsuarioSchema)

    class Meta:
        model = OrdenServicio
        include_fk = True
        load_instance = True

class CertificadoSchema(SQLAlchemyAutoSchema):
    orden_servicio = fields.Nested(OrdenServicioSchema)
    fichas_tecnicas = fields.Nested(FichaTecnicaSchema, many=True)

    class Meta:
        model = Certificado
        include_fk = True
        load_instance = True

class RolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Rol
        include_fk = True
        load_instance = True

# ----------------- Crear superusuario -----------------

def crear_superusuario():
    superuser_role = Rol.query.filter_by(nombre="Admin").first()
    if not superuser_role:
        superuser_role = Rol(nombre="Admin")
        db.session.add(superuser_role)
        db.session.commit()
        print("Rol Admin creado")

    if not Usuario.query.filter_by(nombre="superAdministrador").first():
        superuser = Usuario(
            nombre="superAdministrador",
            direccion="sena complejo sur",
            telefono="123456789",
            contrasena="cmc123456",
            rol_id=superuser_role.id
        )
        db.session.add(superuser)
        db.session.commit()
        print("SuperUsuario creado")
    else:
        print("SuperUsuario ya existe")

