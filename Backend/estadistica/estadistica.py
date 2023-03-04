#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from flask import Blueprint, render_template, request, session
from Backend.auth import auth
from Backend.informeErrores import informeErrores
from Backend.database import database
def quitarAcento(string):
    string = str(string).replace("á","a")
    string = str(string).replace("é","e")
    string = str(string).replace("í","i")
    string = str(string).replace("ó","o")
    string = str(string).replace("ú","u")
    return string
    
def busqueda_lineal(lista, x):
    i = 0
    for z in lista:
        if z[0].lower() == x.lower():
            return i
        i = i+1
    return -1

est = Blueprint('est', __name__, url_prefix='/')

@est.route("/estadistica", methods = ["GET","POST"])
@auth.login_required
def estadistica():
    if request.method == "POST":
        desde = request.form.get("desde")
        hasta = request.form.get("hasta")
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = """select H.tipo_envio,ifnull(Z.nombre,"Sin cotizar"),count(*) as Cantidad 
                from historial_estados as H 
                left join localidad as L on H.Localidad = L.localidad
                left join indicePrecio as IP on L.id = IP.id_localidad and IP.id_tarifa = 1
                left join zona as Z on IP.id_zona = Z.id
                where H.estado_envio = 'En Camino' and Fecha BETWEEN %s AND %s group by H.tipo_envio, Z.nombre;"""
        values = (desde,hasta)
        cursor.execute(sql, values)
        resultado = []
        for x in cursor:
            resultado.append(x)
        return render_template("estadistica.html", 
                                titulo="Estadistica", 
                                data=resultado, 
                                total=str(None),
                                caba=str(None),
                                z1=str(None),
                                z2=str(None),
                                cancelado=str(None),
                                error = None, 
                                mensaje_error=None, 
                                auth = session.get("user_auth"))
    else:
        return render_template("estadistica.html", 
                                titulo="Estadistica", 
                                auth = session.get("user_auth"))