from flask import Blueprint, redirect, render_template, request, session
from Backend.auth import auth
from Backend.database import database
from datetime import datetime
from Backend.scriptGeneral import scriptGeneral
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
        levantadas.append(x[0])
        if contador < mitad:
            parte1.append(x[0])
        else:
            parte2.append(x[0])
        contador +=1
        clienteChofer[x[0]] = x[1]
        choferesAsignados[x[0]] = x[1]
        cotizacion[x[0]] = x[2]
    return levantadas,clienteChofer,cotizacion,parte1,parte2

def consultarRetiros(database):
    cursor = database.cursor()
    cursor.execute('SELECT vendedor(Vendedor),count(*) FROM mmslogis_MMSPack.ViajesFlexs where Fecha = current_date() and estado_envio like "%para retirar" group by vendedor(Vendedor);')
    retiros = []
    vendedores = []
    for x in cursor.fetchall():
        retiro = [x[0],x[1]]
        retiros.append(retiro)
        vendedores.append(x[0])
    return retiros,vendedores

@lgAR.route("/logistica/asignar/retirodeproductos", methods=["GET","POST"])
@auth.login_required
def retiroDeProductos():
    hoy = str(datetime.now())[0:10]
    midb = database.connect_db()
    levantadas,clienteChofer,cotizacion,parte1,parte2 = actualizarTablas(midb)
    cursor = midb.cursor()
    """
    # cursor.execute("SELECT Apodo,Cliente FROM mmslogis_MMSPack.`Apodos y Clientes`;")
    # apodoCliente = {}
    # for w in cursor.fetchall():
    #     apodoCliente[w[0]] = w[1]
    # hoy = str(datetime.now())[0:10]
    # cursor.execute(f"select vendedor(Vendedor) from ViajesFlexs where Fecha = '{hoy}' group by vendedor(Vendedor)")
    # vendedores = []
    # vend = ""
    # for z in cursor.fetchall():
    #     vendor = z[0]
    #     vend = ""
    #     if vendor in apodoCliente.keys():
    #         vendor = apodoCliente[vendor]
    #     vendedores.append(vendor)
    #     if not str(vendor).lower() in str(levantadas).lower():
    #         vend += "('"+str(z[0])+"'),"
    #         levantadas.append(vendor)
    # # if vend != "":
    # #     vend = vend[0:-1]
    # #     sql = f"insert ignore into levantadas (vendedor) values {vend}"
    # #     cursor.execute(sql)
    # #     midb.commit()
    """
    retirosHoy,vendedores = consultarRetiros(midb)
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
                cursor.execute(sql)
                midb.commit()
        return render_template("logistica/levantadas.html",
                                fecha=hoy,
                                retirosHoy = retirosHoy,
                                ruta = "confirmarRetiros",
                                boton = "CONFIRMAR LEVANTADAS", 
                                vendedores=levantadas,
                                vendedores1 = parte1,
                                vendedores2 = parte2,
                                vendedoresHoy = vendedores,
                                zonas=["Flex a base caba","Flex a base zona 1"], 
                                choferes =  scriptGeneral.correoChoferes(midb).keys(),
                                asignados = actualizarTablas(midb)[1],
                                auth = session.get("user_auth"))

    return render_template("logistica/levantadas.html",
                            fecha=hoy,
                            ruta = "retirodeproductos",
                            retirosHoy = retirosHoy,
                            boton = "Guardar en tabla temporal",
                            vendedores=levantadas, 
                            vendedores1 = parte1,
                            vendedores2 = parte2,
                            vendedoresHoy = vendedores,
                            zonas=["Flex a base caba","Flex a base zona 1"], 
                            choferes = scriptGeneral.correoChoferes(midb).keys(),
                            asignados = actualizarTablas(midb)[1],
                            auth = session.get("user_auth"))

@lgAR.route("/logistica/asignar/confirmarRetiros", methods=["GET","POST"])
@auth.login_required
def retiroconfirmadoss():
    midb = database.connect_db()
    cursor = midb.cursor()
    levantadas = {}
    levantadas["flex a base ezeiza"] = 2000
    levantadas["flex a base caba"] = 660
    levantadas["flex a base zona 1"] = 1000
    fecha = request.form.get("fecha")
    precio = 0
    choferesAsignados = ""
    for x in request.form.keys():
        if not str(x) in ["fecha", "None", ""]: 
            chofer = str(request.form.get(x))
            if chofer != "None":
                cotizacion = actualizarTablas(midb)[2]
                localidad = cotizacion[x]
                print(localidad)
                correoChofer = scriptGeneral.correoChoferes(midb)[chofer]
                choferesAsignados += f"('Flex a base {x} {str(datetime.now())[0:19]}','{x}','{localidad}','{chofer}','{correoChofer}',{precio},{levantadas[str(localidad).lower()]},'{fecha}','Levantada','Modifico: {session.get('user_id')}','Retiro de productos en {x}'),"
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
    return redirect("/logistica/asignar/retirodeproductos")

@lgAR.route("/logistica/asignar/retirodeproductos/nuevalevantada", methods = ["GET","POST"])
@auth.login_required
def agregarLevantada():
    midb = database.connect_db()
    cursor = midb.cursor()
    vendedor = request.form.get("nuevoVendedor")
    zona = request.form.get("zona")
    cursor.execute("insert into levantadas (vendedor,cotizacion) values(%s,%s)",(vendedor,zona))
    midb.commit()
    return redirect("/logistica/asignar/retirodeproductos")


@lgAR.route("/logistica/asignar/retirodeproductos/eliminarlevantada", methods = ["GET","POST"])
@auth.login_required
def borrarLevantada():
    vendedor = request.form.get("borrarVendedor")
    midb = database.connect_db()
    cursor = midb.cursor()
    sql = f"delete from levantadas where vendedor = '{vendedor}'"
    print(sql)
    cursor.execute(sql)
    midb.commit()
    return redirect("/logistica/asignar/retirodeproductos")