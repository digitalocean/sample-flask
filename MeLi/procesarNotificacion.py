from database import database
from .consultar_envio import consultar_envio
from .script import traducirEstado
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
            if estado == "En Camino":
                print(f"envio {nro_envio} En Camino")
                midb = database.connect_db()
                cursor = midb.cursor()
                cursor.execute(f"select access_token from vinculacion where user_id = {user_id}")
                access_token = cursor.fetchone()[0]
                form_data = {'Authorization': f'Bearer {access_token}', 'Accept-version': 'v1'}
                url = f"https://api.mercadolibre.com/ultron/public/sites/MLA/shipments/{nro_envio}/assignment"
                response =  requests.get(url,headers=form_data)
                response_json = response.json()
                print(response_json)
                User_id = response_json.get("driver_id")
                urlConsultaUsuario = f"https://api.mercadolibre.com/users/{User_id}"
                response2 =  requests.get(urlConsultaUsuario)
                print(response2.json())
                try:
                    print(response2.get("nickname"))
                except:
                    print(f"{nro_envio} no se pudo obterner el chofer")
            if resEnvio == None:
                if tipo_envio == 2:
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