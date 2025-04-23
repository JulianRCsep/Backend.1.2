from backend.modelos import db
from backend.modelos.modelos import rep_legal
from backend import create_app

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)


usuario = rep_legal(
    rep_nombre="Juan",
    rep_nombreusuario="camiloroa1006@gmail.com",
    rep_direccion="Calle 123",
    rep_telefono=123456789,
    rol_id_rol=2
)
usuario.contrasena = "123456"  

db.session.add(usuario)
db.session.commit()

print("Usuario creado exitosamente")