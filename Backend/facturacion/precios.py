from Backend.database import database
from Backend.auth import auth
from flask import Blueprint, g, render_template, request, session,redirect
from threading import Thread
pr = Blueprint('precios', __name__, url_prefix='/')

def obtenerIdTarifas(db):
    cursor = db.cursor()
    cursor.execute("select id,nombre from tarifa")
    tarifas = []
    for x in cursor.fetchall():
        tarifas.append([x[0],x[1]])
    return tarifas

def obtenerTarifaPorCliente(db):
    cursor = db.cursor()
    cursor.execute("""
                    select C.nombre_cliente,t.nombre
                    from Clientes as C 
                    inner join tarifaCliente as T 
                    on C.idClientes = T.id_cliente 
                    inner join tarifa as t on t.id = T.idTarifa where Fecha_Baja is null order by t.id;
                    """)
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
    sql = f"select Z.nombre,ZP.precio,I.id_tarifa,I.id_zona from zona as Z left join indicePrecio as I on Z.id = I.id_zona left join zonaTarifaPrecio as ZP on I.id_zona = ZP.id_zona and ZP.id_tarifa = {tarifa} group by Z.nombre"
    cursor.execute(sql)
    zonas = []
    for x in cursor.fetchall():
        zona = [x[0],x[1],x[2],x[3]]
        zonas.append(zona)
    return zonas

def obtenerZonas(tarifa,db):
    cursor = db.cursor()
    cursor.execute(f"""select L.localidad,Z.nombre,L.id,P.partido 
                        from localidad as L 
                        inner join localidadCpPartido as LCP  
                        on L.id = LCP.localidad 
                        inner join partido as P
                        on LCP.partido = P.id
                        left join indicePrecio as I 
                        on L.id = I.id_localidad and I.id_tarifa = {tarifa}
                        left join zona as Z on I.id_zona = Z.id 
                        group by L.localidad
                        order by LCP.partido,Z.nombre, L.localidad """)
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

def obtenerPartidos(db):
    cursor = db.cursor()
    cursor.execute("select * from partido order by partido")
    partidos = list(cursor.fetchall())
    return partidos

def nuevaTarifaThread(nuevatarifa):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select id,id_tarifa,id_localidad,id_tipoEnvio,id_zona from indicePrecio where id_tarifa = 1")
    for x in cursor.fetchall():
        sql = f"""
        insert ignore into indicePrecio(
            id,
            id_tarifa,
            id_localidad,
            id_tipoEnvio,
            id_zona
            ) 
            values(
                "{nuevatarifa}-{x[2]}-{x[3]}",
                {nuevatarifa},
                {x[2]},
                {x[3]},
                {x[4]})"""
        cursor.execute(sql)
        midb.commit()
    midb.close()

@pr.route('/facturacion/verprecio', methods=["GET","POST"])
@auth.login_required
def consultarPrecio():
    midb = database.connect_db()
    if request.method == "POST":
        tarifa = request.form["tarifa"]
        return render_template("facturacion/tarifas.html",
                                localidades = obtenerZonas(tarifa,midb),
                                zonas = obtenerZonasId(midb),
                                precios=obtenerPrecios(tarifa,midb),
                                cant_columnas = 2,
                                clientes = obtenerTarifaPorCliente(midb),
                                tarifa=tarifa,
                                tarifas=obtenerIdTarifas(midb),
                                auth = session.get("user_auth"))
    else:
        return render_template("facturacion/tarifas.html",
                                localidades = obtenerZonas("1",midb),
                                partidos = obtenerPartidos(midb),
                                zonas = obtenerZonasId(midb),
                                precios=obtenerPrecios("1",midb),
                                clientes = obtenerTarifaPorCliente(midb),
                                tarifa = "1",
                                cant_columnas = 2,
                                tarifas=obtenerIdTarifas(midb),
                                auth = session.get("user_auth"))

@pr.route('/facturacion/cambioprecio/', methods=["POST","GET"])
@auth.login_required
@auth.admin_required
def cambiarprecio():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "POST":
        tarifa = request.form["tarifa"]
        zonaCambia = request.form["zona"]
        nuevoprecio = request.form["nuevoprecio"]
        nuevoprecio = float(str(nuevoprecio).replace(",","."))
        sql = f"update zonaTarifaPrecio set precio = {nuevoprecio} where id_tarifa = {tarifa} and id_zona = {zonaCambia}"
        # sql = f"INSERT IGNORE INTO zonaTarifaPrecio (id_tarifa, id_zona, precio) VALUES ({tarifa}, {zonaCambia}, {nuevoprecio}) ON DUPLICATE KEY UPDATE precio = {nuevoprecio};"
        print(sql)
        cursor.execute(sql)
        midb.commit()
        return render_template("facturacion/tarifas.html",
                                precios=obtenerPrecios(tarifa,midb),
                                zonas = obtenerZonasId(midb),
                                cant_columnas = 2,
                                tarifa=tarifa,
                                clientes = obtenerTarifaPorCliente(midb),
                                tarifas=obtenerIdTarifas(midb),
                                localidades = obtenerZonas(tarifa,midb),
                                auth = session.get("user_auth"))
    
