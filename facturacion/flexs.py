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
from scriptGeneral import scriptGeneral
fb = Blueprint('facturacion', __name__, url_prefix='/')



@fb.route('/consulta_flexs')
@auth.login_required
def consultaFlexs():
    hoy = str(datetime.now())[0:10]
    return render_template("facturacion/tabla_viajes.html",
                        titulo="Facturacion", 
                        desde=hoy,
                        hasta=hoy,
                        clientes=scriptGeneral.consultar_clientes(database.connect_db()), 
                        tipo_facturacion="flex", 
                        auth = session.get("user_auth"))

@fb.route("/facturacion_flex", methods=["GET"])
@auth.login_required
def facturacionFlex():
    midb = database.connect_db()
    cursor = midb.cursor()
    cliente = request.args.get("cliente")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
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
    sql = f"select Fecha, Numero_envío,Direccion_Completa,Localidad,Precio,Vendedor from historial_estados where Vendedor in (select Apodo from mmslogis_MMSPack.`Apodos y Clientes` where Cliente = '{cliente}') and Fecha between '{desde}' and '{hasta}' and estado_envio in ('En Camino','Levantada') order by Fecha desc"
    cursor.execute(sql)
    sinprecio = 0
    for viajeTupla in cursor.fetchall():
        viaje = list(viajeTupla)
        contador += 1
        fecha = viaje[0]
        nenvio = viaje[1]
        direccionCompleta = viaje[2]
        localidad = viaje[3]
        precio = viaje[4]
        apodo = viaje[5]
        if(precio == None):
            sinprecio = sinprecio +1
            viaje[4] = "Sin precio"
            suma = suma + 0
        else:
            suma = suma + float(precio)
        sheet["A"+str(contador)] = fecha
        sheet["B"+str(contador)] = nenvio
        sheet["C"+str(contador)] = direccionCompleta
        sheet["D"+str(contador)] = localidad
        sheet["E"+str(contador)] = apodo
        sheet["F"+str(contador)] = precio
        
        viajes.append(viaje)
    sheet["F"+str(contador+1)] = "=SUM(E2:E"+str(contador)+")"
    book.save("Resumen.xlsx")
    return render_template("facturacion/tabla_viajes.html",
                            cliente=cliente,
                            desde=desde,
                            hasta=hasta,
                            titulo="Facturacion", 
                            tipo_facturacion="flex", 
                            viajes=viajes, 
                            total=f"${suma} y {sinprecio} viajes sin precio", 
                            clientes = scriptGeneral.consultar_clientes(midb), 
                            auth = session.get("user_auth")
                            )

