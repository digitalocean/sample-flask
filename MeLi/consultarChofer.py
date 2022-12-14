import requests
import database
def consultaChoferMeli(nro_envio,user_id):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select access_token from vinculacion where user_id = {user_id}")
    access_token = cursor.fetchone()[0]
    midb.close()
    form_data = {'Authorization': f'Bearer {access_token}', 'Accept-version': 'v1'}
    url = f"https://api.mercadolibre.com/ultron/public/sites/MLA/shipments/{nro_envio}/assignment"
    response =  requests.get(url,headers=form_data)
    response_json = response.json()
    User_id = response_json.get("driver_id")
    urlConsultaUsuario = f"https://api.mercadolibre.com/users/{User_id}"
    response2 =  requests.get(urlConsultaUsuario).json()
    print(response2)
    if "error" in response2.keys():
        pass
    else:
        nickname = response2.get("nickname")
        midb=database.connect_db()
        cursor = midb.cursor()
        sql = "INSERT INTO `mmslogis_MMSPack`.`enCaminoMeLi`(`fecha`,`hora`,`Numero_envío`,`nickname`,userId)VALUES(current_date(),current_timestamp()-'03:00',%s,%s,%s);"
        values = (nro_envio,nickname,User_id)
        cursor.execute(sql,values)
        midb.commit()
        midb.close()
