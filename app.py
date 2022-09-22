import datetime
from email import message
from telnetlib import STATUS
from urllib import response
from flask import Flask, render_template, request, session, make_response
from flask_cors import CORS
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

