import requests
import json
from Backend.database.database import connect_db
def actualizar_estado_logixs(mensajero_id, tipo_operacion, path, contenido, id_ml, recibe_dni="1234567", recibe_nombre="titular"):
    nickname = ""
    resultado = None
    if "sender_id" in contenido.keys():
        sender_id = contenido["sender_id"]
        info = set(requests.get("https://api.mercadolibre.com/users/"+str(sender_id)))
        for infoML in info:
            if "nickname" in str(infoML):
                nickname = (str(infoML).split(",")[1]).split(":")[1]
                nickname = nickname.replace('"','')
    else:
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(f"select V.Vendedor,ifnull(R.scanner,ifnull(S.scanner,ifnull(EC.scanner,V.Scanner))) as scanner from ViajesFlexs as V left join retirado as R on V.Numero_envío = R.Numero_envío left join sectorizado as S on V.Numero_envío = S.Numero_envío left join en_camino as EC on V.Numero_envío = EC.Numero_envío where V.Numero_envío = '{id_ml}' limit 1")
        resultado = cursor.fetchone()
        if resultado != None:
            sender_id = json.loads(str(resultado[1]).replace("'",'"'))["sender_id"]
            nickname = resultado[0].title()
        else:
            print("No se obtuvo sender_id")
    url = f"https://www.logixs.com.ar/{path}/envioflex/RecibirScanQR"
    data = {
        "MensajeroId": mensajero_id,
        "EntregaOretiro": tipo_operacion,
        "Path": path,
        "Scan": str(contenido),
        "IdML": id_ml,
        "Nickname": nickname,
        "Sender_id": sender_id,
        "recibeDNI": recibe_dni,
        "RecibeNombre": recibe_nombre
    }
    response = requests.post(url, data=data)
    print(data)
    if response.status_code == 200:
        print(response.content)
        return "Estado actualizado con éxito en Logixs"
    else:
        print(f"Se produjo un error al actualizar el estado en Logixs: {response.text}")
        return ""
   