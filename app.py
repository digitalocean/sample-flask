import datetime
from email import message
from telnetlib import STATUS
from urllib import response
from flask import Flask, render_template, request, session, jsonify, make_response
from flask_cors import CORS
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
import jwt

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
from NOML import NOML
app.register_blueprint(NOML.NOML)

@app.route("/")
@auth.login_required
def bienvenido():
    return render_template("index.html", titulo="Bienvenido", auth = session.get("user_auth"), usuario = session.get("user_id"))

from database import database
@app.route("/api/users/create",methods=["POST"])
def test():
    try:
        data = request.get_json()
        midb = database.connect_db()
        cursor = midb.cursor()
        passw = generate_password_hash(data['password'])
        cursor.execute(f"insert into empleado (nombre,puesto,vehiculo,patente,correo,dni,cbu,telefono,direccion,localidad,password) values('{data['nombre']}','{data['puesto']}','{data['vehiculo']}','{data['patente']}','{data['correo']}','{data['dni']}','{data['cbu']}','{data['telefono']}','{data['direccion']}','{data['localidad']}','{passw}')")
        midb.commit()
        midb.close()
        return jsonify(success=True,message="Usuario Creado",data=None)
    except:
        return jsonify(success=False,message="Se produjo un error al intentar crear el usuario",data=None)

@app.route("/api/users/login",methods=["POST"])
def test2():
    dataLogin = request.get_json()
    midb = database.connect_db()
    cursor = midb.cursor()
    sql =f"select password,id,nombre,correo from empleado where dni = {dataLogin['dni']}"
    cursor.execute(sql)
    res = cursor.fetchone()
    if res is None:
        return jsonify(success=False,message="Usuario inexistente",data=None)
    midb.close()
    if check_password_hash(res[0],dataLogin["password"]):
        data = {
            'id':res[1],
            'nombre':res[2],
            'correo':res[3],
            'session_token': None
        }
        return jsonify(success=True,message="Inicio de sesion correcto",data=data)
    else:
        return jsonify(success=False,message="Contraseña incorrecta",data=None)

