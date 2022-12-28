from flask import Blueprint, redirect, render_template, request, session,jsonify
from auth import auth
from database import database

lgMapa = Blueprint('mapa', __name__, url_prefix='/')

consultaTodoMapa = """
select Numero_envío, Direccion,  Localidad, Vendedor, Latitud, Longitud, Fecha,chofer,estado_envio,Zona,Timechangestamp,Motivo,tipo_envio
from ViajesFlexs
"""
consultaMapa = """
select 
    Numero_envío, Direccion,  Localidad, Vendedor, Latitud, Longitud, Fecha,chofer,estado_envio,Zona,Timechangestamp,Motivo,tipo_envio
from
    ViajesFlexs 
where 
    (estado_envio = 'Lista Para Retirar' and not Vendedor in ('ONEARTARGENTINA','PF FERRETERIA','La querciola')) and estado_envio in ("Retirado","Lista Para Retirar","Listo Para Retirar","Listo para salir (Sectorizado)")
"""

@lgMapa.route("/logistica/jsonPendientes", methods = ["GET","POST"])
# @auth.login_required
def jsonPendientes():
    if request.method == "POST":
        estados = ""
        tipoEnvio = request.form["tipoEnvio"]
        estados += f" where tipo_envio = {tipoEnvio}  and not (estado_envio = 'Lista Para Retirar' and Vendedor in ('ONEARTARGENTINA','PF FERRETERIA','La querciola')) and estado_envio in ('algo')"

        if "listaParaRetirar" in request.form.keys():
            estados = estados[0:-1] + ",'Lista Para Retirar')"
        if "enDeposito" in request.form.keys():
            estados = estados[0:-1] + ",'Listo para salir (Sectorizado)')"
        if "enCamino" in request.form.keys():
            estados = estados[0:-1] + " ,'En Camino')"
        if "retirado" in request.form.keys():
            estados = estados[0:-1] + ",'Retirado')"
        if "entregado" in request.form.keys():
            estados = estados[0:-1] + ",'Entregado')"
        if "noEntregado" in request.form.keys():
            estados = estados[0:-1] + " ,'No Entregado') and Motivo != 'Cancelado'"
        if  request.form["fecha"] != "":
            estados += " and Fecha = '" + request.form["fecha"] + "'"
        if "extra" in request.form.keys():
            extra = request.form["extra"]
            if extra != "" and not ";" in extra:
                estados += " and " + request.form["extra"]
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
                "motivo":x[11],
                "tipoEnvio":x[12]
            }
        return jsonify(jsonPendientes)

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


@lgMapa.route("/cambiozona", methods=["GET","POST"])
@auth.login_required
def cambioZona():
    if request.method == "POST":
        zona = request.form.get("zona")
        envio = request.form.get("envio")
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = f"update ViajesFlexs set Zona = '{zona}' where Numero_envío = '{envio}'"
        cursor.execute(sql)
        midb.commit()
        print(sql)
        return redirect("/logistica/vistamapa")

        
@lgMapa.route("/logistica/cambiozonamasivo", methods=["GET","POST"])
@auth.login_required
def cambioZonaMasivo():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "GET":
        zona = request.args.get("zonamasiva")
        envios = request.args.get("enviosAzonificar")
        tipoEnvio = request.args.get("tipoEnvio")
        listaEnvios = envios.split(",")
        envios = ""
        for x in listaEnvios:
            envios += "'" + x + "',"
        envios = envios[0:-1]
        if zona != "null":
            zona = f"""'{str(zona).replace("'","")}/{tipoEnvio}'"""
        sql = f"update ViajesFlexs set Zona = {zona} where Numero_envío in ({envios})"
        cursor.execute(sql)
        midb.commit()
        return redirect("/logistica/vistamapa")
    else:
        post = request.form.keys() 
        zona = request.form.get("zonamasiva")
        envios = request.form.get("enviosAzonificar")
        tipoEnvio = request.form.get("tipoEnvio")
        listaEnvios = envios.split(",")
        envios = ""
        for x in listaEnvios:
            envios += "'" + x + "',"
        envios = envios[0:-1]
        if zona != "null":
            zona = f"""'{str(zona).replace("'","")}/{tipoEnvio}'"""
        sql = f"update ViajesFlexs set Zona = {zona} where Numero_envío in ({envios})"
        cursor.execute(sql)
        midb.commit()
        return "NO ES GET"
