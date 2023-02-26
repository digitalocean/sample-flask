#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

from flask import Blueprint, g, render_template, session, request
from datetime import datetime
from auth import auth
from database import database
from datetime import datetime


ahora = (datetime.today())

fecha_hoy = str(ahora.day)+"/"+str(ahora.month)+"/"+str(ahora.year)


envcl = Blueprint('envcl', __name__, url_prefix='/')


@envcl.route("/misenvios")
@auth.login_required
def envios_clientes():
    viajes = []
    midb = database.connect_db()
    cursor = midb.cursor()
    cabezeras = ["Fecha","Numero de envío","Numero de venta","Comprador","Telefono","Direccion","Estado","Motivo","Observación","Paquete","Monto a cobrar"]
    cursor.execute("select Fecha, Numero_envío, nro_venta, comprador,Telefono,concat(Direccion,', ',Localidad), estado_envio,Motivo,Observacion,sku,Cobrar from ViajesFlexs where Vendedor = %s order by Fecha Desc", (session.get("user_id"),))
    paraRetirar = 0
    sectorizado = 0
    enCamino = 0
    retirado = 0
    for viaje in cursor:
        if viaje[6] == "Lista Para Retirar":
            paraRetirar += 1
        elif viaje[6] == "Listo para salir (Sectorizado)":
            sectorizado += 1
        if viaje[6] == "En Camino":
            enCamino += 1
        if viaje[6] == "Retirado":
            retirado += 1
        viajes.append(viaje)


    message = f"{paraRetirar} Para Retirar || {retirado} Retirados || {sectorizado} Listos para salir || {enCamino} En Camino"
    return render_template("envios_clientes/tabla_viajes.html", 
                            cabezeras = cabezeras,
                            viajes=viajes,
                            mensajeCliente=message,
                            auth = session.get("user_auth"))