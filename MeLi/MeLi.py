#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from ftplib import error_proto
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, make_response

from MeLi.script import consultar_envio
from informeErrores import informeErrores
ML = Blueprint('MeLi', __name__, url_prefix='/')
from datetime import datetime
import pymysql

secret_key = "abcd1234"
@ML.route("/callbacks", methods=["GET","POST"])
def vinculacion():
    file = open("MeLi/logcallbacks.txt", "a")
    file.write("\n\n-.-.-.-callbacks-.-.-.-\n")
    file.write(str(datetime.now()))
    file.write("\nMetodo = " + str(request.method) + "\n")
    if request.method == "POST":
        file.close()
        return redirect("https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=4857198121733101&redirect_uri=https://www.mmspack.com/callbacks")
    elif request.method == "GET":
        data = request.args
        for x in data:
            file.write(str(x + " = " + data[x] + "\n"))
        try:
            code = data["code"]
            state = data["state"]
            return render_template ("MeLi/usuario_web.html", code=code, state=state)

        except Exception as ErrorEnPOST:
            informeErrores.reporte(str(ErrorEnPOST) + "FUNCIONA A FUERZA BRUTA","/Callbacks")
            try:
                user_id = data["user_id"]
                access_token = data["access_token"]
                refresh_token= data["refres_token"]
                return render_template("MeLi/usuario_web.html", user_id=user_id, access_token=access_token,refresh_token=refresh_token)
            except Exception as errorEnVinculacion:
                informeErrores.reporte(errorEnVinculacion,"/Callbacks 2do except")
                return "fallo la vinculacion"


@ML.route("/usuario_vinculado", methods=["POST"])
def usuario_vinculado():
    if request.method == "POST":
        nickname = request.form["nickname"]
        contrasenia = request.form["contrasenia"]
        correo_electronico = request.form["correo_electronico"]
        code = request.form["code"]
        state = request.form["state"]
        if state == secret_key:
            midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='viajesbarracas', charset = 'utf8mb4')
            cursor = midb.cursor()
            cursor.execute("insert into usuario (nickname, contraseña,correo_electronico, tipo_usuario, refresh_token) values(%s,%s,%s,%s,%s)", (nickname, contrasenia,correo_electronico, "Cliente", code))
            midb.commit()
            midb.close()
            render_template ("login.html", mensaje="Bienvenido")    
            return "Usuario creado"
        else:
            return "Error al crear el usuario"
    else:
        return "Metodo GET"

@ML.route("/notificacionesml", methods=["GET","POST"])
def recibirnotificacion():
    file = open("MeLi/log.txt", "a")
    file.write("\n\n\nNueva notificacion!!\n-.-.-"+str(datetime.now())[0:19]+".-.-.-")
    file.write("\nMetodo = "+ request.method +"\n")
    data = request.get_json()
    file.write("JSON recibido\n")
    file.write(str(data))

    if request.method == "POST":
        nros_envios = []
        midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='mmspack-almagro', charset = 'utf8mb4')
        cursor = midb.cursor()
        cursor.execute("select Numero_envío from ViajesFlexs")
        envios = cursor.fetchall()
        for x in envios:
            nros_envios.append(x[0])
        resource = data.get("resource")
        user_id = data.get("user_id")
        topic = data.get("topic")
        received = data.get("received")
        attempts = data.get("attempts")
        application_id = data.get("application_id")
        sent = data.get("sent")
        file.write("\nRecursos obtenidos\n")
        file.write(str(topic))
        if str(topic) == "shipments":
            midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='mmspack-almagro', charset = 'utf8mb4')
            cursor = midb.cursor()
            cursor.execute("insert into registro_ml (resource, user_id, topic, received, attempts, application_id, sent) values(%s,%s,%s,%s,%s,%s,%s)", (resource,user_id,topic,received,attempts,application_id,sent))
            midb.commit()
            midb.close()
            nro_envio = (resource.split("/"))[2]
            #nro_envio, tipo_envio, direccion, localidad, referencia, estado, comprador, fecha_creacion,nro_venta
            if str(nro_envio) not in str(nros_envios):
                viaje = consultar_envio(nro_envio, user_id)
                tipo_envio= viaje[1] 
                direccion= viaje[2] 
                localidad= viaje[3] 
                referencia= viaje[4] 
                estado = viaje[5]
                comprador = viaje[6]
                fecha_creacion = viaje[7]
                nro_venta = viaje[8]
                direccion_concatenada = direccion + ", " + localidad + ", Buenos aires"
                midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='mmspack-almagro', charset = 'utf8mb4')
                while midb.open == False:
                    midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='mmspack-almagro', charset = 'utf8mb4')
                cursor = midb.cursor()
                cursor.execute("insert into ViajesFlexs (Fecha, Numero_envío, Direccion, Referencia, Localidad, tipo_envio, Vendedor, estado_envio, comprador,nro_venta,Direccion_Completa) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (fecha_creacion,nro_envio,direccion,referencia,localidad,tipo_envio,user_id,estado,comprador,nro_venta,direccion_concatenada))
                midb.commit()
                midb.close()
                nros_envios.append(x[0])
            else:
                midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='mmspack-almagro', charset = 'utf8mb4')
                while midb.open == False:
                    midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='mmspack-almagro', charset = 'utf8mb4')
                cursor = midb.cursor()
                cursor.execute("select * from ViajesFlexs where Numero_envío = '%s'", (nro_envio,))
                estado_db = cursor[0]
                midb.commit()
                midb.close()
                if estado_db == "Entregado" or  estado_db == estado:
                    pass
                else:
                    midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='mmspack-almagro', charset = 'utf8mb4')
                    while midb.open == False:
                        midb = pymysql.connect(host='190.228.29.62', user='matyacc', passwd='Agustin_1504', db='mmspack-almagro', charset = 'utf8mb4')
                    cursor = midb.cursor()
                    cursor.execute("UPDATE `viajesbarracas`.`ViajesFlexs` SET `estado_envio` = '%s' WHERE (`Numero_envío` = '%s');", (estado,nro_envio))
                    midb.commit()
                    midb.close()
                    



        file.write("\nJson guardado en DB")
        return  "Json guardado en base de datos"

    else:
        try:
            file.write("request.args")
            for x in request.args:
                file.write(x)
                file.write("\n")
                file.close()
        except Exception as getInCallbacks:
            informeErrores.reporte(getInCallbacks,"/CallbacksGET")
        return "GET"


