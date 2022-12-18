from database import database
from auth import auth
from flask import (
    Blueprint, g, render_template, request, session,redirect
)
from scriptGeneral import scriptGeneral
pr = Blueprint('precios', __name__, url_prefix='/')

def obtenerIdTarifas(db):
    cursor = db.cursor()
    cursor.execute("select idTarifa from tarifa group by idTarifa")
    tarifas = []
    for x in cursor.fetchall():
        tarifas.append(x[0])
    return tarifas

def obtenerTarifaPorCliente(db):
    cursor = db.cursor()
    cursor.execute("select C.nombre_cliente,T.idTarifa from Clientes as C inner join tarifa as T on idClientes = id_cliente order by C.nombre_cliente;")
    clienteTarifa = []
    for x in cursor.fetchall():
        paq = [x[0],x[1]]
        clienteTarifa.append(paq)
    return clienteTarifa

def obtenerPrecios(tarifa,db):
    """Devuelve SUBlistas de 4 elementos
        nombre de la zona,
        precio de la zona,
        id tarifa,
        id zona
    """
    cursor = db.cursor()
    sql = f"select Z.nombre,ZP.precio,I.id_tarifa,I.id_zona from zona as Z join indicePrecio as I on Z.id = I.id_zona join zonaTarifaPrecio as ZP on I.id_zona = ZP.id_zona and ZP.id_tarifa = {tarifa} group by Z.nombre"
    cursor.execute(sql)
    zonas = []
    for x in cursor.fetchall():
        zona = [x[0],x[1],x[2],x[3]]
        zonas.append(zona)
    return zonas

def obtenerZonas(tarifa,db):
    cursor = db.cursor()
    cursor.execute(f"select L.localidad,Z.nombre from localidad as L join indicePrecio as I on L.id = I.id_localidad and I.id_tarifa = {tarifa} join zona as Z on I.id_zona = Z.id union select localidad,'Sin asignar' from localidad where not id in (select L.id from localidad as L join indicePrecio as I on L.id = I.id_localidad and I.id_tarifa = {tarifa} join zona as Z on I.id_zona = Z.id)")
    localidades = []
    for x in cursor.fetchall():
        localidades.append(x)
    return localidades

def obtenerZonasId(db):
    cursor = db.cursor()
    cursor.execute(f"select id,nombre from zona")
    zonas = []
    for x in cursor.fetchall():
        zonas.append(x)
    return zonas


@pr.route('/facturacion/verprecio', methods=["GET","POST"])
@auth.login_required
@auth.admin_required
def consultarPrecio():
    midb = database.connect_db()
    if request.method == "POST":
        tarifa = request.form["tarifa"]
        return render_template("facturacion/tarifas.html",
                                localidades = obtenerZonas(tarifa,midb),
                                zonas = obtenerZonasId(midb),
                                precios=obtenerPrecios(tarifa,midb),
                                cant_columnas = 2,
                                tarifa=tarifa,
                                tarifas=obtenerIdTarifas(midb),
                                auth = session.get("user_auth"))
    else:
        return render_template("facturacion/tarifas.html",
                                localidades = obtenerZonas("1",midb),
                                zonas = obtenerZonasId(midb),
                                precios=obtenerPrecios("1",midb),
                                clientes = obtenerTarifaPorCliente(midb),
                                tarifa = "1",
                                cant_columnas = 2,
                                tarifas=obtenerIdTarifas(midb),
                                auth = session.get("user_auth"))

@pr.route('facturacion/cambioprecio/', methods=["POST","GET"])
@auth.login_required
def cambiarprecio():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "POST":
        tarifa = request.form["tarifa"]
        zonaCambia = request.form["zona"]
        nuevoprecio = request.form["nuevoprecio"]
        sql = f"update zonaTarifaPrecio set precio = {nuevoprecio} where id_tarifa = {tarifa} and id_zona = {zonaCambia}"
        print(sql)
        cursor.execute(sql)
        midb.commit()
        return render_template("facturacion/tarifas.html",
                                precios=obtenerPrecios(tarifa,midb),
                                zonas = obtenerZonasId(midb),
                                cant_columnas = 2,
                                tarifa=tarifa,
                                tarifas=obtenerIdTarifas(midb),
                                localidades = obtenerZonas(tarifa,midb),
                                auth = session.get("user_auth"))


@pr.route("/facturacion/cambiolocalidadzona",methods=["POST"])
@auth.login_required
def cambioLocalidadZona():
    # tarifa = request.form["tarifa"]
    for x in request.form.keys():
        print(f"{x} : {request.form[x]}")
    # midb = database.connect_db()
    # cursor = midb.cursor()
    # cursor.execute(f"select L.localidad,Z.nombre from localidad as L inner join indicePrecio as IP on L.id = IP.id_localidad inner join zona as Z on IP.id_zona = Z.id where IP.id_tarifa = {tarifa};")
    # for x in cursor.fetchall():
    #     if request.form[x[0]] != x[1]:
    #         sql = f"update indicePrecio as IP inner join localidad as L on IP.id_localidad = L.id inner join zona as Z on L.localidad = Z.nombre set IP.id_zona = (select id from zona where nombre = '{request.form[x[0]]}') where IP.id_tarifa = {tarifa} and L.localidad = '{x[0]}'"
    #         print(sql)
    #         cursor.execute(sql)
    #         midb.commit()
    return render_template("facturacion/tarifas.html",
                            # precios=obtenerPrecios(tarifa,midb),
                            # zonas = obtenerZonasId(midb),
                            # cant_columnas = 2,
                            # tarifa=tarifa,
                            # tarifas=obtenerIdTarifas(midb),
                            # localidades = obtenerZonas(tarifa,midb),
                            auth = session.get("user_auth"))