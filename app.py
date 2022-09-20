from flask import Flask, render_template, request, session
from flask_cors import CORS

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY="abcd1234"
)
CORS(app)

from auth import auth
app.register_blueprint(auth.auth)
from logistica import logistica
app.register_blueprint(logistica.lg)
from logistica import mapa
app.register_blueprint(mapa.lgMapa)
from logistica import historial
app.register_blueprint(historial.lgHS)
from logistica import asignacionRetiros
app.register_blueprint(asignacionRetiros.lgAR)
from logistica import asignacionZonas
app.register_blueprint(asignacionZonas.lgAZ)
from logistica import hojaRuta
app.register_blueprint(hojaRuta.hojaRuta)
from usuarios import usuarios
app.register_blueprint(usuarios.us)
from envios_cliente import envios_cliente
app.register_blueprint(envios_cliente.envcl)
from estadistica import estadistica
app.register_blueprint(estadistica.est)

@app.route("/")
@auth.login_required
def bienvenido():
    return render_template("index.html", titulo="Bienvenido", auth = session.get("user_auth"), usuario = session.get("user_id"))

from database import database
@app.route("/api/users/create",methods=["POST"])
def test():
    data = request.get_json()
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"insert into empleado (nombre,puesto,vehiculo,patente,correo,dni,cbu,telefono,direccion,localidad,password) values('{data['nombre']}','{data['puesto']}','{data['vehiculo']}','{data['patente']}','{data['correo']}','{data['dni']}','{data['cbu']}','{data['telefono']}','{data['direccion']}','{data['localidad']}','{data['password']}')")
    midb.commit()
    midb.close()
    return "algo"


@app.route("/api/users/login",methods=["POST"])
def loginAppMovil():
    dataLogin = request.get_json()
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select id,nombre,password from empleado where dni = {dataLogin['dni']}")
    res = cursor.fetchone()
    if res is None:
        return "Usuario y/o contraseña incorrectos"
    midb.close()
    if dataLogin["password"] == res[2]:
        print("True")
        return "{success:True,message:'usuario validado',data:""'}"
    else:
        return "Contraseña incorrecta"
