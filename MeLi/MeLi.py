#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8
from threading import Thread
from database import database
from flask import Blueprint, render_template, redirect, request
import requests

from MeLi.consultar_envio import consultar_envio
from informeErrores import informeErrores
ML = Blueprint('MeLi', __name__, url_prefix='/')

@ML.route("/callbacks", methods=["GET","POST"])
def vinculacion():
    if request.method == "POST":
        return redirect("https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=4857198121733101&redirect_uri=https://whale-app-suwmc.ondigitalocean.app/callbacks")
    else:
        data = request.args
        code = data["code"]
        # state = data["state"]
        data2={"grant_type":"authorization_code",
                "client_id":"4857198121733101",
                "code":code,
                "client_secret":"LHTeBl8PL4BXCk4f6v5jvbokxP04hOli",
                "redirect_uri":"https://whale-app-suwmc.ondigitalocean.app/callbacks"
                }
        r = requests.post("https://api.mercadolibre.com/oauth/token", data2).json()
        if "user_id" in r.keys():
            user_id = r["user_id"]
            info = set(requests.get("https://api.mercadolibre.com/users/"+str(user_id)))
            nickname = str(user_id)
            for infoML in info:
                if "nickname" in str(infoML):
                    nickname = ((str(infoML).split(",")[1]).split(":")[1]).replace('"','')
            access_token = r["access_token"]
            refresh_token = r["refresh_token"]
            midb = database.connect_db()
            cursor = midb.cursor()    
            try:
                sql = f"""insert into vinculacion 
                            (nickname,user_id,access_token,refresh_token) 
                        values
                            ('{nickname}','{user_id}','{access_token}','{refresh_token}')
                        ON DUPLICATE KEY UPDATE    
                            user_id={user_id}, nickname = '{nickname}',
                            access_token = '{access_token}',refresh_token = '{refresh_token}';"""

                cursor.execute(sql)
                midb.commit()
            except Exception as err:
                informeErrores.reporte(err," /callbacks")
            sql = f"""insert ignore into `Apodos y Clientes` (Apodo,sender_id) values('{nickname}',{user_id})
                         ON DUPLICATE KEY UPDATE    
                         sender_id={user_id}, Apodo = '{nickname}';"""
            cursor.execute(sql)
            midb.commit()
            midb.close()
                
        return "Bienvenido a MMSPACK, La vinculacion se realizo correctamente"

enviosDic = {}
def procesarNotificacion(data):
    nros_envios = []
    midb = database.connect_db()
    cursor = midb.cursor()
    if len(enviosDic.keys()) < 2: sqlEnvios = "select Numero_envío,estado_envio from ViajesFlexs" 
    else: sqlEnvios = f"select Numero_envío,estado_envio from ViajesFlexs where not Numero_envío in {tuple(enviosDic.keys())};"
    cursor.execute(sqlEnvios)
    envios = cursor.fetchall()
    midb.close()
    for x in envios:
        enviosDic[x[0]] = x[1]
        print(x)
    resource = data.get("resource")
    user_id = data.get("user_id")
    topic = data.get("topic")
    received = data.get("received")
    attempts = data.get("attempts")
    application_id = data.get("application_id")
    sent = data.get("sent")
    if str(topic) == "shipments":
        nro_envio = (resource.split("/"))[2]
        viaje = consultar_envio(nro_envio, user_id)
        if viaje != None:
            tipo_envio= viaje[1] 
            direccion= viaje[2] 
            localidad= viaje[3] 
            referencia= str(viaje[4]).replace("'"," ")
            estado = viaje[5]
            if estado == "ready_to_ship":
                estado = "Listo para Retirar"
            comprador = viaje[6]
            fecha_creacion = viaje[7]
            nro_venta = viaje[8]
            direccion_concatenada = direccion + ", " + localidad + ", Buenos aires"
            if tipo_envio == "self_service" and str(nro_envio) not in nros_envios and estado == "Listo para Retirar":
                midb = database.connect_db()
                cursor = midb.cursor()
                sql = f"insert into ViajesFlexs (Fecha, Numero_envío, Direccion, Referencia, Localidad, tipo_envio, Vendedor, estado_envio, comprador,nro_venta,Direccion_Completa) values('{str(fecha_creacion)[0:10]}','{nro_envio}','{direccion}','{referencia}','{localidad}',2,apodoOcliente(apodo({user_id})),'{estado}','{comprador}','{nro_venta}','{direccion_concatenada}')"
                cursor.execute(sql)
                midb.commit()
                print(f"Envio: {nro_envio} Agregado")
                nros_envios.append(x[0])
            else:
                print(f"Envio {nro_envio} descartado")
                print(f"Tipo de envio: {tipo_envio}")
                print(estado)

@ML.route("/notificacionesml", methods=["GET","POST"])
def recibirnotificacion():
    data = request.get_json()
    if request.method == "POST":
        t = Thread(target=procesarNotificacion, args=(data,))
        t.start()
        return  "Recibido"
