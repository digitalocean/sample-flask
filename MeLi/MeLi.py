#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from database import database
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, make_response

from MeLi.script import consultar_envio
from informeErrores import informeErrores
ML = Blueprint('MeLi', __name__, url_prefix='/')
from datetime import datetime

secret_key = "abcd1234"
@ML.route("/callbacks", methods=["GET","POST"])
def vinculacion():
    if request.method == "POST":
        return redirect("https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=4857198121733101&redirect_uri=https://www.mmspack.com/callbacks")
    elif request.method == "GET":
        data = request.args
        if "code" in data.keys():
            code = data["code"]
            state = data["state"]
            return render_template ("MeLi/usuario_web.html", code=code, state=state)
        else:
            try:
                user_id = data["user_id"]
                access_token = data["access_token"]
                refresh_token= data["refres_token"]
                return render_template("MeLi/usuario_web.html", user_id=user_id, access_token=access_token,refresh_token=refresh_token)
            except Exception as errorEnVinculacion:
                informeErrores.reporte(f"{errorEnVinculacion} ","/Callbacks")
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
            midb = database.connect_db
            cursor = midb.cursor()
            cursor.execute("insert into usuario (nickname, contraseña,correo_electronico, tipo_usuario, refresh_token) values(%s,%s,%s,%s,%s)", (nickname, contrasenia,correo_electronico, "Cliente", code))
            midb.commit()
            midb.close()
            return render_template ("login.html", mensaje="Bienvenido")    
        else:
            return "Error al crear el usuario"
    else:
        return "Metodo GET"


@ML.route("/notificacionesml", methods=["GET","POST"])
def recibirnotificacion():
    data = request.get_json()
    if request.method == "POST":
        nros_envios = []
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("select Numero_envío from ViajesFlexs")
        envios = cursor.fetchall()
        for x in envios:
            nros_envios.append(str(x[0]))
        resource = data.get("resource")
        user_id = data.get("user_id")
        topic = data.get("topic")
        received = data.get("received")
        attempts = data.get("attempts")
        application_id = data.get("application_id")
        sent = data.get("sent")
        print(f"resource: {resource},\nuser_id: {user_id},\ntopic: {topic},\nsent: {sent},\nreceived: {received},\nattempts: {attempts},\napplication_id: {application_id}")
        if str(topic) == "shipments":
            nro_envio = (resource.split("/"))[2]
            print(nro_envio)
            viaje = consultar_envio(nro_envio, user_id)
            if viaje != None:
                print(f"viaje: {viaje}")
                tipo_envio= viaje[1] 
                direccion= viaje[2] 
                localidad= viaje[3] 
                referencia= viaje[4] 
                estado = viaje[5]
                comprador = viaje[6]
                fecha_creacion = viaje[7]
                nro_venta = viaje[8]
                direccion_concatenada = direccion + ", " + localidad + ", Buenos aires"
                if str(nro_envio) not in nros_envios:
                    # midb = database.connect_db()
                    # midb = database.verificar_conexion(midb)
                    # cursor = midb.cursor()
                    # cursor.execute("insert into ViajesFlexs (Fecha, Numero_envío, Direccion, Referencia, Localidad, tipo_envio, Vendedor, estado_envio, comprador,nro_venta,Direccion_Completa) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (fecha_creacion,nro_envio,direccion,referencia,localidad,tipo_envio,user_id,estado,comprador,nro_venta,direccion_concatenada))
                    # midb.commit()
                    print(fecha_creacion," / ",nro_envio," / ",direccion," / ",referencia," / ",localidad," / ",tipo_envio," / ",user_id," / ",estado," / ",comprador," / ",nro_venta," / ",direccion_concatenada)
                    nros_envios.append(x[0])
        return  "Json guardado en base de datos"
