from database import database
import requests

def consultaUsuarioMeLi(userId):
    urlConsultaUsuario = f"https://api.mercadolibre.com/users/{userId}"
    response2 =  requests.get(urlConsultaUsuario).json()
    nickname = response2.get("nickname")
    return response2

def consultaChoferMeli(nro_envio,sender_id):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select access_token from vinculacion where user_id = {sender_id}")
    access_token = cursor.fetchone()[0]
    midb.close()
    form_data = {'Authorization': f'Bearer {access_token}', 'Accept-version': 'v1'}
    url = f"https://api.mercadolibre.com/ultron/public/sites/MLA/shipments/{nro_envio}/assignment"
    response =  requests.get(url,headers=form_data)
    response_json = response.json()
    userId = response_json.get("driver_id")
    response2 =  consultaUsuarioMeLi(userId)
    print(response2)
    if "error" in response2.keys():
        pass
    else:
        nickname = response2.get("nickname")
        midb=database.connect_db()
        cursor = midb.cursor()
        sql = "INSERT INTO `mmslogis_MMSPack`.`enCaminoMeLi`(`fecha`,`hora`,`Numero_envío`,`nickname`,userId)VALUES(current_date(),current_timestamp()-'03:00:00',%s,%s,%s);"
        values = (nro_envio,nickname,userId)
        cursor.execute(sql,values)
        midb.commit()
        midb.close()

def consultaUsuarioMeLi(userId):
    urlConsultaUsuario = f"https://api.mercadolibre.com/users/{userId}"
    response2 =  requests.get(urlConsultaUsuario).json()
    nickname = response2.get("nickname")
    return response2


def traducirEstado(estado):
    if estado == "pending":
        estado = "Pendiente"
    elif estado == "handling":
        estado = "manejo"
    elif estado == "ready_to_ship":
        estado = "Listo para Retirar"
    elif estado == "shipped":
        estado = "En Camino"
    elif estado == "delivered":
        estado = "Entregado"
    elif estado == "not_delivered":
        estado = "no entregado"
    elif estado == "cancelled":
        estado = "Cancelado"
    return estado