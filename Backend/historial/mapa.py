from flask import Blueprint, redirect, render_template, request, session,jsonify
from Backend.auth import auth
from Backend.database import database
from Backend.scriptGeneral.scriptGeneral import consultaChoferCorreo
from datetime import datetime

mapaHS = Blueprint('mapaHistorial', __name__, url_prefix='/')

@mapaHS.route("/historial/vistamapacompleto")
@auth.login_required
def carga_mapaCompleto_historial():
    return render_template("historial/mapaCompleto.html", 
                        auth = session.get("user_auth"),
                        mapa=True,
                        choferes=consultaChoferCorreo(database.connect_db()))
    

@mapaHS.route("/historial/mapacompleto", methods = ["GET","POST"])
@auth.login_required
def mapaCompletoHistorial():
    if request.method == "POST":
        fecha = request.form["fecha"]
        tipoEnvio = request.form["tipoEnvio"]
        sql = f"""
        select 
            V.Numero_envío, V.Direccion,  V.Localidad, V.Vendedor, V.Latitud, V.Longitud, V.Fecha,V.chofer,V.estado_envio,H.Zona,V.Timechangestamp,V.Motivo
        from 
            ViajesFlexs as V
        JOIN
            historial_estados as H
        ON
            V.Numero_envío = H.Numero_envío where H.Fecha = '{fecha}' and V.tipo_envio = {tipoEnvio} and H.estado_envio in ('En Camino','Reasignado')"""
        session["consultaMapaHistorial"] = sql
        return redirect("/historial/vistamapacompleto")
    elif request.method == "GET":
        jsonPendientes = {}
        midb = database.connect_db()
        cursor = midb.cursor()
        if "consultaMapaHistorial" in session.keys():
            cursor.execute(session["consultaMapaHistorial"])
            for x in cursor.fetchall():
                jsonPendientes[x[0]] = {
                    "direccion":x[1],
                    "localidad":x[2],
                    "vendedor":x[3],
                    "latitud":x[4], 
                    "longitud":x[5], 
                    "fecha":x[6],
                    "chofer":x[7],
                    "estado_envio":x[8],
                    "zona":x[9],
                    "fechaUltimoEstado":str(x[10])[0:10],
                    "horaUltimoEstado":str(x[10])[10:19],
                    "motivo":x[11]
                }
            return jsonPendientes
        return jsonify({})


@mapaHS.route("/historial/vistamapa")
@auth.login_required
def carga_mapa_historial():
    # midb = database.connect_db()
    # cursor = midb.cursor()
    # cursor.execute("SELECT Chofer FROM mmslogis_MMSPack.historial_estados GROUP BY Chofer")
    # choferes = []
    # for x in cursor.fetchall():
    #     choferes.append(x[0])
    return render_template("historial/mapa.html", 
                            auth = session.get("user_auth"),
                            mapa=True,
                            choferes=consultaChoferCorreo(database.connect_db()))



@mapaHS.route("/historial/mapa", methods = ["GET","POST"])
@auth.login_required
def mapaHistorial():
    if request.method == "POST":
        fecha = request.form["fecha"]
        chofer = request.form["chofer"]
        sql = f"""
        select 
            V.Numero_envío, V.Direccion,  V.Localidad, V.Vendedor, V.Latitud, V.Longitud, V.Fecha,V.chofer,V.estado_envio,H.Zona,V.Timechangestamp,V.Motivo
        from 
            ViajesFlexs as V
        JOIN
            historial_estados as H
        ON
            V.Numero_envío = H.Numero_envío and H.Fecha = '{fecha}' and H.Chofer = '{chofer}' and H.estado_envio in ('En Camino','Reasignado')"""
        session["consultaMapaHistorial"] = sql
        return redirect("/historial/vistamapa")
    elif request.method == "GET":
        jsonPendientes = {}
        midb = database.connect_db()
        cursor = midb.cursor()
        if "consultaMapaHistorial" in session.keys():
            cursor.execute(session["consultaMapaHistorial"])
            for x in cursor.fetchall():
                jsonPendientes[x[0]] = {
                    "direccion":x[1],
                    "localidad":x[2],
                    "vendedor":x[3],
                    "latitud":x[4], 
                    "longitud":x[5], 
                    "fecha":x[6],
                    "chofer":x[7],
                    "estado_envio":x[8],
                    "zona":x[9],
                    "fechaUltimoEstado":str(x[10])[0:10],
                    "horaUltimoEstado":str(x[10])[10:19],
                    "motivo":x[11]
                }
            return jsonPendientes
        return jsonify({})

