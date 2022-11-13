import requests
from database import database
from datetime import datetime

def actualizar_token(idUser):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select user_id, refresh_token from vinculacion where user_id = {idUser}")
    user = []
    resultado = cursor.fetchone()   
    if resultado != None:
        id_user = [resultado[0],resultado[1]]
        user.append(id_user)
        data = {
            "grant_type":"authorization_code",
            "client_id":4857198121733101,
            "client_secret":"LHTeBl8PL4BXCk4f6v5jvbokxP04hOli",
            "code": user[0][1],
            "redirect_uri":"https://whale-app-suwmc.ondigitalocean.app/callbacks"
        }
        respuesta_ML = requests.post("https://api.mercadolibre.com/oauth/token", data).json()
        if "user_id" in respuesta_ML.keys():
            user_id = respuesta_ML["user_id"]
            access_token = respuesta_ML["access_token"]
            refresh_token = respuesta_ML["refresh_token"]
            sql = f"UPDATE vinculacion SET access_token = '{access_token}', refresh_token = '{refresh_token}', ultima_actualizacion =  CURRENT_TIMESTAMP() WHERE user_id = {idUser};"
            cursor.execute(sql)
            midb.commit()
            return True
        else:
            data = {
                "grant_type":"refresh_token",
                "client_id":4857198121733101,
                "client_secret":"LHTeBl8PL4BXCk4f6v5jvbokxP04hOli",
                "refresh_token": id_user[1]
            }
            respuesta_ML = requests.post("https://api.mercadolibre.com/oauth/token", data).json()
            if "access_token" in respuesta_ML.keys():
                access_token = respuesta_ML["access_token"]
                refresh_token = respuesta_ML["refresh_token"]
                sql = f"UPDATE vinculacion SET access_token = '{access_token}', refresh_token = '{refresh_token}', ultima_actualizacion =  CURRENT_TIMESTAMP() WHERE user_id = {idUser};"
                cursor.execute(sql)
                midb.commit()
                midb.close()
                return True
            return False
