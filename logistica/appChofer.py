
import json
from flask import (
    Blueprint, jsonify, g, redirect, render_template, request, session
)
from werkzeug.security import generate_password_hash,check_password_hash
from threading import Thread
from database import database


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
    midb = database.connect_db()
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
    midb = database.connect_db()
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
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("Select Zona from ViajesFlexs where Numero_envío = %s",(envio,))
    zona = cursor.fetchone()
    if zona == None:
        zona = " No esta en lista "
    else:
        zona = zona[0]
        t = Thread(target=sectorizar, args=(midb,cursor,data,zona))
        t.start()
    return jsonify({"Zona":zona})


@pd.route("/pendientes/<usser>")
def pendientesGET(usser):
    sql = """select V.Numero_envío,V.Direccion,V.Localidad,V.Vendedor,V.Latitud,V.Longitud 
                from ViajesFlexs as V inner join ZonasyChoferes as Z 
                on concat(Z.`nombre Zona`,"/",tipoEnvio) = V.Zona
                where Z.`Nombre Completo` = choferCorreo(%s);"""
    midb = database.connect_db()
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


@pd.route("/cargar",methods=["POST"])
def cargar():
    if True != None:
        return jsonify(success=True,message="Cargado")
    else:
        return jsonify(success=False,message="Zona incorrecta")

@pd.route("/mireparto",methods=["GET","POST"])
def miReparto():
    sql = """select Numero_envío,Direccion,Localidad,Vendedor,Latitud,Longitud from ViajesFlexs 
            where estado_envio in ("En Camino","Reasignado") and Correo_chofer = %s"""
    data = request.get_json()
    usser = data["chofer"]
    midb = database.connect_db()
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
    
@pd.route("/mireparto/<usser>")
def miRepartoGET(usser):
    sql = """select Numero_envío from ViajesFlexs 
            where estado_envio in ("En Camino","Reasignado") and Correo_chofer = %s"""
    midb = database.connect_db()
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