from flask import Flask, render_template, session
from flask_cors import CORS
import os


app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY")
    )
CORS(app)

from Backend.tareas import tareas
app.register_blueprint(tareas.ToDo)

from Backend.auth import auth
app.register_blueprint(auth.auth)
from Backend.logistica import logistica
app.register_blueprint(logistica.lg)
from Backend.logistica import mapa
app.register_blueprint(mapa.lgMapa)

from Backend.ftp import ftpMod
app.register_blueprint(ftpMod.ftpMod)


from Backend.cliente import cliente
app.register_blueprint(cliente.cl)
from Backend.envios_cliente import envios_cliente
app.register_blueprint(envios_cliente.envcl)
from Backend.NOML import NOML
app.register_blueprint(NOML.NOML)
from Backend.estadistica import estadistica
app.register_blueprint(estadistica.est)

#Vinculaciones
from Backend.MeLi import MeLi
app.register_blueprint(MeLi.ML)
from Backend.tiendaNube import tiendaNube
app.register_blueprint(tiendaNube.TN)

#FACTURACION
from Backend.facturacion import facturacion
app.register_blueprint(facturacion.FcGeneral)
from Backend.facturacion import cobrados
app.register_blueprint(cobrados.cb)
from Backend.facturacion import gsolutions
app.register_blueprint(gsolutions.fa)
from Backend.facturacion import precios
app.register_blueprint(precios.pr)
from Backend.facturacion import apodos
app.register_blueprint(apodos.ap)
from Backend.facturacion import localidadesMal
app.register_blueprint(localidadesMal.arregloLocalidades)


#CARGA XLSX
from Backend.uploadXLSX import chips
app.register_blueprint(chips.formatSim)
from Backend.uploadXLSX import formatomms
app.register_blueprint(formatomms.formms)
from Backend.uploadXLSX import formatoMeLi
app.register_blueprint(formatoMeLi.upML)

#EMPLEADO
from Backend.empleado import empleado
app.register_blueprint(empleado.em)
from Backend.empleado import sueldo
app.register_blueprint(sueldo.MS)

#LOGISTICA
from Backend.logistica import fijos
app.register_blueprint(fijos.fj)
from Backend.logistica import asignacionRetiros
app.register_blueprint(asignacionRetiros.lgAR)
from Backend.logistica import asignacionZonas
app.register_blueprint(asignacionZonas.lgAZ)
from Backend.logistica import hojaRuta
app.register_blueprint(hojaRuta.hojaRuta)
from Backend.logistica import devoluciones
app.register_blueprint(devoluciones.devolucion)
from Backend.logistica import appChofer
app.register_blueprint(appChofer.pd)
from Backend.logistica import appOperadores
app.register_blueprint(appOperadores.OPLG)
from Backend.logistica import rutaChofer
app.register_blueprint(rutaChofer.lgMR)
from Backend.logistica import vistaGeneral
app.register_blueprint(vistaGeneral.VG)

#HISTORIAL
from Backend.historial import historial
app.register_blueprint(historial.hsList)
from Backend.historial import mapa
app.register_blueprint(mapa.mapaHS)

@app.route("/")
@auth.login_required
def bienvenido():
    return render_template("index.html", titulo="Bienvenido a MMSPack", auth = session.get("user_auth"), usuario = session.get("user_id"))

from apscheduler.schedulers.background import BackgroundScheduler
from Backend.tareas.tareasProgramadas import informeEstados,descargaDesdePlanillas,informeFinalDia,ponerNoVisitados

scheduler = BackgroundScheduler()
@scheduler.scheduled_job('cron',day_of_week='mon-fri',minute="*/8", hour="12-18")
def background_task0():
    descargaDesdePlanillas()

@scheduler.scheduled_job('cron',day_of_week='sat',minute="*/8", hour="14-18")
def background_task1():
    descargaDesdePlanillas()


@scheduler.scheduled_job('cron', day_of_week='tue-sun', hour='3', minute='0')
def background_task4():
    ponerNoVisitados()

@scheduler.scheduled_job('cron', day_of_week='tue-sun', hour='3', minute='5')
def background_task5():
    informeFinalDia()


scheduler.start()