@pr.route('/facturacion/nuevoprecio/', methods=["POST","GET"])
@auth.login_required
@auth.admin_required
def nuevoPrecio():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "POST":
        tarifa = request.form["tarifa"]
        zonaCambia = request.form["zona"]
        nuevoprecio = request.form["nuevoprecio"]
        nuevoprecio = float(str(nuevoprecio).replace(",","."))
        # sql = f"update zonaTarifaPrecio set precio = {nuevoprecio} where id_tarifa = {tarifa} and id_zona = {zonaCambia}"
        sql = f"INSERT IGNORE INTO zonaTarifaPrecio (id_tarifa, id_zona, precio) VALUES ({tarifa}, {zonaCambia}, {nuevoprecio}) ON DUPLICATE KEY UPDATE precio = {nuevoprecio};"
        print(sql)
        cursor.execute(sql)
        midb.commit()
        return render_template("facturacion/tarifas.html",
                                precios=obtenerPrecios(tarifa,midb),
                                zonas = obtenerZonasId(midb),
                                cant_columnas = 2,
                                tarifa=tarifa,
                                clientes = obtenerTarifaPorCliente(midb),
                                tarifas=obtenerIdTarifas(midb),
                                localidades = obtenerZonas(tarifa,midb),
                                auth = session.get("user_auth"))


@pr.route("/facturacion/cambiolocalidadzona",methods=["POST"])
@auth.login_required
@auth.admin_required
def cambioLocalidadZona():
    idTarifa = request.form["tarifa"]
    idLocalidad = request.form["localidad"]
    idZona = request.form["zona"]
    idTipoEnvio = 2
    # id = f"{idTarifa},"
    sql = """
    insert ignore into indicePrecio 
        (id,id_tarifa,id_localidad,id_tipoEnvio,id_zona)
    values
        (concat(%s,"-",%s,"-",%s),%s,%s,%s,%s) 
    ON DUPLICATE KEY UPDATE    
        id_tarifa = %s,id_localidad = %s,id_tipoEnvio = %s,id_zona = %s;"""

    values = (idTarifa,idLocalidad,idTipoEnvio,idTarifa,idLocalidad,idTipoEnvio,idZona,idTarifa,idLocalidad,idTipoEnvio,idZona)
    print(sql % values)
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    return render_template("facturacion/tarifas.html",
                            precios=obtenerPrecios(idTarifa,midb),
                            zonas = obtenerZonasId(midb),
                            cant_columnas = 2,
                            clientes = obtenerTarifaPorCliente(midb),
                            tarifa=idTarifa,
                            tarifas=obtenerIdTarifas(midb),
                            localidades = obtenerZonas(idTarifa,midb),
                            auth = session.get("user_auth"))


@pr.route("/facturacion/nuevalocalidad",methods=["POST"])
@auth.login_required
@auth.admin_required
def nuevaLocalidad():
    localidad = request.form["nombreLocalidad"]
    partido = request.form["nombrePartido"]
    cp = request.form["CP"]
    midb = database.connect_db()
    cursor = midb.cursor()
    midb.start_transaction()
    try:
        cursor.execute("insert into localidad (localidad) values(%s)",(localidad,))
        idLocalidad = cursor.lastrowid
        cursor.execute("insert into localidadCpPartido (localidad,cp,partido) values(%s,%s,%s)",(idLocalidad,cp,partido))
        midb.commit()
    except Exception as e:
        print(e)
        midb.rollback()
    midb.close()
    return redirect("/facturacion/verprecio")


@pr.route("/facturacion/nuevatarifa",methods=["POST"])
@auth.login_required
@auth.admin_required
def nuevaTarifa():
    nombreTarifa = request.form["nombreTarifa"]
    midb = database.connect_db()
    cursor = midb.cursor()
    try:
        cursor.execute("insert into tarifa (nombre) values (%s)",(nombreTarifa,))
        idTarifa = cursor.lastrowid
        cursor.execute("insert into zonaTarifaPrecio (id_tarifa,id_zona) values(%s,1),(%s,2),(%s,3),(%s,4)",(idTarifa,idTarifa,idTarifa,idTarifa))
        midb.commit()
        tarifaNueva = Thread(target=nuevaTarifaThread, args=(idTarifa,))
        tarifaNueva.start()
    except Exception as e:
        print(e)
        midb.rollback()
    midb.close()
    return redirect("/facturacion/verprecio")
