from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session
from Backend.auth import auth
from Backend.database import database
from .script import  geolocalizarFaltantes
from Backend.tareas.tareasProgramadas import descargaDesdePlanillas
from .Envio import Envio
lg = Blueprint('logistica', __name__, url_prefix='/')

@lg.route("/descargalogixs")
@auth.login_required
def descargaLogixsBoton():
    descargaDesdePlanillas()
    return redirect ("/vistamapa")

@lg.route('/formularioEdicionLogistica')
def mostrarFormulario():
  direccion = request.args.get('direccion')
  localidad = request.args.get('localidad')
  vendedor = request.args.get('vendedor')
  cobrar = request.args.get('cobrar')
  numeroEnvio = request.args.get('numeroEnvio')
  estado = request.args.get('estado')
  return render_template('logistica/formularioEdicion.html', 
                         direccion=direccion, 
                         localidad=localidad, 
                         vendedor=vendedor, 
                         cobrar=cobrar,
                         numeroEnvio=numeroEnvio, 
                         estado=estado)

@lg.route('/guardarCambiosEnvio',methods=["POST"])
def guardarCambiosEnvio():
    numEnvio = request.form.get("numEnvio")
    direccion = request.form.get("direccion")
    localidad = request.form.get("localidad")
    cobrar = request.form.get("cobrar")
    vendedor = request.form.get("vendedor")
    modifico = session['user_id']
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("update ViajesFlexs set Direccion = %s,Localidad = %s,Cobrar = %s, columna_2 = %s where Numero_envío = %s",(direccion,localidad,cobrar,modifico,numEnvio))
    midb.commit()
    geolocalizarFaltantes(midb)
    return "exito"

@lg.route("/logistica/ruteo")
@auth.login_required
def RuteoPrimera():
    from .mapa import consultaMapa
    midb = database.connect_db()
    cursor = midb.cursor()
    cabezeras = ["Acciones","Zona","Fecha","Numero de envío","Direccion","Localidad","CP","vendedor","Cobrar","Chofer","Estado","QR"]
    if "tipoEnvio" in session.keys():
        valueMapa = session["tipoEnvio"]
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
        qr = x[15]
        cobrar = x[16]
        lista.append([zona,fecha,nEnvio,direccion,localidad,cp,vendedor,cobrar,chofer,estado,qr])
    return render_template("logistica/ruteo.html", 
                            titulo="Ruteo",
                            viajes=lista,
                            columnas = cabezeras,
                            cant_columnas = len(cabezeras),
                            contador = 0,
                            acciones = True,
                            auth = session.get("user_auth"))


@lg.route("/cambiartipoenvio",methods = ["POST"])
@auth.login_required
def cambioTipoEnvio():
    tipoEnvio = request.form["tipoEnvio"]
    envio = request.form["envio"]
    sql = "update ViajesFlexs set tipo_envio = %s where Numero_envío = %s"
    values = (tipoEnvio,envio)
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    return redirect("/vistamapa")

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
    return redirect("/vistamapa")

@lg.route("/logistica/reprogramar/<nro_envio>")
@auth.login_required
def reprogramarEnvioGet(nro_envio):
    return render_template("/logistica/reprogramar.html",
                            titulo = "Reprogramar envio",
                            nro_envio = nro_envio,
                            auth = session.get("user_auth"))
    

@lg.route("/logistica/reprogramar",methods=["POST"])
@auth.login_required
def reprogramarEnvioPost():
    fecha = request.form.get("fecha")
    nro_envio = request.form.get("nEnvio")
    sql = "update ViajesFlexs set reprogramado = %s where Numero_envío = %s;"
    values = (fecha,nro_envio)
    print(sql % values)
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return redirect("/logistica/ruteo")