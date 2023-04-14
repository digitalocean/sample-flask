
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
    
@OPLG.route("/operadores/ingreso",methods=["POST"])
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
