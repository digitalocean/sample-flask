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
        sql = "select Fecha, Numero_envío, Localidad, Vendedor from historial_estados where estado_envio in ('En Camino', 'En camino', 'en camino','Reasignado') and Fecha BETWEEN %s AND %s order by Vendedor"
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
        clientes = []
        cursor.execute("select localidad, zona from tarifa")
        zonas = []
        localidadyzona = {}
        for x in cursor.fetchall():
            localidad = str(x[0]).lower()
            localidad = quitarAcento(localidad)
            zona = x[1]
            localidadyzona[localidad] = zona
            locyzona = [localidad,zona]
            zonas.append(locyzona)
        total = 0 
        cancelado = 0
        errores = 0
        lista_error = []
        caba = 0
        z1 = 0 
        z2 = 0
        for x in resultado:
            total += 1
            localidad = str(x[2]).lower()
            localidad = quitarAcento(localidad)
            try:
                if localidad in localidadyzona.keys():
                    zona = localidadyzona[localidad]
                    if zona == "Flex CABA":
                        caba += 1
                    elif zona == "Flex Zona (1)":
                        z1 += 1
                    elif zona == "Flex Zona (2)":
                        z2 += 1
                else:
                    errores += 1
                    if localidad not in lista_error:
                        lista_error.append(localidad)
                if str(x[3]) in str(clientes):
                    for y in clientes:
                        if y[0] == x[3]:
                            y[1] += 1
                            if zona == "Flex CABA":
                                y[2] += 1
                            elif zona == "Flex Zona (1)":
                                y[3] += 1
                            elif zona == "Flex Zona (2)":
                                y[4] +=1
                else:
                    if zona == "Flex CABA":
                        flex_caba = 1
                    else:
                        flex_caba = 0
                    if zona == "Flex Zona (1)":
                        flex_zona1 = 1
                    else:
                        flex_zona1 = 0
                    if zona == "Flex Zona (2)":
                        flex_zona2 =1
                    else:
                        flex_zona2 = 0
                    cliente = x[3]
                    cantidad = 1
                    paquete = [cliente,cantidad,flex_caba,flex_zona1,flex_zona2]
                    clientes.append(paquete)
            except Exception as estadistica:
                informeErrores.informeErrores(estadistica)
                errores += 1
        return render_template("estadistica.html", titulo="Estadistica", data=clientes, total=str(total),caba=str(caba),z1=str(z1),z2=str(z2),cancelado=str(cancelado),error = errores, mensaje_error=sorted(lista_error), auth = session.get("user_auth"))
    else:
        return render_template("estadistica.html", titulo="Estadistica", auth = session.get("user_auth"))