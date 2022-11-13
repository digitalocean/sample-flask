#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# encoding: utf-8

import requests
from database import database
from .renovar_token import actualizar_token

 

def consultar_envio(nro_envio,idUser):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select access_token from usuario where user_id = {idUser}")
    resultado = cursor.fetchone()
    midb.close()
    if resultado != None:
        authorization = resultado[0]
        # url = f"https://api.mercadolibre.com/shipments/{nro_envio}"
        # payload = ""
        # headers = {"Authorization": f"Bearer {authorization}"}
        # response = requests.request("GET", url, data=payload, headers=headers)
        url = f"https://api.mercadolibre.com/shipments/{nro_envio}?access_token={authorization}"
        response =  requests.get(url)
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
            return nro_envio, tipo_envio, direccion, localidad, referencia, estado, comprador, fecha_creacion,nro_venta
        else:
            if actualizar_token(idUser) == True:
                print("Se actualizo el access token")
                # return consultar_envio(nro_envio,idUser)
            else:
                print(f"Error al actualizar access token")
    else:
        print("no se encontro el sender_id en nuestra base de datos")
    
