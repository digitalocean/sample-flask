
from flask import Blueprint, jsonify, request,send_file,redirect
from threading import Thread
import requests
from Backend.database.database import connect_db
from datetime import datetime,timedelta

OPLG = Blueprint('operadoresLogisticos', __name__, url_prefix='/')


@OPLG.route("/api/admin/login",methods=["POST"])
def loginAdmin():
    dataLogin = request.get_json()
    usser = dataLogin["ussername"]
    password = dataLogin["password"]
    print(usser," ",password)
    midb = connect_db()
    cursor = midb.cursor()
    sql ="""
    SELECT 
        `nickname`
    FROM 
        `mmslogis_MMSPack`.`usuario` where nickname= %s and password = %s;
    """
    cursor.execute(sql,(usser,password))
    res = cursor.fetchone()
    midb.close()
    if res != None:
        return jsonify(success=True,message="Inicio de sesion correcto",data=res)
    else:
        return jsonify(success=False,message="password invalid",data=None)

@OPLG.route("/retirado",methods=["POST"])
def enviosRetirados():
    sql = """select V.Numero_envío,V.Comprador,V.Telefono,V.Direccion,V.Localidad,V.Vendedor,V.Latitud,V.Longitud,V.tipo_envio,choferCorreo(R.chofer),R.fecha from retirado as R inner join ViajesFlexs as V on R.Numero_envío = V.Numero_envío"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    envios = []
    for x in result:
        nEnvio = x[0]
        comprador = x[1]
        telefono = x[2]
        dirCompleta = f"{x[3]}, {x[4]}"
        vendedor = x[5]
        latitud = x[6]
        longitud = x[7]
        tipoEnvio = x[8]
        chofer = x[9]
        fecha = x[10]
        data = {"nEnvio":nEnvio,"comprador":comprador,"telefono":telefono,"direccion":dirCompleta,"vendedor":vendedor,"Latitud":latitud,"Longitud":longitud,"tipoEnvio":tipoEnvio,"chofer":chofer,"fecha":fecha}
        envios.append(data)
    return jsonify(envios)

def hiloRetirar(_midb,_cursor,_envio,_chofer,_data,_location):
    _cursor.execute("""insert into retirado
                            (fecha,hora,Numero_envío,chofer,estado,scanner,Currentlocation) 
                            values(
                                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                                %s,
                                %s,
                                'Retirado',
                                %s,
                                %s);""",
                                (_envio,_chofer,str(_data),_location))
    _midb.commit()
    _midb.close()
    
@OPLG.route("/retirar",methods=["POST"])
def scannerRetirar():
    data = request.get_json()
    envio = data["id"]
    chofer = data["chofer"]
    location = data["location"]
    del data["chofer"]
    del data["location"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("SELECT fecha,choferCorreo(chofer) from retirado where Numero_envío = %s limit 1",(envio,))
    resultado = cursor.fetchone()
    print(resultado)
    if resultado == None:
        t = Thread(target=hiloRetirar, args=(midb,cursor,envio,chofer,data,location))
        t.start()
        return jsonify(success=True,message="Retirado")
    else:
        midb.close()
        return jsonify(success=False,message=f"Ya retirador por {resultado[1]} el {resultado[0]}")

def sectorizar(database,data,zona):
    nenvio = data["id"]
    chofer = data["chofer"]
    location = data["location"]
    del data["chofer"]
    del data["location"]

    cursor = database.cursor()
    cursor.execute(
        """INSERT INTO `mmslogis_MMSPack`.`sectorizado`
                (`id`,`zona`,`fecha`,`hora`,`Numero_envío`,`scanner`,`chofer`,Currentlocation)
            VALUES
                (UUID(),
                %s,
                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                %s,
                %s,
                %s,
                %s);""",(zona,nenvio,str(data),chofer,location))

    database.commit()
    database.close()

@OPLG.route("/sectorizar",methods=["POST"])
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
        t = Thread(target=sectorizar, args=(connect_db(),data,zona))
        t.start()
    return jsonify({"Zona":zona})

@OPLG.route("/pendienteschofer",methods=["POST"])
def pendientesChofer():
    data = request.get_json()
    chofer = data["chofer"]
    sql = """select V.Numero_envío from ViajesFlexs as V inner join ZonasyChoferes as Z 
                on concat(Z.`nombre Zona`,"/",tipoEnvio) = V.Zona
                where Z.`Nombre Completo` = choferCorreo(%s) and V.estado_envio in ("Lista Para Retirar","Retirado","Listo para salir (Sectorizado)");"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(chofer,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        envios.append(x[0])
    return jsonify(envios)

