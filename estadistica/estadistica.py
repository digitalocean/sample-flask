#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from flask import Blueprint, render_template, request, session
from auth import auth
from informeErrores import informeErrores
from database import database
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
        sql = "select Fecha, Numero_envío, Localidad, Vendedor from historial_estados where lower(estado_envio) in ('en camino') and Fecha BETWEEN %s AND %s order by Vendedor"
        values = (desde,hasta)
        cursor.execute(sql, values)
        resultado = []
        for x in cursor:
            fecha = x[0]
            nenvio= x[1]
            loc = str(x[2]).lower()
            loc = quitarAcento(loc)
            vendedor = x[3]
            paquete = [fecha,nenvio,loc,vendedor]
            resultado.append(paquete)
        return render_template("estadistica.html", titulo="Estadistica", data=None, total=str(None),caba=str(None),z1=str(None),z2=str(None),cancelado=str(None),error = None, mensaje_error=None, auth = session.get("user_auth"))
    else:
        return render_template("estadistica.html", titulo="Estadistica", auth = session.get("user_auth"))