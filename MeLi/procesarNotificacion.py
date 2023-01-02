from database import database
from logistica.Envio import Envio
from logistica.script import geolocalizarFaltantes
from .consultar_envio import consultar_envio
from .script import traducirEstado,consultaChoferMeli
import requests
def procesarNotificacion(data):
    resource = data.get("resource")
    user_id = data.get("user_id")
    topic = data.get("topic")
    if str(topic) == "shipments":
        nro_envio = (resource.split("/"))[2]
        midb = database.connect_db()
        cursor = midb.cursor()
        resEnvio = Envio.fromDB(nro_envio)
        cursor.execute("select apodoOcliente(apodo(%s))",(user_id,))
        vendedor = cursor.fetchone()[0]
        midb.close()
        viaje = consultar_envio(nro_envio, user_id)
        if viaje != None:
            tipo_envio= viaje[1]
            if tipo_envio == "self_service": tipo_envio = 2 
            estado = traducirEstado(viaje[5])
            if resEnvio == False:
                if tipo_envio == 2:
                    envio = Envio(viaje[2],viaje[3],vendedor,viaje[0],viaje[6],tipoEnvio=tipo_envio,referencia=viaje[4],fecha=viaje[7],numeroVenta=viaje[8])
                    if envio.toDB(): 
                        print(f"Envio: {nro_envio} Agregado")
                        geolocalizarFaltantes(database.connect_db())
            else:
                if estado == "En Camino": consultaChoferMeli(nro_envio,user_id)
                estadoDb = resEnvio.estado_envio
                if tipo_envio == 2 and estadoDb != estado and estado == "Cancelado":
                    resEnvio.cambioEstado("cancelado",None)
                    print(f"Envio {nro_envio} cancelado")
                else:
                    print(f"Envio {nro_envio} descartado se encuentra {estado} y en nuestra db {estadoDb}")
                    print(f"Tipo de envio: {tipo_envio}")

