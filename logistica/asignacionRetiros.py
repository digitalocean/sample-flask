from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
from datetime import datetime
from .script import correoChoferes
lgAR = Blueprint('asignacionRetiros', __name__, url_prefix='/')

def actualizarTablas(database):
    levantadas = []
    parte1 = []
    parte2 = []
    clienteChofer = {}
    choferesAsignados = {}
    cotizacion = {}
    cursor = database.cursor()
    cursor.execute("select Vendedor,chofer,cotizacion from levantadas")
    resultado = cursor.fetchall()
    contador = 0
    mitad = len(resultado)/2
    for x in resultado:
        if contador < mitad:
            levantadas.append(x[0])
            parte1.append(x[0])
        else:
            parte2.append(x[0])
        contador +=1
        clienteChofer[x[0]] = x[1]
        choferesAsignados[x[0]] = x[1]
        cotizacion[x[0]] = x[2]
    return levantadas,clienteChofer,cotizacion,parte1,parte2

@lgAR.route("/logistica/asignar/retirodeproductos", methods=["GET","POST"])
@auth.login_required
def retiroDeProductos():
    hoy = str(datetime.now())[0:10]
    midb = database.connect_db()
    levantadas,clienteChofer,cotizacion,parte1,parte2 = actualizarTablas(midb)
    cursor = midb.cursor()
    cursor.execute("SELECT Apodo,Cliente FROM mmslogis_MMSPack.`Apodos y Clientes`;")
    apodoCliente = {}
    for w in cursor.fetchall():
        apodoCliente[w[0]] = w[1]
    hoy = str(datetime.now())[0:10]
    cursor.execute(f"select Vendedor from ViajesFlexs where Fecha = '{hoy}' group by Vendedor")
    vendedores = []
    for z in cursor.fetchall():
        vendor = z[0]
        vend = ""
        if vendor in apodoCliente.keys():
            vendor = apodoCliente[vendor]
        vendedores.append(vendor)
        if not str(vendor).lower() in str(levantadas).lower():
            vend += "('"+str(z[0])+"'),"
            levantadas.append(vendor)
    if vend != "":
        vend = vend[0:-1]
        sql = f"insert ignore into levantadas (vendedor) values {vend}"
        cursor.execute(sql)
        midb.commit()
    print(sql)
    if request.method == "POST":
        for y in request.form.keys():
            chofer = request.form.get(y)
            if chofer == request.form.get("fecha"):
                continue
            if chofer != clienteChofer[y]:
                if str(chofer) == "None":
                    continue 
                if chofer != "null":
                    chofer = f"'{chofer}'"
                sql = f"update mmslogis_MMSPack.levantadas set Chofer = {chofer} where vendedor = '{y}';"
                print(sql)
                cursor.execute(sql)
                midb.commit()
                print(y + " " + chofer)
        levantadaspost,clienteChofer = actualizarTablas(midb)[0:2]
        return render_template("levantadas.html",fecha=hoy,ruta = "confirmarRetiros",boton = "CONFIRMAR LEVANTADAS", vendedores1 = parte1,vendedores2 = parte2,vendedoresHoy = vendedores, choferes =  correoChoferes(midb).keys(),asignados = clienteChofer,auth = session.get("user_auth"))
    return render_template("levantadas.html",fecha=hoy,ruta = "retirodeproductos",boton = "Guardar en tabla temporal", vendedores1 = parte1,vendedores2 = parte2,vendedoresHoy = vendedores, choferes = correoChoferes(midb).keys(),asignados = actualizarTablas(midb)[1],auth = session.get("user_auth"))

@lgAR.route("/logistica/asignar/confirmarRetiros", methods=["GET","POST"])
@auth.login_required
def retiroconfirmadoss():
    midb = database.connect_db()
    cursor = midb.cursor()
    fecha = request.form.get("fecha")
    precio = 0
    costo = 250
    choferesAsignados = ""
    for x in request.form.keys():
        if not str(x) in ["fecha", "None", ""]: 
            chofer = str(request.form.get(x))
            if chofer != "None":
                cotizacion = actualizarTablas(midb)[2]
                localidad = cotizacion[x]
                correoChofer = correoChoferes(midb)[chofer]
                choferesAsignados += f"('Flex a base {x} {str(datetime.now())[0:19]}','{x}','{localidad}','{chofer}','{correoChofer}',{precio},{costo},'{fecha}','Levantada','Modifico: {session.get('user_id')}','Retiro de productos en {x}'),"
    choferesAsignados = choferesAsignados[0:-1]
    sql = f"insert into historial_estados (Numero_envío,Vendedor,Localidad,Chofer,Correo_chofer,Precio,Costo,Fecha,estado_envio,Foto_domicilio,Direccion_completa) values {choferesAsignados}"
    print(sql)
    if choferesAsignados != "":
        cursor.execute(sql)
        midb.commit()
    return redirect("/logistica/asignar/retirodeproductos")

@lgAR.route("/logistica/asignar/limpiarchoferes", methods=["GET","POST"])
@auth.login_required
def limpiarChoferes():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select vendedor from levantadas")
    vendedores = "('"
    for x in cursor.fetchall():
        vendedores += x[0] + "','"
    vendedores = vendedores[0:-2] + ")"
    sql = f"update levantadas set chofer = null where vendedor in {vendedores}"
    cursor.execute(sql)
    midb.commit()
    print(sql)
    hoy = str(datetime.now())[0:10]
    return redirect("/logistica/asignar/retirodeproductos")
