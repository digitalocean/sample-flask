
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
    

@OPLG.route("/operadores/consultaempleados",methods=["POST"])
def consultaEmpleado():
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select id,nombre,correo from empleado where Fecha_Baja is null")
    empleados = []
    for x in cursor.fetchall():
        empleado = {"id":x[0],"nombre":x[1],"correo":x[2]}
        empleados.append(empleado)
    return jsonify(empleados)

@OPLG.route("/operadores/ingreso",methods=["POST"])
def scannerIngreso():
    data = request.get_json()
    print(data)
    envio = data["id"]
    operador = data["operador"]
    chofer = data["chofer"]
    location = data["location"]
    del data["operador"]
    del data["chofer"]
    del data["location"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("SELECT Fecha,estado_envio,Motivo from ViajesFlexs where Numero_envío = %s ",(envio,))
    resultado = cursor.fetchone()
    print(resultado)
    
    if resultado == None:
        values = (envio,operador,chofer,"NO ESTA EN LISTA",str(data),location)
        cursor.execute("""insert into ingresado 
                        (Numero_envío,operador,chofer,estado,scanner,Currentlocation)
                        values (%s,%s,%s,%s,%s,%s);""",values)
        midb.commit()
        midb.close()
        return jsonify(success=False,message="No esta en lista")
    else:
        estado = resultado[1]
        motivo = resultado[2]
        values = (envio,operador,chofer,f"Estado: {estado}, Motivo: {motivo}",str(data),location)
        cursor.execute("""insert into ingresado 
                        (Numero_envío,operador,chofer,estado,scanner,Currentlocation)
                        values (%s,%s,%s,%s,%s,%s);""",values)
        midb.commit()
        midb.close()
        if estado != "Retirado":
            return jsonify(success=False,message=f"Estado: {estado}, Motivo: {motivo}")
        else:
            return jsonify(success=True,message=f"Envio {envio} ingresado")

        
def sectorizar(database,data,zona):
    nenvio = data["id"]
    chofer = data["operador"]
    location = data["location"]
    del data["operador"]
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

@OPLG.route("/operadores/sectorizar",methods=["POST"])
def scannerSectorizar():
    data = request.get_json()
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

