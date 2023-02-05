from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
from .script import  geolocalizarFaltantes
from tareasProgramadas.tareasProgramadas import descargaDesdePlanillas
from .Envio import Envio
lg = Blueprint('logistica', __name__, url_prefix='/')

@lg.route("/descargalogixs")
@auth.login_required
def descargaLogixsBoton():
    descargaDesdePlanillas()
    return redirect ("logistica/vistamapa")

@lg.route('/formularioEdicionLogistica')
def mostrarFormulario():
  direccion = request.args.get('direccion')
  localidad = request.args.get('localidad')
  vendedor = request.args.get('vendedor')
  numeroEnvio = request.args.get('numeroEnvio')
  estado = request.args.get('estado')
  return render_template('logistica/formularioEdicion.html', direccion=direccion, localidad=localidad, vendedor=vendedor, numeroEnvio=numeroEnvio, estado=estado)

@lg.route('/guardarCambiosEnvio',methods=["POST"])
def guardarCambiosEnvio():
    numEnvio = request.form.get("numEnvio")
    direccion = request.form.get("direccion")
    localidad = request.form.get("localidad")
    vendedor = request.form.get("vendedor")
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("update ViajesFlexs set Direccion = %s,Localidad = %s where Numero_envío = %s",(direccion,localidad,numEnvio))
    midb.commit()
    geolocalizarFaltantes(midb)
    return "exito"

@lg.route("/logistica/ruteo")
@auth.login_required
def RuteoPrimera():
    from .mapa import consultaMapa
    midb = database.connect_db()
    cursor = midb.cursor()
    cabezeras = ["Zona","Fecha","Numero de envío","Direccion","Localidad","CP","vendedor","Chofer","Estado"]
    if "valuesMapa" in session.keys():
        valueMapa = session["valuesMapa"]
        cursor.execute(consultaMapa,(valueMapa,))
    else:
        cursor.execute(consultaMapa,(2,))
    resultado = cursor.fetchall()
    lista = []
    for x in resultado:
        zona = x[9]
        fecha = x[6]
        nEnvio = x[0]
        direccion = x[1]
        localidad = x[2]
        cp = x[13]
        vendedor = x[3]
        chofer = x[7]
        estado = x[8]
        lista.append([zona,fecha,nEnvio,direccion,localidad,cp,vendedor,chofer,estado])
    return render_template("logistica/VistaTabla.html", 
                            titulo="Ruteo",
                            viajes=lista,
                            columnas = cabezeras,
                            cant_columnas = len(cabezeras),
                            contador = 0,
                            auth = session.get("user_auth"))

@lg.route("/bultosporenvio",methods = ["POST"])
@auth.login_required
def bultosPorEnvio():
    bultos = request.form["bultos"]
    envio = request.form["envio"]
    sql = "update ViajesFlexs set columna_1 = %s where Numero_envío = %s"
    values = (bultos,envio)
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    return redirect("/logistica/vistamapa")