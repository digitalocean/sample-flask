#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from flask import Blueprint, render_template, request, session,redirect
from datetime import datetime
from auth import auth
from database import database
from informeErrores import informeErrores
import openpyxl
from logistica import Envio
from scriptGeneral import scriptGeneral


formms = Blueprint('formms', __name__, url_prefix='/')

@formms.route("/carga_formms", methods = ["GET","POST"])
@auth.login_required
def subir_exel_formms():
    ahora = (datetime.today())
    if request.method == "POST":
        archivo_xlsx = request.files["upload"]
        libro = openpyxl.load_workbook(archivo_xlsx)
        sheet_obj = libro.active 
        cant_columnas = 14
        contador = 0
        try:
            for x in range(cant_columnas):
                contador += 1
                cab = str(sheet_obj.cell(row = 1, column = contador).value)
                if cab.lower() == "fecha":
                    col_fecha = contador
                elif cab.lower() in ("numero de envio", "numero de envío", "nro de envio","order number"):
                    col_numero_envio = contador
                elif cab.lower() in ("cliente","first Name (shipping)","comprador","quien recibe"):
                    col_cliente = contador
                elif cab.lower() in ("direccion","address 1&2 (Shipping)"):
                    col_direccion = contador
                elif cab.lower() in ("localidad","city (shipping)"):
                    col_localidad = contador
                elif cab.lower() in ("vendedor"):
                    col_vendedor = contador
                elif cab.lower() in ("cp","postcode (shipping)","código postal","codigo postal"):
                    col_cp = contador
                elif cab.lower() in ("telefono","phone (billing)"):
                    col_telefono = contador
                elif cab.lower() in ("referencia","customer note","detalle dirección","detalle direccion"):
                    col_referencia = contador
            print("\nasignacion completa\n")
        except Exception as cabezeras:
            informeErrores.reporte(cabezeras,"/carga_formms")
            print("\nError al asignar variables\n")
        n_row = 1
        total = 0
        omitido = 0
        flex_agregado = 0
        cantidad = range(sheet_obj.max_row)
        contadorCantidad = 0
        for fila in cantidad:
            contadorCantidad += 1
            if contadorCantidad > 200:
                break
        if contadorCantidad > 200:
            cantidad = range(0,200)
        for x in cantidad:
            total += 1
            n_row += 1
            if col_numero_envio:
                nro_envio = str(sheet_obj.cell(row = n_row, column = col_numero_envio).value)
            else:
                nro_envio = ""
            if nro_envio == str(None) or nro_envio == "":
                continue
            fecha = str(ahora)[0:10]
            if col_fecha:
                fecha = str(sheet_obj.cell(row = n_row, column = col_fecha).value)
            if col_cliente:
                cliente = str(sheet_obj.cell(row = n_row, column = col_cliente).value)
            else:
                cliente = ""
            if col_telefono:    
                telefono = str(sheet_obj.cell(row = n_row, column = col_telefono).value)
            else:
                telefono = None
            if col_direccion: 
                direccion = str(sheet_obj.cell(row = n_row, column = col_direccion).value)
            else:
                direccion = ""
            if "/" in str(direccion):
                direccion = str(direccion.split("/"))[0]
            if col_referencia:
                referencia = str(sheet_obj.cell(row = n_row, column = col_referencia).value)
            else:
                referencia = ""
            if col_localidad: localidad = str(sheet_obj.cell(row = n_row, column = col_localidad).value)
            if col_cp:
                cp = str(sheet_obj.cell(row = n_row, column = col_cp).value)
            else:
                cp = 0
            if cp == "":
                cp = 0
            if session.get("user_auth") == "Cliente":
                vendedor = session.get("user_id")
            elif session.get("user_auth") == "Zippin":
                vendedor = str(sheet_obj.cell(row = n_row, column = col_vendedor).value)
            else:
                vendedor = request.form.get("nombre_cliente")
            
            fecha = fecha[0:10].replace("/","-").replace("\\","")
            tipo_envio = 2
            viaje = Envio.Envio(nro_envio,direccion,localidad,vendedor,cliente,telefono,referencia,cp,fecha,tipoEnvio=tipo_envio)
            if viaje.toDB():flex_agregado += 1 
            else: omitido+=1
            print(viaje.Numero_envío)
        print(f"agregados {flex_agregado}")
        print(f"omitidos {omitido}")
        return render_template("CargaArchivo/data.html",
                                titulo="Carga", 
                                analizados=total, 
                                agregados=flex_agregado, 
                                repetido=omitido, 
                                auth = session.get("user_auth"))

    else:
        return render_template("CargaArchivo/carga_archivo.html",
                                titulo="Carga", 
                                clientes=scriptGeneral.consultar_clientes(database.connect_db()), 
                                auth = session.get("user_auth"), 
                                url_post="carga_formms")


