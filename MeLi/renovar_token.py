import requests
from database import database
from datetime import datetime

def actualizar_token(idUser):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select user_id, refresh_token from usuario where user_id = {idUser}")
    user = []
    resultado = cursor.fetchone()    
    if resultado[1] != None:
        id_user = [resultado[0],resultado[1]]
        user.append(id_user)
    print(user)
    try:
        data = {
            "grant_type":"authorization_code",
            "client_id":4857198121733101,
            "client_secret":"rsH5HedyMwFMjRm2aaAb8jFN1McNUW9c",
            "code": user[1] ,
            "redirect_uri":"https://www.mmspack.com/callbacks"
        }
        respuesta_ML = requests.post("https://api.mercadolibre.com/oauth/token", data).json()
        user_id = respuesta_ML["user_id"]
        access_token = respuesta_ML["access_token"]
        refresh_token = respuesta_ML["refresh_token"]
        sql = f"UPDATE usuario SET access_token = '{access_token}', refresh_token = '{refresh_token}' WHERE user_id = {idUser};"
        print(sql)
        cursor.execute(sql)
        midb.commit()
    except:
        try:
            data = {
                "grant_type":"refresh_token",
                "client_id":4857198121733101,
                "client_secret":"rsH5HedyMwFMjRm2aaAb8jFN1McNUW9c",
                "refresh_token": id_user[1]
            }
            respuesta_ML = requests.post("https://api.mercadolibre.com/oauth/token", data).json()
            print(respuesta_ML)
            access_token = respuesta_ML["access_token"]
            refresh_token = respuesta_ML["refresh_token"]
        except Exception as postML:
            print(postML)
        try:
            cursor.execute("UPDATE usuario SET access_token = '"+str(access_token)+"', refresh_token = '"+str(refresh_token)+"' WHERE nickname = '"+str(idUser)+"';")
            midb.commit()
            cursor.execute("UPDATE usuario SET ultima_actualizacion =  CURRENT_TIMESTAMP() WHERE nickname = '"+str(idUser)+"';")
            midb.commit()

        except Exception as a:
            print(a)
    midb.close()
    print(idUser)
    print("actualizado")
    print(str(datetime.now())[0:19])
