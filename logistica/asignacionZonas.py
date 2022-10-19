from flask import Blueprint, redirect, render_template, request, session,url_for
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
    cursor.execute(f"select Zona from ViajesFlexs where Fecha = '{hoy}' and not Zona is null group by Zona")
    zonas = []
    for x in cursor.fetchall():
        zonas.append(x[0])
    cursor.execute("select `Nombre Zona`, `Nombre Completo` from ZonasyChoferes")
    choferesAsignados = {}
    for x in cursor.fetchall():
        choferesAsignados[x[0]] = x[1]
    return render_template("logistica/asignacionChoferes.html",zonas = zonas, choferes = scriptGeneral.correoChoferes(midb).keys(),asignados = choferesAsignados,auth = session.get("user_auth"))



@lgAZ.route("/choferesAsignados", methods=["GET","POST"])
@auth.login_required
def choferesAsignados():
    hoy = str(datetime.now())[0:10]
    midb = database.connect_db()
    for x in request.args.keys():
        zona = x
        chofer = request.args.get(x)
        if chofer != '':
            midb = database.verificar_conexion(midb)
            cursor = midb.cursor()
            sql = f"update ZonasyChoferes set `Nombre Completo` = '{chofer}' where `Nombre Zona` = '{zona}'"
            cursor.execute(sql)
            midb.commit()
    return redirect("/logistica/asignacionChoferes")

@lgAZ.route("/logistica/limpiarzonas", methods=["GET","POST"])
@auth.login_required
@auth.admin_required
def limpiarZonas():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select `Nombre Zona` from ZonasyChoferes")
    for zona in cursor.fetchall():
        cursor.execute(f"update ZonasyChoferes set `Nombre Completo` = null where `Nombre Zona` = '{zona[0]}'")
        midb.commit()
    return redirect ("/logistica/asignacionChoferes")

@lgAZ.route("/logistica/reasignar/", methods=["GET","POST"])
@auth.login_required
def agregarRetiro():
    midb = database.connect_db()
    correoChofer = scriptGeneral.correoChoferes(midb)
    if request.method == "GET":
        fecha = str(datetime.now())[0:10]
        return render_template("logistica/nuevoRegistro.html", 
                                titulo="Asignar",
                                fecha=fecha,
                                choferes=correoChofer, 
                                auth = session.get("user_auth")
                                )
    elif request.method == "POST":
        fecha = request.form["fecha"]
        numeroEnvio = request.form["numeroEnvio"]
        chofer = request.form["chofer"]
        cursor = midb.cursor()
        sql = """select Numero_envío,Direccion_completa,Localidad,Vendedor 
                        from historial_estados 
                        where Numero_envío = %s and estado_envio = 'En Camino'"""
        values = (numeroEnvio,)
        cursor.execute(sql,values)
        resu = cursor.fetchone()
        if resu is None:
            sql = "select Direccion_completa,Localidad,Vendedor from ViajesFlexs where Numero_envío = %s"
            values = (numeroEnvio,)
            cursor.execute(sql,values)
            res = cursor.fetchone()
            if res is None:
                return render_template("NOML/carga_noml.html",
                                    titulo="Carga", 
                                    auth = session.get("user_auth"), 
                                    mensaje_error=f"{numeroEnvio} no se encuentra registrado", 
                                    numeroEnvio=numeroEnvio,
                                    clientes=scriptGeneral.consultar_clientes(midb))
            sql = f"update ViajesFlexs set `Check` = 'En Camino', Chofer = '{chofer}',Correo_chofer='{correoChofer[chofer]}',estado_envio = 'En Camino',Motivo = 'En Camino', Ultimo_motivo = 'En Camino' where Numero_envío = '{numeroEnvio}'"
            print(sql)
            cursor.execute(sql)
            midb.commit()
        else:
            sql = f"update ViajesFlexs set `Check` = 'En Camino', Chofer = '{chofer}',Correo_chofer='{correoChofer[chofer]}',estado_envio = 'En Camino',Motivo = 'En Camino', Ultimo_motivo = 'En Camino' where Numero_envío = '{numeroEnvio}'"
            print(sql)
            cursor.execute(sql)
            midb.commit()
        return render_template("logistica/nuevoRegistro.html", 
                                titulo="Asignar",
                                envio=numeroEnvio,
                                chofer=chofer,
                                fecha=fecha,
                                choferes=correoChofer, 
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
        costo = (int(horas) * 750)
        
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


# @lgAZ.route("/logistica/reasignar/<nro_envio>/<chofer>")
# @auth.login_required
# def historial(nro_envio,chofer):
#     midb = database.connect_db()
#     correoChofer = scriptGeneral.correoChoferes(midb)
#     cursor = midb.cursor()
#     cursor.execute(f"""select Numero_envío,Direccion_completa,Localidad,Vendedor 
#                     from historial_estados 
#                     where Numero_envío = '{nro_envio}' and estado_envio = 'En Camino'""")
#     resu = cursor.fetchone()
#     if resu is None:
#         cursor.execute(f"select Direccion_completa,Localidad,Vendedor from ViajesFlexs where Numero_envío = '{nro_envio}'")
#         res = cursor.fetchone()
#         if res is None:
#             return redirect("/carga_noml")
#         cursor.execute(f"""insert into historial_estados (Fecha,Numero_envío,Direccion_completa,Localidad,Vendedor,Chofer,correo_chofer,
#         estado_envio,motivo_noenvio) 
#         values (current_date(),'{nro_envio}',
#         '{str(res[0]).replace(',',' ')}','{str(res[1]).replace(',',' ')}','{str(res[2]).replace(',',' ')}','{chofer}','{correoChofer[chofer]}',
#         'En Camino','En Camino')""")
#         midb.commit()
#         cursor.execute(f"update ViajesFlexs set `Check` = 'En Camino', Chofer = '{chofer}',Correo_chofer='{correoChofer[chofer]}',estado_envio = 'En Camino',Motivo = 'En Camino', Ultimo_motivo = 'En Camino' where Numero_envío = '{nro_envio}'")
#         midb.commit()
#     else:
#         cursor.execute(f"""insert into historial_estados 
#                     (Fecha,Numero_envío,Direccion_completa,Localidad,Vendedor,Chofer,correo_chofer,estado_envio,motivo_noenvio) 
#                     values 
#                     (current_date(),'{nro_envio}','{str(resu[1]).replace(',',' ')}',
#                     '{str(resu[2]).replace(',',' ')}','{str(resu[3]).replace(',',' ')}',
#                     '{chofer}','{correoChofer[chofer]}','Reasignado','Reasignado')""")
#         midb.commit()
#         cursor.execute(f"update ViajesFlexs set `Check` = 'En Camino', Chofer = '{chofer}',Correo_chofer='{correoChofer[chofer]}',estado_envio = 'En Camino',Motivo = 'En Camino', Ultimo_motivo = 'En Camino' where Numero_envío = '{nro_envio}'")
#         midb.commit()
#     return "a donde te mando?"