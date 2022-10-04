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
    sheet["A1"] = "id"
    sheet["B1"] = "Numero_envío"
    sheet["C1"] = "Vendedor"
    sheet["D1"] = "Direccion_Completa"
    sheet["E1"] = "Fecha"
    sheet["F1"] = "Localidad"
    sheet["G1"] = "Recibio"
    sheet["H1"] = "Chofer"
    sheet["I1"] = "Precio"
    sheet["J1"] = "Costo"
    sheet["K1"] = "Hora"
    sheet["L1"] = "Currentlocation"
    sheet["M1"] = "estado_envio"
    sheet["N1"] = ""
    
    
    contador = 1
    # sql = f"select Fecha, Numero_envío,Direccion_Completa,Localidad,Precio,Vendedor from historial_estados where Vendedor in (select Apodo from mmslogis_MMSPack.`Apodos y Clientes` where Cliente = '{cliente}') and Fecha between '{desde}' and '{hasta}' and estado_envio in ('En Camino','Levantada') order by Fecha desc"
    sql = f"select id,Numero_envío,Vendedor,Direccion_Completa,Fecha,Localidad,Recibio,Chofer,Precio,Costo,Hora,Currentlocation,estado_envio from historial_estados where Fecha between '{desde}' and '{hasta}' and estado_envio in ('En Camino','Levantada') order by Fecha desc"
    cursor.execute(sql)
    sinprecio = 0
    for viajeTupla in cursor.fetchall():
        viaje = list(viajeTupla)
        contador += 1
        # fecha = viaje[5]
        # nenvio = viaje[1]
        # direccionCompleta = viaje[2]
        # localidad = viaje[3]
        # precio = viaje[4]
        # apodo = viaje[5]
        id = viaje[0]
        nenvio = viaje[1] 
        apodo = viaje[2]
        direccionCompleta = viaje[3]
        fecha = viaje[4]
        localidad = viaje[5]
        Recibio = viaje[6] 
        Chofer = viaje[7]
        precio = viaje[8] 
        Costo = viaje[9] 
        Hora = viaje[10]
        Currentlocation = viaje[11]
        estado_envio = viaje[12]



        if(precio == None):
            sinprecio = sinprecio +1
            viaje[4] = "Sin precio"
            suma = suma + 0
        else:
            suma = suma + float(precio)
        # sheet["A"+str(contador)] = fecha
        # sheet["B"+str(contador)] = nenvio
        # sheet["C"+str(contador)] = direccionCompleta
        # sheet["D"+str(contador)] = localidad
        # sheet["E"+str(contador)] = apodo
        # sheet["F"+str(contador)] = precio
        sheet["A"+str(contador)] = id
        sheet["B"+str(contador)] = nenvio
        sheet["C"+str(contador)] = apodo
        sheet["D"+str(contador)] = direccionCompleta
        sheet["E"+str(contador)] = fecha
        sheet["F"+str(contador)] = localidad
        sheet["G"+str(contador)] = Recibio
        sheet["H"+str(contador)] = Chofer
        sheet["I"+str(contador)] = precio
        sheet["J"+str(contador)] = Costo
        sheet["K"+str(contador)] = Hora
        sheet["L"+str(contador)] = Currentlocation
        sheet["M"+str(contador)] = estado_envio

        viajes.append(viaje)
    sheet["J"+str(contador+1)] = "=SUM(J2:j"+str(contador)+")"
    sheet["K"+str(contador+1)] = "=SUM(K2:K"+str(contador)+")"
    book.save("Resumen.xlsx")
    cabezeras = ["id","Numero_envío","Vendedor","Direccion_Completa","Fecha","Localidad","Recibio","Chofer","Precio","Costo","Hora","Currentlocation","estado_envio"]
    return render_template("facturacion/tabla_viajes.html",
                            cliente=cliente,
                            desde=desde,
                            hasta=hasta,
                            titulo="Facturacion", 
                            cabezeras = cabezeras,
                            tipo_facturacion="flex", 
                            viajes=viajes, 
                            total=f"${suma} y {sinprecio} viajes sin precio", 
                            clientes = scriptGeneral.consultar_clientes(midb), 
                            auth = session.get("user_auth")
                            )

@fb.route("/facturacion/borrar_repetido")
@auth.login_required
@auth.admin_required
def borrarRepetidos():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select id, Numero_envío, estado_envio from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'En Camino' group by Numero_envío having count(Numero_envío) >1) and estado_envio = 'En Camino'")
    envios = {}
    for x in cursor.fetchall():
        if x[1] in envios.keys():
            envios[str(x[1])].append(x[2])
        else:
            envios[x[1]] = [x[2]]
    cantidad = 0
    enviosDuplicados = []
    for x in envios:
        if (len(envios[x])) > 1:
            enviosDuplicados.append(x)
            cantidad += 1
    print(f"{cantidad} a revisar antes de facturar")
    borrados = 0
    controlado = 0
    errores = []
    for y in enviosDuplicados:
        controlado += 1
        # midb = database.verificar_conexion(midb)
        sql = f"select id from historial_estados where estado_envio = 'En Camino' and Numero_envío = '{y}'"
        cursor.execute(sql)
        enCaminos = 0
        seGuarda = 99999999999999999999999999999999999999999999999999999999999999999999999
        for x in cursor.fetchall():
            if x[0] < seGuarda:
                seGuarda = x[0]
            else:
                sql = f"DELETE FROM historial_estados WHERE id = '{x[0]}';"
                borrados+=1
                try:
                    cursor.execute(sql)
                    midb.commit()
                except Exception as err:
                    errores.append(err)
    cant_err = len(errores)
    if cant_err != 0:
        return f"Se borraron {borrados} y se produjeron {cant_err} errores"
    else:
        return f"Se borraron {borrados}"