#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from datetime import datetime
from flask import (
    Blueprint, g, render_template, request, session
)
from auth import auth
from informeErrores import informeErrores
from openpyxl import Workbook


from database import database
from .script import consultar_clientes,quitarAcento
fb = Blueprint('fc_barracas', __name__, url_prefix='/')



@fb.route('/consulta_flexs')
@auth.login_required
def fac_barracas():
    hoy = str(datetime.now())[0:10]
    clientes = consultar_clientes()
    return render_template("tabla_viajes.html",desde=hoy,hasta=hoy,titulo="Busqueda", clientes=clientes, tipo_facturacion="barracas", auth = session.get("user_auth"))

# para grabar los precios en DB comentar lineas 45, y 86 y descomentar 46:47,85,101 y 107:110
@fb.route("/facturacion_barracas", methods=["GET"])
@auth.login_required
def df_barracas():
    midb = database.connect_db()
    cursor = midb.cursor()
    cliente = request.args.get("cliente")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    cursor.execute("select nombre_cliente, tarifa from Clientes")
    clienteTarifa = {}
    for client in cursor.fetchall():
        clienteTarifa[quitarAcento(client[0].lower())] = client[1]
    tarifa = clienteTarifa[quitarAcento(cliente.lower())]
    # tarifaAFacturar = "1"
    # tarifa = "9"
    print(tarifa)
    viajes = []
    suma = 0
    book = Workbook()
    sheet = book.active
    sheet["A1"] = "Fecha"
    sheet["B1"] = "id envio"
    sheet["C1"] = "Direccion"
    sheet["D1"] = "Localidad"
    sheet["E1"] = "Precio"
    sheet["F1"] = "Cuenta"
    contador = 1
    sinPrecio = 0
    if tarifa == "1":
        columnaTarifa = "Tarifa1"
    elif tarifa == "2":
        columnaTarifa = "Tarifa2"
    elif tarifa == "3":
        columnaTarifa = "Tarifa3"
    elif tarifa == "4":
        columnaTarifa = "Tarifa4"
    elif tarifa == "5":
        columnaTarifa = "Tarifa5"
    elif tarifa == "6":
        columnaTarifa = "Tarifa6"
    elif tarifa == "7":
        columnaTarifa = "Tarifa7"
    elif tarifa == "8":
        columnaTarifa = "Tarifa8"
    elif tarifa == "9":
        columnaTarifa = "Tarifa9"
    elif tarifa == "10":
        columnaTarifa = "Tarifa10"
    elif tarifa == "11":
        columnaTarifa = "Tarifa11"
    elif tarifa == "12":
        columnaTarifa = "Tarifa12"
    elif tarifa == "13":
        columnaTarifa = "Tarifa13"
    elif tarifa == "14":
        columnaTarifa = "Tarifa14"
    elif tarifa == "15":
        columnaTarifa = "Tarifa15"

    localidadPrecio = {}
    cursor.execute(f"select localidad,{columnaTarifa} from tarifa")
    for dato in cursor.fetchall():
        localidad = quitarAcento(str(dato[0]).lower())
        precio = dato[1]
        localidadPrecio[localidad] = precio
    # sql = f"select Fecha, Numero_envío,Direccion_Completa,Localidad,Precio,id from historial_estados where id in(select id from historial_estados where Vendedor in (select nombre_cliente from Clientes where tarifa = {tarifaAFacturar})) and Precio is null and estado_envio = 'En Camino';"
    sql = f"select Fecha, Numero_envío,Direccion_Completa,Localidad,Precio,Vendedor from historial_estados where Vendedor in (select Apodo from mmslogis_MMSPack.`Apodos y Clientes` where Cliente = '{cliente}') and Fecha between '{desde}' and '{hasta}' and estado_envio in ('En Camino','Levantada') order by Fecha desc"    
    cursor.execute(sql)
    print(sql)
    for viajeTupla in cursor.fetchall():
        viaje = list(viajeTupla)
        contador += 1
        fecha = viaje[0]
        nenvio = viaje[1]
        direccionCompleta = viaje[2]
        localidad = viaje[3]
        precio = viaje[4]
        apodo = viaje[5]
        sheet["A"+str(contador)] = fecha
        sheet["B"+str(contador)] = nenvio
        sheet["C"+str(contador)] = direccionCompleta
        sheet["D"+str(contador)] = localidad
        # id = viaje[5]
        sheet["E"+str(contador)] = apodo
        try:
            prc = localidadPrecio[quitarAcento(str(localidad).lower())]
            sheet["E"+str(contador)] = prc
            suma = suma + float(prc)
            viaje[4] = prc
            # sql = f"update historial_estados set Precio = {prc} where id = {id}"
            # print(sql)
            # cursor.execute(sql)
            # midb.commit()
        except:
            sinPrecio += 1
            sheet["E"+str(contador)] = "Este no facturo"
        viajes.append(viaje)
    sheet["E"+str(contador+1)] = "=SUM(E2:E"+str(contador)+")"
    book.save("Resumen.xlsx")
    midb.close()
    return render_template("tabla_viajes.html",cliente=cliente,desde=desde,hasta=hasta,titulo="Facturacion", tipo_facturacion="barracas", viajes=viajes, total=f"${suma} y {sinPrecio} viajes sin precio", clientes = consultar_clientes(), auth = session.get("user_auth"))

