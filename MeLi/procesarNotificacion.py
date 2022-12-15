from database import database
from .consultar_envio import consultar_envio
from .script import traducirEstado,consultaChoferMeli,agregarEnvio
import requests
def procesarNotificacion(data):
    resource = data.get("resource")
    user_id = data.get("user_id")
    topic = data.get("topic")
    received = data.get("received")
    attempts = data.get("attempts")
    application_id = data.get("application_id")
    sent = data.get("sent")
    if str(topic) == "shipments":
        nro_envio = (resource.split("/"))[2]
        midb = database.connect_db()
        cursor = midb.cursor()
        sqlEnvio = f"select Numero_envío,estado_envio from ViajesFlexs where Numero_envío = '{nro_envio}'" 
        cursor.execute(sqlEnvio)
        resEnvio = cursor.fetchone()
        midb.close()
        viaje = consultar_envio(nro_envio, user_id)
        if viaje != None:
            tipo_envio= viaje[1]
            if tipo_envio == "self_service": tipo_envio = 2 
            estado = traducirEstado(viaje[5])
            if resEnvio == None:
                if tipo_envio == 2: agregarEnvio(viaje,nro_envio,user_id)
            else:
                if estado == "En Camino": consultaChoferMeli(nro_envio,user_id)
                estadoDb = resEnvio[1]
                if tipo_envio == 2 and estadoDb != estado and estado == "Cancelado":
                    midb = database.connect_db()
                    cursor = midb.cursor()
                    sqlCancelado = f"update ViajesFlexs set estado_envio = '{estado}', Motivo = 'Venta cancelada' where Numero_envío = '{nro_envio}'"
                    cursor.execute(sqlCancelado)
                    midb.commit()
                    print(f"Envio {nro_envio} cancelado")
                else:
                    print(f"Envio {nro_envio} descartado se encuentra {estado} y en nuestra db {estadoDb}")
                    print(f"Tipo de envio: {tipo_envio}")

