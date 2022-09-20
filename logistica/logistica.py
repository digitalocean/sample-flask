from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
from .script import  geolocalizarFaltantes
from descargaLogixs import descargaLogixs,actualizarDesdeHistorial

lg = Blueprint('logistica', __name__, url_prefix='/')



@lg.route("/descargalogixs")
@auth.login_required
def descargaLogixsBoton():
    tiempoinicio = datetime.now()
    midb = database.connect_db()
    descargaLogixs.descargaLogixs(midb)
    finDescargaLogixs = datetime.now()
    print(f"Tiempo de actualizacion desde logixs: {finDescargaLogixs - tiempoinicio}")
    geolocalizarFaltantes(midb)
    midb.close()
    tiempofinal = datetime.now()
    print(f"Tiempo de geolocalizacion: {tiempofinal - finDescargaLogixs}")
    duracion = tiempofinal - tiempoinicio
    print(f"Tiempo total: {duracion}")
    return redirect ("vistamapa")


@lg.route("/busquedaAdmin")
@auth.login_required
def busqueda():
    mjstbla = ""
    midb = database.connect_db()
    cursor = midb.cursor()
    busqueda = request.args.get("buscar")
    columnas = "Fecha,Hora,id,Zona,Numero_envío,Chofer,Direccion_Completa,Vendedor,estado_envio,motivo_noenvio,Correo_chofer,Foto_domicilio,Ubicacion_ultimoestado"
    cabezeras = ["Accion","Fecha","Hora","ID","Zona","Numero de envio","Chofer","Direccion","Vendedor","estado_envio","Motivo","Modifico","Tiene foto","Ubicacion estado"]
    #  order by Numero_envío, Fecha desc,Hora desc
    if busqueda.lower() == "entregadoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' group by Numero_envío having count(Numero_envío) >1) and estado_envio = 'Entregado' order by Numero_envío"
    elif busqueda.lower() == "noentregadoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'No Entregado' group by Numero_envío having count(Numero_envío) >1) and estado_envio = 'No Entregado' order by Numero_envío"
    elif busqueda.lower() == "encaminoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'En Camino' group by Numero_envío having count(Numero_envío) >1) and estado_envio = 'En Camino' order by Numero_envío"
    elif busqueda.lower() == "segundasvueltas":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' group by Numero_envío having count(Numero_envío) >1) order by Fecha desc, Hora desc, Numero_envío"
    elif busqueda.lower() == "tercerasvueltas":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' group by Numero_envío having count(Numero_envío) >2) order by Fecha desc, Hora desc, Numero_envío"
    elif busqueda.lower() == "sinencamino":
        sql = f"select {columnas} from historial_estados where estado_envio in ('Entregado','No Entregado','No entregado','Listo para salir (Sectorizado)') and not Numero_envío in (select Numero_envío from historial_estados where estado_envio in ('En Camino') or motivo_noenvio in ('Cancelado'))"
    else:
        sql = f"select {columnas} from historial_estados where Numero_envío like '%{busqueda}%' or Chofer like '%{busqueda}%' or Vendedor like '%{busqueda}%' or Direccion_completa like '%{busqueda}%' or estado_envio like '%{busqueda}%' or motivo_noenvio like '%{busqueda}%' order by Fecha desc, Hora desc;"
    print(sql)
    cursor.execute(sql)
    resultado = cursor.fetchall()
    print(len(resultado))
    if len(resultado) == 0:
        sql = f"select Fecha, Numero_envío, Direccion, Localidad, Vendedor from ViajesFlexs where Numero_envío like '%{busqueda}%' or Chofer like '%{busqueda}%' or Vendedor like '%{busqueda}%' or Direccion like '%{busqueda}%' order by Fecha desc"
        cursor.execute(sql)
        print(sql)
        resultado = cursor.fetchone()
        lista = (resultado,)
        mjstbla = "No se registro historial de este envio"
        cabezeras = ["Fecha", "Numero_envío", "Direccion", "Localidad", "Vendedor"]
        return render_template("vistaTabla.html", titulo="Busqueda", viajes=lista ,columnas = cabezeras, cant_columnas = len(cabezeras), mensaje_tabla = mjstbla, auth = session.get("user_auth"))
    lista = []
    cobra = 0
    print(sql)
    for x in resultado:
        lista.append(x)
    print(range(len(cabezeras)))
    return render_template("vistaTabla.html", titulo="Busqueda", viajes=lista,cobra = cobra ,columnas = cabezeras, cant_columnas = len(cabezeras),contador = 0, historial = True, auth = session.get("user_auth"))