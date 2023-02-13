from flask import Blueprint, redirect, render_template, request, session,jsonify
from auth import auth
from database import database

lgMapa = Blueprint('mapa', __name__, url_prefix='/')

consultaMapa = """
        select 
            Numero_envío, 
            Direccion, 
            Localidad, 
            Vendedor, 
            Latitud, 
            Longitud, 
            Fecha,
            chofer,
            estado_envio,
            Zona,
            Timechangestamp,
            Motivo,
            tipo_envio,
            CP,
            columna_1,
            Scanner
        from ViajesFlexs
        where 
            not (estado_envio = "Lista Para Retirar" and vendedor(Vendedor) in ("PF FERRETERIA"))
        and
            tipo_envio = %s 
        and 
            estado_envio in ('Lista Para Retirar','Para preparar','Retirado','Listo para salir (Sectorizado)') 
        and
            not (tipo_envio = 15 and Fecha < current_date())
        and
            not (estado_envio = "Lista Para Retirar" and Fecha > current_date())
        """

@lgMapa.route("/logistica/jsonPendientes", methods = ["GET","POST"])
@auth.login_required
def jsonPendientes():
    if request.method == "POST":
        tipoEnvio = request.form["tipoEnvio"]
        session["tipoEnvio"] = tipoEnvio
        session["valuesMapa"] = tipoEnvio
        return redirect("/logistica/vistamapa")
    else:
        jsonPendientes = {}
        midb = database.connect_db()
        cursor = midb.cursor()
        if "valuesMapa" in session.keys():
            valueMapa = session["valuesMapa"]
            cursor.execute(consultaMapa,(valueMapa,))
        else:
            cursor.execute(consultaMapa,(2,))
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
                "tipoEnvio":x[12],
                "CP":x[13],
                "bultos":x[14]
            }
        return jsonify(jsonPendientes)

@lgMapa.route("/logistica/vistamapa")
@auth.login_required
def carga_mapa():
    midb = database.connect_db()
    cursor = midb.cursor()
    try:
        tipoEnvio = session["valuesMapa"]
    except: 
        tipoEnvio = 2
    cursor.execute("SELECT `Nombre Zona` FROM mmslogis_MMSPack.ZonasyChoferes where tipoEnvio = %s",(tipoEnvio,))
    zonas = []
    for x in cursor.fetchall():
        zonas.append(x[0])
    return render_template("logistica/mapa.html", 
                            auth = session.get("user_auth"),
                            mapa=True,
                            zonas=zonas)


@lgMapa.route("/logistica/mapa/fueradezona", methods=["GET","POST"])
@auth.login_required
def fueraDeZonaMapa():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("""
                    update ViajesFlexs 
                        set 
                            estado_envio = "Fuera De Zona",
                            Motivo = null,
                            `Check` = null,
                            Zona = null where Numero_envío = %s;
                    """,(request.json["nro_envio"],))
    midb.commit()
    return ""

@lgMapa.route("/logistica/mapa/cancelado", methods=["GET","POST"])
@auth.login_required
def canceladoMapa():
    midb = database.connect_db()
    cursor = midb.cursor()
    envio = request.json["nro_envio"]
    cursor.execute("""
                    update ViajesFlexs 
                        set 
                            estado_envio = "Cancelado",
                            Motivo = null,
                            `Check` = null,
                            Zona = null 
                        where
                            Numero_envío = %s
                    """,(envio,))
    midb.commit()
    return ""

@lgMapa.route("/logistica/mapa/novino", methods=["GET","POST"])
@auth.login_required
def noVinoMapa():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("""
                    update ViajesFlexs 
                        set 
                            estado_envio = "No Vino",
                            Motivo = null,
                            `Check` = null,
                            Zona = null where Numero_envío = %s and estado_envio = "Lista Para Retirar"
                    """,(request.json["nro_envio"],))
    midb.commit()
    return ""

@lgMapa.route("/cambiozona", methods=["GET","POST"])
@auth.login_required
def cambioZona():
    if request.method == "POST":
        tipoEnvio = session["tipoEnvio"]
        zona = request.form.get("zona")
        zona = f"{zona}/{tipoEnvio}"
        envio = request.form.get("envio")
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = f"update ViajesFlexs set Zona = '{zona}' where Numero_envío = '{envio}'"
        cursor.execute(sql)
        midb.commit()
        return redirect("/logistica/vistamapa")

        
@lgMapa.route("/logistica/cambiozonamasivo", methods=["GET","POST"])
@auth.login_required
def cambioZonaMasivo():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "POST":
        tipoEnvio = session["tipoEnvio"]
        zona = request.form.get("zonamasiva")
        zona = f"{zona}/{tipoEnvio}"
        envios = request.form.get("enviosAzonificar")
        tipoEnvio = request.form.get("tipoEnvio")
        listaEnvios = envios.split(",")
        envios = ""
        for x in listaEnvios:
            envios += "'" + x + "',"
        envios = envios[0:-1]
        if zona != "null":
            zona = f"""'{str(zona).replace("'","")}'"""
            sql = f"update ViajesFlexs set Zona = {zona} where Numero_envío in ({envios})"
        else:
            sql = f"update ViajesFlexs set Zona = null where Numero_envío in ({envios})"
        cursor.execute(sql)
        midb.commit()
        return "NO ES GET"
