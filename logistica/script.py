from database import database
from geopy.geocoders import GoogleV3 as api


def geocoder(dir):
    geolocator = api(user_agent="appmms", api_key="AIzaSyD3CqHvT0eiesSF0kuzId-bNHfsw7RChXg")
    location = geolocator.geocode(dir)
    return location.latitude, location.longitude

def geolocalizarFaltantes(midatabase):
    cursor = midatabase.cursor()
    cursor.execute(f"select Numero_envío, Vendedor, Direccion_Completa from ViajesFlexs where latitud is null and Fecha >= current_date()-3")
    resultado = cursor.fetchall()
    if len(resultado) > 0:
        for x in resultado:
            try:
                database.verificar_conexion(midatabase)
                latlong = geocoder(x[2])
                sql = f"UPDATE ViajesFlexs SET `latitud` = '{latlong[0]}', `longitud` = '{latlong[1]}' WHERE (`Numero_envío` = '{x[0]}');"
                cursor.execute(sql)
                midatabase.commit()
            except Exception as err:
                database.verificar_conexion(midatabase)
                cursor.execute("UPDATE ViajesFlexs SET Direccion_Completa = concat(concat(Direccion,', '),concat(Localidad,', Buenos Aires')) where Direccion_Completa is null and Numero_envío = Numero_envío")
                database.commit()
                latlong = geocoder(x[2])
                sql = f"UPDATE ViajesFlexs SET `latitud` = '{latlong[0]}', `longitud` = '{latlong[1]}' WHERE (`Numero_envío` = '{x[0]}');"
                try:
                    cursor.execute(sql)
                    midatabase.commit()
                except:
                    print(f"Error en {x[0]} al intentar geolocalizar \n {err}")