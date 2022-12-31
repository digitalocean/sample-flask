from database import database
from geopy.geocoders import GoogleV3 as api
import requests


def geocoder(direccion):
    result = requests.get(f"http://www.mapquestapi.com/geocoding/v1/address?key=ZGEUQet8O32iwdTkKxhCkQ0ZayJxBVgF&location={direccion}").json()
    latitude = result['results'][0]["locations"][0]["latLng"]["lat"]
    longitude = result['results'][0]["locations"][0]["latLng"]["lng"]
    return (latitude,longitude)

# def geocoder(dir):
#     geolocator = api(user_agent="appmms", api_key="AIzaSyAt-xZYW0smZUbe2xh95M06EqmYPfnZRYQ-bNHfsw7RChXg")
#     location = geolocator.geocode(dir)
#     return location.latitude, location.longitude

def geolocalizarFaltantes(midatabase):
    cursor = midatabase.cursor()
    cursor.execute(f"select Numero_envío, Vendedor, Direccion_Completa,Direccion,Localidad from ViajesFlexs where latitud is null and Fecha >= current_date()-3")
    resultado = cursor.fetchall()
    if len(resultado) > 0:
        for x in resultado:
            latlong = geocoder(f"{x[1]}, {x[2]}, Buenos Aires")
            sql = "UPDATE ViajesFlexs SET `latitud` = %s, `longitud` = %s WHERE (`Numero_envío` = %s);"
            values = (latlong[0],latlong[1],x[0])
            cursor.execute(sql,values)
            midatabase.commit()
            
