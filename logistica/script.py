from database import database
from geopy.geocoders import GoogleV3 as api


def geocoder(dir):
    geolocator = api(user_agent="appmms", api_key="AIzaSyAL5RgvjJ6CwjnKgQXO921voodcystsUlQ")
    location = geolocator.geocode(dir)
    return location.latitude, location.longitude

def geolocalizarFaltantes(midatabase):
    cursor = midatabase.cursor()
    cursor.execute(f"select Numero_envío, Vendedor, Direccion_Completa from ViajesFlexs where latitud is null and not estado_envio in ('Entregado','Cancelado','No Vino') and not Motivo in ('Cancelado')")
    resultado = cursor.fetchall()
    if len(resultado) > 0:
        for x in resultado:
            database.verificar_conexion(midatabase)
            latlong = geocoder(x[2])
            print(latlong)
            sql = f"UPDATE ViajesFlexs SET `latitud` = '{latlong[0]}', `longitud` = '{latlong[1]}' WHERE (`Numero_envío` = '{x[0]}');"
            cursor.execute(sql)
            midatabase.commit()
        print(f"{len(resultado)} direcciones geolicalizadas")
    else: print("No se encontraron direcciones sin coordenadas")