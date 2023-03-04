#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from flask import Blueprint, g, render_template, session, request
from datetime import datetime
from Backend.auth import auth
from Backend.database import database
from datetime import datetime,timedelta
from Backend.scriptGeneral.scriptGeneral import consultar_clientes


ahora = (datetime.today())

fecha_hoy = str(ahora.day)+"/"+str(ahora.month)+"/"+str(ahora.year)

envcl = Blueprint('envcl', __name__, url_prefix='/')


def verEnvios(_vendedor,_desde,_hasta):
    viajes = []
    midb = database.connect_db()
    cursor = midb.cursor()
    cabezeras = ["Fecha","Numero de envío","Numero de venta","Comprador","Telefono","Direccion","Estado","Motivo","Observación","Paquete","Monto a cobrar"]
    cursor.execute("select Fecha, Numero_envío, nro_venta, comprador,Telefono,concat(Direccion,', ',Localidad), estado_envio,Motivo,Observacion,sku,Cobrar from ViajesFlexs where Vendedor = %s and Fecha between %s and %s order by Fecha Desc", (_vendedor,_desde,_hasta))
    paraRetirar = 0
    sectorizado = 0
    enCamino = 0
    retirado = 0
    entregado = 0
    noentregado = 0
    listaParaDevolver = 0
    devuelto = 0
    otros = 0
    noVino = 0
    cancelados = 0
    total = 0
    for viaje in cursor:
        total += 1
        if viaje[6] == "Lista Para Retirar":
            paraRetirar += 1
        elif viaje[6] == "Listo para salir (Sectorizado)":
            sectorizado += 1
        elif viaje[6] in ["En Camino","Reasignado"]:
            enCamino += 1
        elif viaje[6] == "Retirado":
            retirado += 1
        elif viaje[6] == "Entregado":
            entregado += 1
        elif viaje[6] in ["No Entregado","Dirección Incorrecta"]:
            noentregado +=1
        elif viaje[6] == "Lista para Devolver":
            listaParaDevolver += 1
        elif viaje[6] == "devuelto":
            devuelto += 1
        elif viaje[6] == "No Vino":
            noVino += 1
        elif viaje[6] == "Cancelado":
            cancelados += 1
        else:
            otros += 1
            print(f"Estado desconocido: -> {viaje[6]}")
        viajes.append(viaje)
    message = f"{paraRetirar} Para Retirar || {retirado} Retirados || {sectorizado} Listos para salir || {enCamino} En Camino || {entregado} Entregados || {noentregado} No entregados"
    if session.get("user_auth") != "Cliente":        
        message = f"""{_vendedor} --> 
                        {total} Total ||
                        {paraRetirar} Para Retirar || 
                        {retirado} Retirados || 
                        {sectorizado} Listos para salir || 
                        {enCamino} En Camino || 
                        {entregado} Entregados || 
                        {noentregado} No entregados || 
                        {listaParaDevolver} Para devolver || 
                        {devuelto} devueltos || 
                        {noVino} No Vino || 
                        {cancelados} Cancelados"""
        if otros > 0:
            message += f" || {otros} Otros"
    return cabezeras,viajes,message

@envcl.route("/envios", methods=["GET","POST"])
@auth.login_required
def envios_clientes():
    desde = str(datetime.now()-timedelta(days=15))[0:10]
    hasta = str(datetime.now()+timedelta(days=7))[0:10]
    vendedores = []
    vendedor = session.get("user_id")
    if request.method == "POST":
        desde = request.form.get("desde")
        hasta = request.form.get("hasta")
        if session.get("user_auth") != "Cliente":
            vendedor = request.form.get("vendedor")
            vendedores = consultar_clientes(database.connect_db())
        cabezeras,viajes,message = verEnvios(vendedor,desde,hasta)
        return render_template("envios_clientes/tabla_viajes.html", 
                            cabezeras = cabezeras,
                                    desde = desde,
                                    hasta = hasta,
                                    viajes=viajes,
                                    mensajeCliente=message,
                                    vendedores = vendedores,
                                    auth = session.get("user_auth"))
    else:
        cabezeras,viajes,message = verEnvios(vendedor,datetime.now()-timedelta(days=15),datetime.now()+timedelta(days=7))
        if session.get("user_auth") != "Cliente":
            vendedores = consultar_clientes(database.connect_db())
        return render_template("envios_clientes/tabla_viajes.html", 
                            cabezeras = cabezeras,
                                    desde = desde,
                                    hasta = hasta,
                                    viajes=viajes,
                                    mensajeCliente=message,
                                    vendedores=vendedores,
                                    auth = session.get("user_auth"))