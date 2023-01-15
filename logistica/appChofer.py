
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash,check_password_hash
from threading import Thread
from database.database import connect_db
from datetime import datetime,timedelta
from logistica.Envio import Envio

pd = Blueprint('pendientes', __name__, url_prefix='/')


@pd.route("/retirado",methods=["POST"])
def algo():
    return "JOSUGATO"


@pd.route("/api/users/login",methods=["POST"])
def loginEmpleado():
    dataLogin = request.get_json()
    usser = dataLogin["ussername"]
    password = dataLogin["password"]
    print(usser," ",password)
    midb = connect_db()
    cursor = midb.cursor()
    sql ="""
    SELECT 
        `empleado`.`id`
    FROM 
        `mmslogis_MMSPack`.`empleado` where correo = %s and dni = %s;
    """
    cursor.execute(sql,(usser,password))
    res = cursor.fetchone()
    midb.close()
    if res != None:
        return jsonify(success=True,message="Inicio de sesion correcto",data=res)
    else:
        return jsonify(success=False,message="password invalid",data=None)


@pd.route("/retirar",methods=["POST"])
def scannerRetirar():
    data = request.get_json()
    envio = data["id"]
    sender_id = data["sender_id"]
    chofer = data["chofer"]
    print(envio)
    print(sender_id)
    print(chofer)
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("insert into retirado(fecha,hora,Numero_envío,chofer,estado,scanner) values(DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),%s,%s,'Retirado',%s);",(envio,chofer,str(data)))
    midb.commit()
    midb.close()
    return ""

def sectorizar(database,cursor,data,zona):
    nenvio = data["id"]
    try:
        chofer = data["chofer"]
    except:
        chofer = data["Chofer"]
    print(zona,nenvio,str(data),chofer)
    cursor.execute(
        """INSERT INTO `mmslogis_MMSPack`.`sectorizado`
                (`id`,`zona`,`fecha`,`hora`,`Numero_envío`,`scanner`,`chofer`)
            VALUES
                (UUID(),%s,DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                ,%s,%s,%s);""",(zona,nenvio,str(data),chofer))

    database.commit()
    database.close()

@pd.route("/sectorizar",methods=["POST"])
def scannerSectorizar():
    data = request.get_json()
    print(data)
    envio = data["id"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("Select Zona from ViajesFlexs where Numero_envío = %s",(envio,))
    zona = cursor.fetchone()
    midb.close()
    if zona == None:
        zona = " No esta en lista "
    else:
        zona = zona[0]
        t = Thread(target=sectorizar, args=(connect_db(),cursor,data,zona))
        t.start()
    return jsonify({"Zona":zona})


@pd.route("/pendientes/<usser>")
def pendientesGET(usser):
    sql = """select V.Numero_envío from ViajesFlexs as V inner join ZonasyChoferes as Z 
                on concat(Z.`nombre Zona`,"/",tipoEnvio) = V.Zona
                where Z.`Nombre Completo` = choferCorreo(%s) and V.estado_envio in ("Lista Para Retirar","Retirado","Listo para salir (Sectorizado)");"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(usser,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        envios.append(x[0])
    return jsonify(envios)

@pd.route("/carga",methods=["POST"])
def cargar():
    data = request.get_json()
    nenvio = data["id"]
    chofer = data["chofer"]
    statusOK = False
    message = ""
    try:
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(
            """INSERT INTO `mmslogis_MMSPack`.`en_camino`
                    (`id`,`fecha`,`hora`,`Numero_envío`,`chofer`,`scanner`)
                VALUES
                    (UUID(),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                    ,%s,%s,%s);""",(nenvio,chofer,str(data)))
        midb.commit()
        midb.close()
        statusOK = True
        message = "Cargado"
    except Exception as err:
        print(err)
        statusOK = False
        message = err
    return jsonify(success=statusOK,message=message,envio=nenvio)

@pd.route("/mireparto",methods=["GET","POST"])
def miReparto():
    sql = """select Numero_envío,Direccion,Localidad,Vendedor,Latitud,Longitud from ViajesFlexs 
            where estado_envio in ("En Camino","Reasignado") and Correo_chofer = %s"""
    data = request.get_json()
    usser = data["chofer"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(usser,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        nEnvio = x[0]
        dirCompleta = f"{x[1]}, {x[2]}"
        vendedor = x[3]
        latitud = x[4]
        longitud = x[5]
        data = {"nEnvio":nEnvio,"direccion":dirCompleta,"vendedor":vendedor,"latitud":latitud,"longitud":longitud}
        envios.append(data)
    return jsonify(envios)
    
@pd.route("/mireparto/<usser>")
def miRepartoGET(usser):
    sql = """select Numero_envío,Direccion,Localidad,Vendedor,Latitud,Longitud from ViajesFlexs 
            where estado_envio in ("En Camino","Reasignado") and Correo_chofer = %s"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(usser,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        nEnvio = x[0]
        dirCompleta = f"{x[1]}, {x[2]}"
        vendedor = x[3]
        latitud = x[4]
        longitud = x[5]
        data = {"nEnvio":nEnvio,"direccion":dirCompleta,"vendedor":vendedor,"Latitud":latitud,"Longitud":longitud}
        envios.append(data)
    return jsonify(envios)

@pd.route("/entregado",methods=["POST"])
def entregado():
    data = request.get_json()
    print(data)
    nroEnvio = data["nEnvio"]
    chofer = data["chofer"]
    sql = """
        update ViajesFlexs set 
        `Check` = null,
        estado_envio = "Entregado",
        Motivo = "Entregado sin novedades",
        Chofer = choferCorreo(%s),
        Correo_chofer = %s,
        Timechangestamp = %s,
        Currentlocation = %s
        where Numero_envío = %s
        """
    values = (chofer,chofer,datetime.now()-timedelta(hours=3),"ubicacion pendiente",nroEnvio)
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return jsonify(success=True,message="Envio Entregado",envio=nroEnvio)

@pd.route("/noentregado",methods=["POST"])
def noEntregado():
    data = request.get_json()
    nroEnvio = data["nEnvio"]
    chofer = data["chofer"]
    print(data)
    return jsonify(success=False,message="Todavia no esta lista esta seccion",envio=nroEnvio)