#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

import requests
from database import database
from .renovar_token import actualizar_token


# def consultar_registro_ml():
#     midb = db_almagro()
#     cursor = midb.cursor()
#     cursor.execute("select topic, user_id, resource from registro_ml")
#     nros_envios_user_id = []
#     nros_envios = []
#     for x in cursor:
#         topic = x[0]
#         user_id = x[1]
#         ruta_envio = x[2]
#         if topic == "shipments":
#             ruta_envio_split = ruta_envio.split("/")
#             nro_envio = ruta_envio_split[2]
#             paquete = [nro_envio,user_id]
#             if str(nro_envio) in str(nros_envios):
#                 pass
#             else:
#                 nros_envios.append(nro_envio)
#                 nros_envios_user_id.append(paquete)
#     midb.close()
#     return nros_envios_user_id
            

def consultar_envio(nro_envio,idUser):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select access_token from usuario where user_id = {idUser}")
    for x in cursor:
        authorization = x[0]
    midb.close()
    url = f"https://api.mercadolibre.com/shipments/{nro_envio}"
    payload = ""
    headers = {"Authorization": f"Bearer {authorization}"}
    response = requests.request("GET", url, data=payload, headers=headers)
    response_json = response.json()
    if "receiver_address" in response_json.keys():
        dato_envio=response_json["receiver_address"]
        comprador = dato_envio["receiver_name"]
        tipo_envio = response_json["logistic_type"]
        direccion = dato_envio["address_line"]
        city = dato_envio["city"]
        localidad = city["name"]
        referencia = dato_envio["comment"]
        fecha_creacion = response_json["date_created"]
        nro_venta = response_json["order_id"]
        fecha_creacion = str(fecha_creacion)[0:19]
        estado = response_json["status"]
        print(str(nro_envio) + " " + str(direccion) + " " + str(estado + " " + tipo_envio))
        return nro_envio, tipo_envio, direccion, localidad, referencia, estado, comprador, fecha_creacion,nro_venta
    else:
        if actualizar_token(idUser) == True:
            return consultar_envio(nro_envio,idUser)
        else:
            print(f"Error al actualizar access token")
    

# def subir_viajes():
#     nros_envios = []
#     midb = database.connect_db()
#     cursor = midb.cursor()
#     cursor.execute("select Numero_envío from ViajesFlexs")
#     envios = cursor.fetchall()
#     for x in envios:
#         nros_envios.append(x[0])
#     lista = consultar_registro_ml()
#     autentificaciones = []
#     for x in lista:
#         nro_envio = x[0]
#         user_id = x[1]
#         if user_id == "1005118825":
#             continue
#         if str(user_id) in str(autentificaciones):
#             pass
#         else:
#             if midb.open == False:
#                 while midb.open == False:
#                     midb = database.connect_db()
#             else:
#                 cursor = midb.cursor()
#                 cursor.execute("select nickname, access_token from usuario where user_id = '" + str(user_id) + "'")
#                 resultado = cursor.fetchone()
#                 nickname = resultado[0]
#                 access_token = resultado[1]
#                 paquete = [user_id,access_token,nickname]
#                 autentificaciones.append(paquete)
#                 midb.close()
#             for x in autentificaciones:
#                 if x[0] == user_id:
#                     access_token = x[1]
#                     nickname = x[2]
#         if access_token != None:
#             try:
#                 if str(nro_envio) not in str(nros_envios):
#                     viaje = consultar_envio(nro_envio, nickname)
#                     tipo_envio= viaje[1] 
#                     direccion= viaje[2] 
#                     localidad= viaje[3] 
#                     referencia= viaje[4] 
#                     estado = viaje[5]
#                     comprador = viaje[6]
#                     fecha_creacion = viaje[7]
#                     nro_venta = viaje[8]
#                     direccion_concatenada = direccion + ", " + localidad + ", Buenos aires"
#                     try:
#                         while midb.open == False:
#                             midb = database.connect_db()
#                         midb = database.connect_db()
#                         cursor = midb.cursor()
#                         cursor.execute("insert into ViajesFlexs (Fecha, Numero_envío, Direccion, Referencia, Localidad, tipo_envio, Vendedor, estado_envio, comprador,nro_venta,Direccion_Completa) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (fecha_creacion,nro_envio,direccion,referencia,localidad,tipo_envio,nickname,estado,comprador,nro_venta,direccion_concatenada))
#                         midb.commit()
#                         midb.close()
#                         nros_envios.append(x[0])
#                         print("Se agrego el envio nro: " + str(nro_envio))
#                     except:
#                         print("Error en coneccion a base de datos(inser viaje)")
#                 else:
#                     print(str(nro_envio) + " ya cargado")
#             except:
#                 print("Error al consultar envio " + str(nro_envio))




lista_cafeyte = [41283908049, 41282503852, 41282986581, 41283091338, 41283367855, 41283635766, 41280527420, 41280802692, 41280949904, 41281034689, 41281392566, 41278401760, 41278841615, 41275528835, 41275537503, 41275671675, 41273048483, 41273129567, 41273947484, 41275223884, 41270709216, 41270739686, 41271170520, 41271716225, 41271916324, 41269070589, 41270085113, 41267951063, 41268196413, 41268506739, 41268781966, 41263550967, 41263602921, 41261078666, 41261603840, 41261813048, 41262084868, 41259046787, 41259099720, 41259137227, 41256452800, 41258340033, 41254881697, 41255180897, 41253762232, 41253793020, 41251063018, 41251737533, 41252339646, 41248921299, 41246991521, 41247213032, 41239257271, 41234907295, 41216242983]
