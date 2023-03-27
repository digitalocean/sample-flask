#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8
from threading import Thread
from Backend.database import database
from flask import Blueprint, redirect, request,render_template,session
from Backend.database.database import connect_db
import requests

from Backend.MeLi.consultar_envio import consultar_envio
from .procesarNotificacion import procesarNotificacion
from Backend.informeErrores import informeErrores
ML = Blueprint('MeLi', __name__, url_prefix='/')

@ML.route("/logistica/vinculacionml/baja", methods=["GET","POST"])
def bajaVinculacion():
    id = request.form.get("id")
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("update vinculacion set baja = 'Yes' where id = %s",(id,))
    midb.commit()
    return redirect("/logistica/vinculacionml")

@ML.route("/logistica/vinculacionml/alta", methods=["GET","POST"])
def altaVinculacion():
    id = request.form.get("id")
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("update vinculacion set baja = 'No' where id = %s",(id,))
    midb.commit()
    return redirect("/logistica/vinculacionml")

@ML.route("/logistica/vinculacionml", methods=["GET","POST"])
def verVinculaciones():
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select id,nickname,user_id,status,reported,alta,baja from vinculacion")
    vinculaciones = list(cursor.fetchall())
    columnas = [i[0] for i in cursor.description]
    return render_template("/MeLi/vinculacion.html",
                            vinculaciones=vinculaciones,
                            cabezeras = columnas, 
                            auth = session.get("user_auth"))


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
            midb = database.connect_db_ML()
            cursor = midb.cursor()    
            try:
                sql = f"""insert into vinculacion 
                            (nickname,user_id,access_token,refresh_token,status,reported) 
                        values
                            ('{nickname}',{user_id},'{access_token}','{refresh_token}','Correcto','No')
                        ON DUPLICATE KEY UPDATE    
                            user_id={user_id}, nickname = '{nickname}',
                            access_token = '{access_token}',refresh_token = '{refresh_token}',status = 'Correcto' ,reported = 'No';"""

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


@ML.route("/notificacionesml", methods=["GET","POST"])
def recibirnotificacion():
    data = request.get_json()
    if request.method == "POST":
        t = Thread(target=procesarNotificacion, args=(data,))
        t.start()
        return  "Recibido"
