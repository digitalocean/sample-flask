import pymysql
import requests
from datetime import datetime

def actualizar_token(nickname):

    midb = pymysql.connect(
        host='190.228.29.62', 
        user='matyacc', 
        passwd='Agustin_1504', 
        db='viajesbarracas', 
        charset = 'utf8mb4')

    cursor = midb.cursor()
    cursor.execute("select user_id, refresh_token from usuario where nickname = '" + nickname + "'")
    user = []
    resultado = cursor.fetchone()    
    if resultado[1] != None:
        iduser = [resultado[0],resultado[1]]
        user.append(iduser)
    print(user)
    file = open("refres_token.txt", "a")
    file.write(str(datetime.now()))
    file.write("\n")
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
        try:
            file.write("intento de cargar db = ")
            cursor.execute("UPDATE usuario SET user_id = "+str(user_id)+", access_token = '"+str(access_token)+"', refresh_token = '"+str(refresh_token)+"' WHERE nickname = '"+str(nickname)+"';")
            print(nickname)
            midb.commit()
            file.write("exito\n")
            file.write("datos guardados")
        except:
            file.write("no se pudo refrescar el access_token del user_id " + str(user_id))
            file.write(nickname)
            file.close()
    except:
        try:
            try:
                data = {
                    "grant_type":"refresh_token",
                    "client_id":4857198121733101,
                    "client_secret":"rsH5HedyMwFMjRm2aaAb8jFN1McNUW9c",
                    "refresh_token": iduser[1]
                }
                respuesta_ML = requests.post("https://api.mercadolibre.com/oauth/token", data).json()
                print(respuesta_ML)
                access_token = respuesta_ML["access_token"]
                refresh_token = respuesta_ML["refresh_token"]
            except:
                file.write("\nerror de llaves")
            try:
                cursor.execute("UPDATE usuario SET access_token = '"+str(access_token)+"', refresh_token = '"+str(refresh_token)+"' WHERE nickname = '"+str(nickname)+"';")
                midb.commit()
                cursor.execute("UPDATE usuario SET ultima_actualizacion =  CURRENT_TIMESTAMP() WHERE nickname = '"+str(nickname)+"';")
                midb.commit()
                file.write("exito\n")
                file.write("datos guardados")
            except:
                file.write("\nError al interactuar con la base de datos al intentar refrescar token")
        
        except:
            file.write("\nFallo refrescar access_token")
        file.close()
    midb.close()
    print(nickname)
    print("actualizado")
    print(str(datetime.now())[0:19])
