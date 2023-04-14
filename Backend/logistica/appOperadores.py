
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
def scannerIngreso():
    data = request.get_json()
    envio = data["id"]
    chofer = data["chofer"]
    location = data["location"]
    del data["chofer"]
    del data["location"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("SELECT Fecha,estado_envio,Motivo from ViajesFlexs where Numero_envío = %s ",(envio,))
    resultado = cursor.fetchone()
    print(resultado)
    midb.close()
    if resultado == None:
        return jsonify(success=False,message="No esta en lista")
    else:
        estado = resultado[1]
        motivo = resultado[2]
        if estado != "Retirado":
            return jsonify(success=False,message=f"Estado: {estado}, Motivo: {motivo}")
        else:
            return jsonify(success=True,message=f"Envio {envio} ingresado")

        

        
