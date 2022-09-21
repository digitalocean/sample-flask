#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session
)
from auth import auth
from datetime import datetime

from database import database

ahora = (datetime.today())
fecha_hoy = str(ahora.year)+"/"+str(ahora.month)+"/"+str(ahora.day)
fecha_hoy_db = str(ahora.year)+"-"+str(ahora.month)+"-"+str(ahora.day)



us = Blueprint('usuarios', __name__, url_prefix='/')

@us.route("/usuarios")
@auth.login_required
def usuarios():
    return render_template ("usuarios/usuarios.html", titulo="Usuarios", auth = session.get("user_auth"))

@us.route("/registro", methods=["GET","POST"])
@auth.login_required
def registro_confirmado():
    if request.method == "POST":
        nickname = request.form.get("nickname")
        session["nw_user_nombre"] = nickname
        correo_electronico = request.form.get("correo_electronico")
        session["nw_user_correo"] = correo_electronico
        password = request.form.get("password")
        tipo_usuario = request.form.get("tipo_usuario")    
        midb = database.connect_db()
        cursor=midb.cursor()
        sql="insert into usuario (nickname,`password`,tipoUsuario) values(%s,%s,%s)"
        values=(nickname,password,tipo_usuario)
        cursor.execute(sql,values)
        midb.commit()
        midb.close()
        if tipo_usuario == "Chofer":
            return render_template("usuarios/nuevo_empleado.html", titulo="Registro", auth = session.get("user_auth"))
        elif tipo_usuario == "Cliente":
            return render_template("usuarios/nuevo_cliente.html", titulo="Registro", auth = session.get("user_auth"))
    else:
        return render_template("usuarios/nuevo_usuario.html", titulo="Registro", auth = session.get("user_auth"))

@us.route("/nuevo_empleado", methods=["GET","POST"])
@auth.login_required
def crear_empleado():
    if(request.method == "POST"):
        nombre = request.form.get("nombre")
        puesto = request.form.get("puesto")
        vehiculo = request.form.get("vehiculo")
        patente = request.form.get("patente")
        correo = request.form.get("correo")
        dni = request.form.get("dni")
        cbu = request.form.get("cbu")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")
        localidad = request.form.get("localidad")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmpassword")
        if password == confirmpassword:
            midb = database.connect_db()
            cursor = midb.cursor()
            sql = f"""INSERT INTO `mmslogis_MMSPack`.`empleado`(`nombre`,`puesto`,`vehiculo`,`patente`,`correo`,`dni`,`cbu`,`telefono`,`direccion`,`localidad`,`fecha_alta`,`password`) VALUES({nombre: },{puesto: },{vehiculo: },{patente: },{correo: },{dni: },{cbu: },{telefono: },{direccion: },{localidad: },current_date(),{password});"""
            cursor.execute(sql)
            midb.commit()
            midb.close()
            return render_template("usuarios/nuevo_empleado.html",titulo="Nuevo empleado", auth = session.get("user_auth"),mensaje="Agregado")
        else:
            return render_template("usuarios/nuevo_empleado.html",titulo="Nuevo empleado", auth = session.get("user_auth"),mensaje="Error al agregar")
    else:
        return render_template("usuarios/nuevo_empleado.html",titulo="Nuevo empleado", auth = session.get("user_auth"))

@us.route('/nuevo_cliente', methods=["GET","POST"])
@auth.login_required
def crear_cliente():
    if(request.method == "POST"):
        nombre = str(session.get("nw_user_nombre"))
        correo_electronico = request.form.get("correo_electronico")
        razon_social = request.form.get("razon_social")
        cuit = request.form.get("cuit")
        direccion = request.form.get("direccion")
        correo_electronico = request.form.get("correo_electronico")
        telefono = request.form.get("telefono")
        tarifa = request.form.get("tarifa")
        modo_cobro = request.form.get("modalidad_cobro")
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("insert into Clientes (nombre_cliente, razon_social, CUIT, Direccion,correo_electronico, telefono, tipo_cotizacion,Modalidad_cobro,Fecha_Alta) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (nombre,razon_social,cuit,direccion,correo_electronico,telefono,tarifa,modo_cobro,fecha_hoy_db))
        midb.commit()
        midb.close()
        session.pop("nw_user_nombre",None)
    return render_template("usuarios/nuevo_cliente.html",titulo="Nuevo Cliente", auth = session.get("user_auth"))



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