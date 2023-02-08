import requests
from database import database
from scriptGeneral import scriptGeneral

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
        else:
            cursor.execute("""
                            select 
                                    V.status,V.reported,V.nickname,C.correo_electronico from vinculacion as V 
                            inner join 
                                `Apodos y Clientes` as AyP 
                            on 
                                V.user_id = AyP.sender_id
							inner join 
								Clientes as C
							on AyP.id_cliente = C.idClientes
                            where 
                                V.user_id = %s""",(idUser,))
            resuEstado = cursor.fetchone()
            status = resuEstado[0]
            reported = resuEstado[1]
            cuentaML = resuEstado[2]
            correoCliente = resuEstado[3]
            if status == "Correcto" and reported == "No":
                cursor.execute("update vinculacion set status = 'Fallo' where user_id = %s",(idUser,))
                midb.commit()
                status = "Fallo"
            if status == "Fallo" and reported == "No":
                avisoCliente = "Se envio un correo automatico al cliente"
                if correoCliente == None:
                    avisoCliente = "se debe enviar la solicitud nuevamente"    
                scriptGeneral.enviar_correo(["mmsmatiasacciaio@gmail.com","mmspackcheck@gmail.com","josudavidg@gmail.com","sistemas@mmslogistica.com"],
                                            f"Error en vinculacion con {cuentaML}",
                                            None,
                                            None,
                                            f"Se produjo un error con la vinculacion de la cuenta {cuentaML}, {avisoCliente}")
                scriptGeneral.enviar_correo([correoCliente],
                                            "Accion necesaria",
                                            None,None,
                                            f"""Se produjo un error en la vinculación entre su cuenta {cuentaML} de mercadolibre y MMS Pack, para restablecer la vinculacion ingrese al siguiente <a href='https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=4857198121733101&redirect_uri=https://whale-app-suwmc.ondigitalocean.app/callbacks'>enlase</a>""")
                cursor.execute("update vinculacion set reported = 'Yes' where user_id = %s",(idUser,))
                midb.commit()
