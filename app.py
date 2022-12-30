from flask import Flask, render_template, session,current_app
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
from descargaLogixs.downloadSpreedSheets import cargaCamargo,cargaformatoMMS,cargaCamargoMe1
from descargaLogixs.descargaLogixs import descargaLogixs
from datetime import datetime
from database.database import connect_db
from logistica.script import  geolocalizarFaltantes
from scriptGeneral.scriptGeneral import enviar_correo
import pandas as pd

scheduler = BackgroundScheduler
def background_task():
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select Numero_envío,estado_envio from ViajesFlexs")
    nrosEnvios = {}
    for env in cursor.fetchall():
        nrosEnvios[env[0]] = env[1]
    descargaLogixs(midb,nrosEnvios)
    cargaCamargo(nrosEnvios)
    cargaCamargoMe1(nrosEnvios)
    cargaformatoMMS(nrosEnvios)
    geolocalizarFaltantes(midb)
    midb.close()
    
def informeQualityShop():
    midb = connect_db()
    fecha = datetime.now()
    pd.read_sql("select Fecha,Numero_envío as Seguimiento,comprador,Direccion,Localidad,estado_envio as Estado,Motivo,Cobrar as Monto from ViajesFlexs where Vendedor = 'Quality Shop' and Fecha = current_date();",midb).to_excel('descargas/informe.xlsx')
    enviar_correo(["qualityshopargentina@gmail.com","josudavidg@gmail.com","acciaiomatiassebastian@gmail.com"],f"Informe de envios {fecha.day}-{fecha.month}-{fecha.year} {fecha.hour}hs","informe.xlsx","informe.xlsx"," ")

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=16)
def background_task2():
    informeQualityShop()

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=21)
def background_task3():
    informeQualityShop()
    
scheduler.start()