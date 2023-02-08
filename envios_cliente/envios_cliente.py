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
    cabezeras = ["Fecha","Numero de envío","Numero de venta","Comprador","Direccion","Estado","Motivo","Observación","Paquete","Monto a cobrar"]
    cursor.execute("select Fecha, Numero_envío, nro_venta, comprador,concat(Direccion,', ',Localidad), estado_envio,Motivo,Observacion,sku,Cobrar from ViajesFlexs where Vendedor = %s order by Fecha Desc", (session.get("user_id"),))
    
    #ESTADOS
    # Listo para salir (Sectorizado)
    # Entregado
    # Fuera de Zona
    # Domicilio Incorrecto
    # Zona Peligrosa
    # Entregado, Buzón/Bajo Puerta

    
    paraRetirar = 0
    sectorizado = 0
    enCamino = 0
    retirado = 0
    for viaje in cursor:
        if viaje[5] == "Lista Para Retirar":
            paraRetirar += 1
        elif viaje[5] == "Listo para salir (Sectorizado)":
            sectorizado += 1
        if viaje[5] == "En Camino":
            enCamino += 1
        if viaje[5] == "Retirado":
            retirado += 1
        viajes.append(viaje)


    message = f"{paraRetirar} Para Retirar || {retirado} Retirados || {sectorizado} Listos para salir || {enCamino} En Camino"
    return render_template("envios_clientes/tabla_viajes.html", 
                            cabezeras = cabezeras,
                            viajes=viajes,
                            mensajeCliente=message,
                            auth = session.get("user_auth"))


@envcl.route("/buscar")
@auth.login_required
def busqueda():
    midb = database.connect_db()
    cursor = midb.cursor()
    busqueda = request.args.get("buscar")
    sql = "select Direccion, Localidad from ViajesFlexs where Numero_envío = %s;"
    values = (busqueda,)
    cursor.execute(sql,values)
    infoviaje = cursor.fetchone()
    print(infoviaje)
    cursor.execute(f"select Fecha,Chofer,Precio,Costo,estado_envio from historial_estados where Numero_envío = '{busqueda}';")
    lista = []
    for x in cursor.fetchall():
        try:
            x[2] = x[2].split(",")[0]
        except:
            mensaje = "introdusca al menos 3 caracteres"
            print("error")
        print(x)
        lista.append(x)
    return render_template("envios_clientes/tabla_viajes.html", 
                            titulo="Busqueda",
                            infoviaje=infoviaje, 
                            viajes=lista, 
                            auth = session.get("user_auth"))