@OPLG.route("/pendienteschofer2",methods=["POST"])
def pendientesChofer2():
    data = request.get_json()
    chofer = data["chofer"]
    sql = """select V.Numero_envío,V.Comprador,V.Telefono,V.Direccion,V.Localidad,V.Vendedor,V.Latitud,V.Longitud,V.tipo_envio,V.Chofer,V.Fecha from ViajesFlexs as V inner join ZonasyChoferes as Z 
                on concat(Z.`nombre Zona`,"/",tipoEnvio) = V.Zona
                where Z.`Nombre Completo` = choferCorreo(%s) and V.estado_envio in ("Lista Para Retirar","Retirado","Listo para salir (Sectorizado)");"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(chofer,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        nEnvio = x[0]
        comprador = x[1]
        telefono = x[2]
        dirCompleta = f"{x[3]}, {x[4]}"
        vendedor = x[5]
        latitud = x[6]
        longitud = x[7]
        tipoEnvio = x[8]
        chofer = x[9]
        fecha = x[10]
        data = {"nEnvio":nEnvio,"comprador":comprador,"telefono":telefono,"direccion":dirCompleta,"vendedor":vendedor,"Latitud":latitud,"Longitud":longitud,"tipoEnvio":tipoEnvio,"chofer":chofer,"fecha":fecha}
        envios.append(data)
    return jsonify(envios)

@OPLG.route("/carga",methods=["POST"])
def cargar():
    data = request.get_json()
    nenvio = data["id"]
    chofer = data["chofer"]
    latlong = data["location"]
    status = False
    message = ""
    try:
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(
            """INSERT INTO `mmslogis_MMSPack`.`en_camino`
                    (`id`,`fecha`,`hora`,`Numero_envío`,`chofer`,`scanner`,Currentlocation)
                VALUES
                    (UUID(),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                    ,%s,%s,%s,%s);""",(nenvio,chofer,str(data),latlong))
        midb.commit()
        midb.close()
        status = True
        message = "Cargado"
    except Exception as err:
        print(err)
        status = False
        message = err
    return jsonify(success=status,message=message,envio=nenvio)
  
@OPLG.route("/mireparto/<usser>")
def miReparto(usser):
    sql = """select Numero_envío,Comprador,Telefono,Direccion,Localidad,Vendedor,Latitud,Longitud,tipo_envio,Chofer,Fecha from ViajesFlexs 
            where estado_envio in ("En Camino","Reasignado") and Correo_chofer = %s"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(usser,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        nEnvio = x[0]
        comprador = x[1]
        telefono = x[2]
        dirCompleta = f"{x[3]}, {x[4]}"
        vendedor = x[5]
        latitud = x[6]
        longitud = x[7]
        tipoEnvio = x[8]
        chofer = x[9]
        fecha = x[10]
        data = {"nEnvio":nEnvio,"comprador":comprador,"telefono":telefono,"direccion":dirCompleta,"vendedor":vendedor,"Latitud":latitud,"Longitud":longitud,"tipoEnvio":tipoEnvio,"chofer":chofer,"fecha":fecha}
        envios.append(data)
    return jsonify(envios)
