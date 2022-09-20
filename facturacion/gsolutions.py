#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, send_file
)
from auth import auth
from openpyxl import Workbook
from database import database

fa = Blueprint('almagro', __name__, url_prefix='/')

def consultar_clientes():
    midb = database.connect_db()
    cursor = midb.cursor()
    lista_clientes = []
    cursor.execute("select nombre from cliente")
    for cliente in cursor:
        lista_clientes.append(cliente)
    midb.close()
    return lista_clientes



@fa.route('/consulta_gsolutions')
@auth.login_required
def fac_almagro():
    clientes = [["GSolutions"],["Prueba"]]
    return render_template("tabla_viajes.html",titulo="Busqueda", clientes=clientes, auth = session.get("user_auth"), tipo_facturacion="almagro", indice_id=0)



@fa.route("/facturacion_almagro", methods=["GET"])
@auth.login_required
def fc_barracas():
    midb = database.connect_db()
    cursor = midb.cursor()
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    cliente = str(request.args.get("cliente"))
    desde = desde.replace("'","")
    hasta = hasta.replace("'","")
    cursor.execute("select fecha_despacho, remito, direccion, altura, ciudad, envios, estado, chofer from "+cliente+" where fecha_despacho between %s and %s", (desde,hasta))
    viajes = []
    dir_ant = ""
    cant_sobres = 0
    cantidad_direcciones = 0
    for viaje in cursor:
        viajes.append(viaje)
        cant_sobres += 1
        if viaje[2] + " " + viaje[3] == dir_ant:
            pass
        else:
            cantidad_direcciones += 1
        dir_ant = viaje[2] + " " + viaje[3]
    clientes = [["consultar_clientes()"]]
    midb.close()
    book = Workbook()
    sheet = book.active
    sheet["A1"] = "Fecha"
    sheet["B1"] = "id envio"
    sheet["C1"] = "Direccion"
    sheet["D1"] = "Localidad"
    sheet["E1"] = "Envios"
    sheet["F1"] = "Precio"
    sheet["G1"] = "Chofer"
    suma = 0
    sueldo_chofer = 0
    lista = []
    contador = 1
    for x in viajes:
        contador += 1
        sheet["A"+str(contador)] = x[0]
        sheet["B"+str(contador)] = x[1]
        sheet["C"+str(contador)] = x[2] + " " + x[3]
        sheet["D"+str(contador)] = x[4]
        sheet["G"+str(contador)] = x[7]
        if x[4] == "CABA" and x[5] == 1:
            sheet["E"+str(contador)] = 1
            sheet["F"+str(contador)] = 300
            suma += 300
            sueldo_chofer += 180
        elif x[4] != "CABA" and x[5] == 1:
            sheet["E"+str(contador)] = 1
            sheet["F"+str(contador)] = 500
            suma += 500
            sueldo_chofer += 250
            lista.append(x[4])
        elif x[5] == 0:
            sheet["E"+str(contador)] = 0
    sheet["E"+str(contador+1)] = "=SUM(E2:E"+str(contador)+")"
    sheet["F"+str(contador+1)] = "=SUM(F2:F"+str(contador)+")"
    book.save("Resumen.xlsx")
    return render_template("tabla_viajes.html",titulo="Facturacion",  tipo_facturacion="almagro", 
                                                direcciones=cantidad_direcciones, sobres=cant_sobres, 
                                                clientes=clientes, viajes=viajes,total=suma, sueldo=sueldo_chofer, 
                                                auth = session.get("user_auth"))

@fa.route("/facturacion/descarga", methods=["GET"])
@auth.login_required
def descargaResumenGsolutions():
    return send_file("Resumen.xlsx")