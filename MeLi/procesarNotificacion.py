from database import database
from .consultar_envio import consultar_envio
from .script import traducirEstado,consultaChoferMeli
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
            direccion= viaje[2] 
            localidad= viaje[3] 
            referencia= viaje[4]
            estado = traducirEstado(viaje[5])
            comprador = viaje[6]
            fecha_creacion = viaje[7]
            nro_venta = viaje[8]
            direccion_concatenada = direccion + ", " + localidad + ", Buenos aires"
            if estado == "En Camino": consultaChoferMeli(nro_envio,user_id);
            if resEnvio == None and tipo_envio == 2:
                midb = database.connect_db()
                cursor = midb.cursor()
                sql = """insert into ViajesFlexs 
                            (Fecha, Numero_envío, Direccion, Referencia, Localidad, tipo_envio, Vendedor, estado_envio, comprador,nro_venta,Direccion_Completa) 
                        values
                            (%s,%s,%s,%s,%s,2,apodoOcliente(apodo(%s)),%s,%s,%s,%s)"""
                values = (fecha_creacion,nro_envio,direccion,referencia,localidad,user_id,"Listo para retirar",comprador,nro_venta,direccion_concatenada)
                cursor.execute(sql,values)
                midb.commit()
                print(f"Envio: {nro_envio} Agregado")
            else:
                estadoDb = resEnvio[1]
                if tipo_envio == 2 and estadoDb != estado and estado in ("Cancelado","Listo para retirar"):
                    midb = database.connect_db()
                    cursor = midb.cursor()
                    sqlCancelado = f"update ViajesFlexs set estado_envio = '{estado}', Motivo = 'Venta cancelada' where Numero_envío = '{nro_envio}'"
                    cursor.execute(sqlCancelado)
                    midb.commit()
                    print(f"Envio {nro_envio} cancelado")
                else:
                    print(f"Envio {nro_envio} descartado se encuentra {estado} y en nuestra db {estadoDb}")
                    print(f"Tipo de envio: {tipo_envio}")

