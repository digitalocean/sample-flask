from flask import Blueprint, redirect, render_template, request, session,url_for
from logistica.Envio import Envio
from auth import auth
from database import database
from datetime import datetime
from scriptGeneral import scriptGeneral
lgAZ = Blueprint('asignacionZonas', __name__, url_prefix='/')

@lgAZ.route("/logistica/asignacionChoferes")
@auth.login_required
def asignacion():
    midb = database.connect_db()
    cursor = midb.cursor()
    hoy = str(datetime.now())[0:10]
    tipoEnvio = session["tipoEnvio"]
    cursor.execute(f"select Zona from ViajesFlexs where tipo_envio = {tipoEnvio} and not Zona is null group by Zona")
    zonas = []
    for x in cursor.fetchall():
        zonas.append(x[0].split("/")[0])
    cursor.execute(f"select `Nombre Zona`, `Nombre Completo` from ZonasyChoferes where tipoEnvio = {tipoEnvio}")
    choferesAsignados = {}
    for x in cursor.fetchall():
        choferesAsignados[f"{x[0]}"] = x[1]
    return render_template("logistica/asignacionChoferes.html",zonas = zonas, choferes = scriptGeneral.correoChoferes(midb).keys(),asignados = choferesAsignados,auth = session.get("user_auth"))



@lgAZ.route("/choferesAsignados", methods=["GET","POST"])
@auth.login_required
def choferesAsignados():
    hoy = str(datetime.now())[0:10]
    midb = database.connect_db()
    tipoEnvio = session["tipoEnvio"]
    for x in request.args.keys():
        zona = x
        chofer = request.args.get(x)
        if chofer != '':
            midb = database.verificar_conexion(midb)
            cursor = midb.cursor()
            sql = f"update ZonasyChoferes set `Nombre Completo` = '{chofer}' where `Nombre Zona` = '{zona}' and tipoEnvio = {tipoEnvio}"
            print(sql)
            cursor.execute(sql)
            midb.commit()
    return redirect("/logistica/asignacionChoferes")


@lgAZ.route("/logistica/limpiarzonas", methods=["GET","POST"])
@auth.login_required
@auth.admin_required
def limpiarZonas():
    tipoEnvio = session["tipoEnvio"]
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select `Nombre Zona` from ZonasyChoferes where tipoEnvio = {tipoEnvio}")
    for zona in cursor.fetchall():
        cursor.execute(f"update ZonasyChoferes set `Nombre Completo` = null where `Nombre Zona` = '{zona[0]}' and tipoEnvio = {tipoEnvio}")
        midb.commit()
    return redirect ("/logistica/asignacionChoferes")


@lgAZ.route("/logistica/reasignar/", methods=["GET","POST"])
@auth.login_required
def agregarRetiro():
    if request.method == "GET":
        fecha = str(datetime.now())[0:10]
        return render_template("logistica/nuevoRegistro.html", 
                                titulo="Asignar",
                                fecha=fecha,
                                choferes=scriptGeneral.correoChoferes(database.connect_db()), 
                                auth = session.get("user_auth")
                                )
    elif request.method == "POST":
        fecha = request.form["fecha"]
        numeroEnvio = request.form["numeroEnvio"]
        chofer = request.form["chofer"]
        viaje = Envio.fromDB(numeroEnvio)
        if not viaje:
            return render_template("NOML/carga_noml.html",
                                    titulo="Carga",
                                    auth = session.get("user_auth"), 
                                    mensaje_error=f"{numeroEnvio} no se encuentra registrado", 
                                    numeroEnvio=numeroEnvio,
                                    clientes=scriptGeneral.consultar_clientes(database.connect_db()))
        viaje.enCamino(chofer,fecha)
        if "entregado" in request.form.keys():
            viaje.cambioEstado("Entregado",chofer,fecha)
        return render_template("logistica/nuevoRegistro.html", 
                                titulo="Asignar",
                                envio=numeroEnvio,
                                chofer=chofer,
                                fecha=fecha,
                                choferes=scriptGeneral.correoChoferes(database.connect_db()), 
                                auth = session.get("user_auth"))


@lgAZ.route("/logistica/ayudadeposito", methods=["GET","POST"])
@auth.login_required
def horasExtra():
    midb = database.connect_db()
    correoChofer = scriptGeneral.correoChoferes(midb)
    if request.method == "GET":
        fecha = str(datetime.now())[0:10]
        return render_template("logistica/horasTrabajadas.html", 
                                titulo="Asignar",
                                fecha=fecha,
                                choferes=correoChofer, 
                                auth = session.get("user_auth")
                                )
    elif request.method == "POST":
        fecha = request.form["fecha"]
        horas = request.form["horas"]
        chofer = request.form["chofer"]
        envio = f"{fecha}-{horas}-{str(chofer)[0:4]}"
        costo = int(horas) * 750
        sql = f"insert into historial_estados (Numero_envío,Fecha,Direccion_completa,estado_envio,Chofer,Correo_chofer,Costo) values('{envio}','{fecha}','{horas} horas trabajadas','ayuda deposito','{chofer}','{correoChofer[chofer]}',{costo})"
        cursor = midb.cursor()
        cursor.execute(sql)
        midb.commit()
        return render_template("logistica/horasTrabajadas.html", 
                                titulo="Asignar",
                                envio=horas,
                                chofer=chofer,
                                fecha=fecha,
                                choferes=correoChofer, 
                                auth = session.get("user_auth"))