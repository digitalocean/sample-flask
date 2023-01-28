from flask import Flask, render_template, session,current_app
from flask_cors import CORS
import os



app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY")
    )
CORS(app)


from auth import auth
app.register_blueprint(auth.auth)
from logistica import logistica
app.register_blueprint(logistica.lg)
from logistica import mapa
app.register_blueprint(mapa.lgMapa)


from cliente import cliente
app.register_blueprint(cliente.cl)
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
from logistica import devoluciones
app.register_blueprint(devoluciones.devolucion)
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
from tareasProgramadas.tareasProgramadas import informeEstados,descargaDesdePlanillas,informeFinalDia

scheduler = BackgroundScheduler()
@scheduler.scheduled_job('cron',day_of_week='mon-fri',minute="*/8", hour="12-18")
def background_task():
    descargaDesdePlanillas()

@scheduler.scheduled_job('cron',day_of_week='sat',minute="*/8", hour="14-18")
def background_task():
    descargaDesdePlanillas()

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=16)
def background_task2():
    informeEstados("Quality Shop")
    informeEstados("Armin")
    informeEstados("Happe")
    informeEstados("Universal Shop")

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=22,min=30)
def background_task3():
    informeEstados("Quality Shop")
    informeEstados("Armin")
    informeEstados("Happe")
    informeEstados("Universal Shop")

@scheduler.scheduled_job('cron', day_of_week='tue-sun', hour='3', minute='1')
def background_task4():
    informeFinalDia()


scheduler.start()