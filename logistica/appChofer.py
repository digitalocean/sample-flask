
import json
from flask import (
    Blueprint, jsonify, g, redirect, render_template, request, session
)
from werkzeug.security import generate_password_hash,check_password_hash
from threading import Thread
from database import database


pd = Blueprint('pendientes', __name__, url_prefix='/')
def sectorizar(database,cursor,nEnvio):
    cursor.execute("update ViajesFlexs set estado_envio = 'Listo para salir (Sectorizado)', Motivo = null where Numero_envío = %s",(nEnvio,))
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
    # chofer = data["Chofer"]
    # midb = database.connect_db()
    # cursor = midb.cursor()
    # cursor.execute("update ViajesFlexs set estado_envio = 'Retirado' where Numero_envío = %s and estado_envio in ('Lista Para Retirar','Retirado');",(envio,))
    # midb.commit()
    return ""

@pd.route("/sectorizar",methods=["POST"])
def scannerSectorizar():
    data = request.get_json()
    envio = data["id"]
    sender_id = data["sender_id"]
    escanea = data["Chofer"]
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("Select Zona from ViajesFlexs where Numero_envío = %s",(envio,))
    res = cursor.fetchall()[0]
    t = Thread(target=sectorizar, args=(midb,cursor,envio))
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
