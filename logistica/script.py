from database import database
from geopy.geocoders import GoogleV3 as api
import os
from threading import Thread
googleMapApi = os.environ.get("googleMapApi")

# import requests
# def geocoder(direccion):
#     result = requests.get(f"http://www.mapquestapi.com/geocoding/v1/address?key=ZGEUQet8O32iwdTkKxhCkQ0ZayJxBVgF&location={direccion}").json()
#     latitude = result['results'][0]["locations"][0]["latLng"]["lat"]
#     longitude = result['results'][0]["locations"][0]["latLng"]["lng"]
#     return (latitude,longitude)

def geocoder(dir):
    geolocator = api(user_agent="appmms", api_key=str(googleMapApi))
    location = geolocator.geocode(dir)
    return location.latitude, location.longitude


def geolocalizarFaltantesback(midatabase):
    midatabase = database.verificar_conexion(midatabase)
    cursor = midatabase.cursor()
    cursor.execute(f"select Numero_envío, Direccion,Localidad,Vendedor from ViajesFlexs where latitud is null or Longitud is null")
    resultado = cursor.fetchall()
    if len(resultado) > 0:
        for x in resultado:
            print(f"geolocaliza {x[0]} {x[1]}, {x[2]} de {x[3]}")
            latlong = geocoder(f"{x[1]}, {x[2]}, Buenos Aires")
            sql = "UPDATE ViajesFlexs SET Direccion_completa = %s,`latitud` = %s, `longitud` = %s WHERE (`Numero_envío` = %s);"
            direccionCompleta = f"{x[1]}, {x[2]}, Buenos Aires"
            values = (direccionCompleta,latlong[0],latlong[1],x[0])
            cursor.execute(sql,values)
            midatabase.commit()

def geolocalizarFaltantes(db):
    t = Thread(target=geolocalizarFaltantesback, args=(db,))
    t.start()
    db.close()
            
