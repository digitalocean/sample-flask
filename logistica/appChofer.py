
import json
from flask import (
    Blueprint, jsonify, g, redirect, render_template, request, session
)
from werkzeug.security import generate_password_hash,check_password_hash
from threading import Thread
from database import database


pd = Blueprint('pendientes', __name__, url_prefix='/')
def sectorizar(database,cursor,data,zona):
    nenvio = data["id"]
    chofer = data["chofer"]
    print(zona,nenvio,str(data),chofer)
    cursor.execute(
        """INSERT INTO `mmslogis_MMSPack`.`sectorizado`
                (`id`,`zona`,`fecha`,`hora`,`Numero_envío`,`scanner`,`chofer`)
            VALUES
                (UUID(),%s,DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                ,%s,%s,%s);""",(zona,nenvio,str(data),chofer))

    database.commit()
    database.close()

@pd.route("/retirado",methods=["POST"])
def algo():
    return "JOSUGATO"

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

@pd.route("/sectorizar",methods=["POST"])
def scannerSectorizar():
    data = request.get_json()
    envio = data["id"]
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("Select Zona from ViajesFlexs where Numero_envío = %s",(envio,))
    res = cursor.fetchall()[0]
    t = Thread(target=sectorizar, args=(midb,cursor,data,res[0]))
    t.start()
    return jsonify({"Zona":res})

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
        `empleado`.`nombre`,
        `empleado`.`dni`
    FROM 
        `mmslogis_MMSPack`.`empleado` where correo = %s and dni = %s;
"""

    cursor.execute(sql,(usser,password))
    res = cursor.fetchone()
    midb.close()
    print(res)
    if res != None:
        return jsonify(success=True,message="Inicio de sesion correcto",data=res)
    else:
        return jsonify(success=False,message="password invalid",data=None)
