import requests
from database import database

def actualizar_token(idUser):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select refresh_token from vinculacion where user_id = {idUser}")
    user = []
    resultado = cursor.fetchone()   
    if resultado != None:
        data = {
            "grant_type":"refresh_token",
            "client_id":4857198121733101,
            "client_secret":"LHTeBl8PL4BXCk4f6v5jvbokxP04hOli",
            "refresh_token": resultado[0]
        }
        respuesta_ML = requests.post("https://api.mercadolibre.com/oauth/token", data).json()
        if "access_token" in respuesta_ML.keys():
            access_token = respuesta_ML["access_token"]
            refresh_token = respuesta_ML["refresh_token"]
            sql = f"""
                        UPDATE 
                            vinculacion 
                        SET 
                            access_token = '{access_token}', 
                            refresh_token = '{refresh_token}', 
                            ultima_actualizacion =  CURRENT_TIMESTAMP() 
                        WHERE 
                            user_id = {idUser};"""

                            
            cursor.execute(sql)
            midb.commit()
            midb.close()
            return True
        return False