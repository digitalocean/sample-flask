#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from flask import (
    Blueprint, jsonify, g, redirect, render_template, request, session
)
from werkzeug.security import generate_password_hash,check_password_hash
import json
from auth import auth
from datetime import datetime

from database import database

ahora = (datetime.today())
fecha_hoy = str(ahora.year)+"/"+str(ahora.month)+"/"+str(ahora.day)
fecha_hoy_db = str(ahora.year)+"-"+str(ahora.month)+"-"+str(ahora.day)



us = Blueprint('usuarios', __name__, url_prefix='/')




@us.route('/nuevo_cliente', methods=["GET","POST"])
@auth.login_required
def crear_cliente():
    if(request.method == "GET"):
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("select id, nombre from tarifa")
        tarifas = []
        for x in cursor.fetchall():
            id = x[0]
            tar = x[1]
            tarifas.append([id,tar])
        return render_template("usuario/nuevo_cliente.html",
                                auth = session.get("user_auth"),
                                tarifas=tarifas)

    elif(request.method == "POST"):
        nombre = request.form.get("nombre")
        razon_social = request.form.get("razon_social")
        cuit = request.form.get("cuit")
        direccion = request.form.get("direccion")
        correo_electronico = request.form.get("correo_electronico")
        telefono = request.form.get("telefono")
        telefonoAlternativo = request.form.get("telefonoAlternativo")
        passw = request.form.get("password")
        modo_cobro = request.form.get("modCobro")
        tarifa = request.form.get("tarifa")
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("""
        INSERT INTO `mmslogis_MMSPack`.`Clientes`
            (`nombre_cliente`,
            `razon_social`,
            `CUIT`,
            `Direccion`,
            `Telefono`,
            `Telefono_Alternativo`,
            `password`,
            `Fecha_Alta`,
            `Modalidad_cobro`,
            `correo_electronico`,
            `tarifa`)
            VALUES(%s,%s,%s,%s,%s,%s,%s,current_date(),%s,%s,%s);""", 
            (nombre,razon_social,cuit,direccion,telefono,telefonoAlternativo,passw,
            modo_cobro,correo_electronico,tarifa))
        midb.commit()
        midb.close()
        session.pop("nw_user_nombre",None)
        return render_template("usuario/nuevo_cliente.html",titulo="Nuevo Cliente", auth = session.get("user_auth"))



@us.route("/cambio_contrasena", methods=["GET","POST"])
@auth.login_required
def cambio_contrasena():
    if request.method == "POST":
        user = session.get("user_id")
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("select contraseña from usuario where nickname = %s", (user,))
        for x in cursor:
            contrasena = x[0]
        actual = request.form.get("actual")
        if actual == contrasena:
            nueva = request.form.get("nueva")
            confirma = request.form.get("confirma")
            if nueva == confirma:
                cursor.execute("UPDATE `usuario_web`.`usuario` SET `password` = %s WHERE (`nickname` = %s);", (nueva,user))
                midb.commit()
                midb.close()
                mensaje = 'La contraseña se cambio correctamente, <a href="/">Clic aqui</a> para volver al inicio'
                return mensaje
            else:
                return 'revise las contraseñas ingresadas<a href="/conf">Volver atras</a>'
        else:
            return 'revise las contraseñas ingresadas<a href="/conf">Volver atras</a>'
    else:
        return redirect("/")



from database import database
@us.route("/api/users/create",methods=["POST"])
def nuevoEmpleado():
    try:
        data = request.get_json()
        midb = database.connect_db()
        cursor = midb.cursor()
        passw = generate_password_hash(data['password'])
        cursor.execute(f"insert into empleado (nombre,puesto,vehiculo,patente,correo,dni,cbu,telefono,direccion,localidad,password) values('{data['nombre']}','{data['puesto']}','{data['vehiculo']}','{data['patente']}','{data['correo']}','{data['dni']}','{data['cbu']}','{data['telefono']}','{data['direccion']}','{data['localidad']}','{passw}')")
        midb.commit()
        midb.close()
        return jsonify(success=True,message="Usuario Creado",data=None)
    except:
        return jsonify(success=False,message="Se produjo un error al intentar crear el usuario",data=None)

