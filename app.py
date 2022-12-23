from flask import Flask, render_template, session
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


from usuarios import usuarios
app.register_blueprint(usuarios.us)
from envios_cliente import envios_cliente
app.register_blueprint(envios_cliente.envcl)
from MeLi import MeLi
app.register_blueprint(MeLi.ML)
from uploadXLSX import formatoMeLi
app.register_blueprint(formatoMeLi.upML)
from NOML import NOML
app.register_blueprint(NOML.NOML)
from facturacion import flexs
app.register_blueprint(flexs.fb)
from facturacion import cobrados
app.register_blueprint(cobrados.cb)
from facturacion import gsolutions
app.register_blueprint(gsolutions.fa)
from facturacion import precios
app.register_blueprint(precios.pr)
from facturacion import apodos
app.register_blueprint(apodos.ap)
from estadistica import estadistica
app.register_blueprint(estadistica.est)
from uploadXLSX import formatomms
app.register_blueprint(formatomms.formms)

#EMPLEADO
from empleado import empleado
app.register_blueprint(empleado.em)
from empleado import sueldo
app.register_blueprint(sueldo.MS)

#LOGISTICA
from logistica import asignacionRetiros
app.register_blueprint(asignacionRetiros.lgAR)
from logistica import asignacionZonas
app.register_blueprint(asignacionZonas.lgAZ)
from logistica import hojaRuta
app.register_blueprint(hojaRuta.hojaRuta)
from logistica import appChofer
app.register_blueprint(appChofer.pd)
from logistica import rutaChofer
app.register_blueprint(rutaChofer.lgMR)

#HISTORIAL
from historial import historial
app.register_blueprint(historial.hsList)
from historial import mapa
app.register_blueprint(mapa.mapaHS)

@app.route("/")
@auth.login_required
def bienvenido():
    return render_template("index.html", titulo="Bienvenido a MMSPack", auth = session.get("user_auth"), usuario = session.get("user_id"))


from apscheduler.schedulers.background import BackgroundScheduler
from descargaLogixs.downloadSpreedSheets import cargaCamargo,cargaformatoMMS
from descargaLogixs.descargaLogixs import descargaLogixs
from database.database import connect_db


scheduler = BackgroundScheduler()
@scheduler.scheduled_job('cron',minute="*/10", hour="09-17")
def background_task():
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select Numero_envío from ViajesFlexs")
    nrosEnvios = {}
    for env in cursor.fetchall():
        nrosEnvios[env[0]] = True
    descargaLogixs(midb,nrosEnvios)
    midb.close()
    cargaCamargo(nrosEnvios)
    cargaformatoMMS(nrosEnvios)

scheduler.start()