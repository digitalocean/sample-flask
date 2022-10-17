import requests
from datetime import datetime
def descargaLogixs(midatabase):
    contadorAgregados = 0
    contadorActualizadosLogixs = 0
    enviosLogixsNuevos = ""
    enviosLogixs = ""
    dicNrosEnviosDB = {}
    cursor = midatabase.cursor()
    cursor.execute("select Numero_envío,estado_envio from ViajesFlexs")
    for x in cursor.fetchall():
        dicNrosEnviosDB[str(x[0])]=str(x[1])
    url = "https://logixs.com.ar/mms/envioflex/JsonPosicionesPendientesDeRetiro?id_envio=0"
    r = requests.get(url)
    jsonData = r.json()
    
    for x in jsonData:
        nroEnvio = x['id_paquete']
        estado = str(x['Estado']).replace("'"," ")
        fecha_entrega = str(x['EntregaEstimada'])
        dia = fecha_entrega[0:2]
        mes = fecha_entrega[3:5]
        year = fecha_entrega[6:10]
        fecha_entrega = f"{year}-{mes}-{dia}"
        #si el envio del json se encuentra en DB
        if nroEnvio in dicNrosEnviosDB.keys():
            if estado == "Lista Para Retirar":
                continue
            if dicNrosEnviosDB[nroEnvio].lower() in ("listo para retirar","lista para retirar", "No Vino"):
                enviosLogixs += f"'{nroEnvio}',"
                contadorActualizadosLogixs += 1
        #si el numero de envio del json no se encuentra en DB
        else:
            contadorAgregados +=1
            referencia = str(x['Comment']).replace("'"," ")
            vendedor = str(x['Nickname_Vend']).replace("'"," ")
            comprador = str(x['Nombre_Destino']).replace("'"," ")
            direccion = str(x['Dir_Destino'])
            if "," in direccion:
                direccion = direccion.split(",")[0]
            direccion = direccion.replace("'"," ")
            cp = str(x['Cp_Destino']).replace("'"," ")
            telefono = str(x['Tel_Destino']).replace("'"," ")
            localidad = str(x['Barrio']).replace("'"," ")
            latitud = str(x['Lat']).replace("'"," ")
            longitud = str(x['Lng']).replace("'"," ")
            referencia = str(referencia).replace("\n", " ")
            direccionCompleta = f"{direccion}, {localidad}, Buenos aires"
            enviosLogixsNuevos += f"('{fecha_entrega}', '{nroEnvio}', '{comprador}', '{telefono}', '{direccion}', '{referencia}', '{localidad}', '{cp}', '{vendedor}', '{direccionCompleta}', '{latitud}', '{longitud}', '{estado}',2),"
    if len(enviosLogixsNuevos) > 0:
        enviosLogixsNuevos = enviosLogixsNuevos[0:-1]
        sql_insert = f"INSERT IGNORE INTO ViajesFlexs (Fecha, Numero_envío, comprador, Telefono, Direccion, Referencia, Localidad, CP, Vendedor, Direccion_Completa, Latitud, Longitud, estado_envio, tipo_envio) VALUES {enviosLogixsNuevos}"
        cursor.execute(sql_insert)
        midatabase.commit()
    if len(enviosLogixs) > 0:
        enviosLogixs = enviosLogixs[0:-1]
        sql_update = f"update ViajesFlexs set estado_envio = 'Retirado',Fecha = current_date() where Numero_envío in ({enviosLogixs})"
        cursor.execute(sql_update)
        midatabase.commit()
    print(f"{contadorAgregados} viajes agregados")
    print(f"{contadorActualizadosLogixs} actualizados desde logixs")



