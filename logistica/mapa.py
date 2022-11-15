from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
from datetime import datetime

lgMapa = Blueprint('mapa', __name__, url_prefix='/')

consultaTodoMapa = """
select Numero_envío, Direccion,  Localidad, Vendedor, Latitud, Longitud, Fecha,chofer,estado_envio,Zona,Timechangestamp,Motivo
from ViajesFlexs
"""
consultaMapa = """
select 
    Numero_envío, Direccion,  Localidad, Vendedor, Latitud, Longitud, Fecha,chofer,estado_envio,Zona,Timechangestamp,Motivo
from
    ViajesFlexs 
where 
    estado_envio in ("Retirado","Lista Para Retirar","Listo Para Retirar","Listo para salir (Sectorizado)")
"""

@lgMapa.route("/logistica/jsonPendientes", methods = ["GET","POST"])
# @auth.login_required
def jsonPendientes():
    if request.method == "POST":
        estados = ""
        if "listaParaRetirar" in request.form.keys():
            estados += " where estado_envio in ('Lista Para Retirar','Listo para Retirar','Listo para Retirar')"
        if "enDeposito" in request.form.keys():
            if len(estados) < 5:
                estados += " where estado_envio = 'Listo para salir (Sectorizado)' or lower(Zona) = '~en deposito'"
            else:
                estados += " or estado_envio = 'Listo para salir (Sectorizado)'"
        if "enCamino" in request.form.keys():
            if len(estados) < 5:
                estados += " where estado_envio = 'En Camino'"
            else:
                estados += " or estado_envio = 'En Camino'"
        if "noEntregado" in request.form.keys():
            if len(estados) < 5:
                estados += " where Motivo in ('Nadie en Domicilio (Reprogramado)','Domicilio no visitado')"
            else:
                estados += " or Motivo in ('Nadie en Domicilio (Reprogramado)','Domicilio no visitado')"
        if "retirado" in request.form.keys():
            if len(estados) < 5:
                estados += " where estado_envio = 'Retirado'"
            else:
                estados += " or estado_envio = 'Retirado'"
        if "entregado" in request.form.keys():
            if len(estados) < 5:
                estados += " where estado_envio = 'Entregado'"
            else:
                estados += " or estado_envio = 'Entregado'"
        if "listaParaRetirar" in request.form.keys():
            if len(estados) < 5:
                estados += " where not "
            else:
                estados += " and not " 
            estados += "(Vendedor in ('ONEARTARGENTINA') and estado_envio = 'Lista Para Retirar')"
        if  request.form["fecha"] != "":
            if len(estados) < 5:
                estados += " where "
            else:
                estados += " and " 
            estados += "Fecha = '" + request.form["fecha"] + "'"
        if "extra" in request.form.keys():
            extra = request.form["extra"]
            if extra != "" and not ";" in extra:
                if len(estados) < 5:
                    estados += " where "
                else:
                    estados += " and " 
                estados += request.form["extra"]
        if len(estados) < 5:
            estados += "where tipo_envio = 2"
        else:
            estados += " and tipo_envio = 2"
        session["consultaMapa"] = consultaTodoMapa+estados
        print(session["consultaMapa"])
        return redirect("/logistica/vistamapa")
    else:
        jsonPendientes = {}
        midb = database.connect_db()
        cursor = midb.cursor()
        if "consultaMapa" in session.keys():
            cursor.execute(session["consultaMapa"])
        else:
            cursor.execute(consultaMapa)
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

@lgMapa.route("/logistica/vistamapa")
@auth.login_required
def carga_mapa():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("SELECT `Nombre Zona` FROM mmslogis_MMSPack.ZonasyChoferes")
    zonas = []
    for x in cursor.fetchall():
        zonas.append(x[0])
    return render_template("logistica/mapa.html", 
                            auth = session.get("user_auth"),
                            mapa=True,
                            zonas=zonas)


@lgMapa.route("/cambiozona/", methods=["GET","POST"])
@auth.login_required
def cambioZona():
    hoy = str(datetime.now())[0:10]
    if request.method == "GET":
        zona = request.args.get("zona")
        envio = request.args.get("envio")
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = f"update ViajesFlexs set Zona = '{zona}/2' where Numero_envío = '{envio}'"
        cursor.execute(sql)
        midb.commit()
        print(sql)
        return redirect("/logistica/vistamapa")

        
@lgMapa.route("/logistica/cambiozonamasivo", methods=["GET","POST"])
@auth.login_required
def cambioZonaMasivo():
    hoy = str(datetime.now())[0:10]
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "GET":
        zona = request.args.get("zonamasiva")
        envios = request.args.get("enviosAzonificar")
        listaEnvios = envios.split(",")
        envios = ""
        for x in listaEnvios:
            envios += "'" + x + "',"
        envios = envios[0:-1]
        if zona != "null":
            zona = "'" + str(zona).replace("'","") + "/2'"
        print(zona)
        sql = f"update ViajesFlexs set Zona = {zona} where Numero_envío in ({envios})"
        print(sql)
        cursor.execute(sql)
        midb.commit()
        return redirect("/logistica/vistamapa")
    else:
        post = request.form.keys() 
        zona = request.form.get("zonamasiva")
        envios = request.form.get("enviosAzonificar")
        listaEnvios = envios.split(",")
        envios = ""
        for x in listaEnvios:
            envios += "'" + x + "',"
        envios = envios[0:-1]
        if zona != "null":
            zona = "'" + str(zona).replace("'","") + "/2'"
        sql = f"update ViajesFlexs set Zona = {zona} where Numero_envío in ({envios})"
        cursor.execute(sql)
        midb.commit()
        return "NO ES GET"
