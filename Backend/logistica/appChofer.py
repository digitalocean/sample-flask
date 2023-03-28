
from flask import Blueprint, jsonify, request,send_file,redirect
import json
import os
from github import Github
from threading import Thread
import requests
from Backend.database.database import connect_db
from datetime import datetime,timedelta

pd = Blueprint('pendientes', __name__, url_prefix='/')

def actualizar_estado_logixs(mensajero_id, tipo_operacion, path, contenido, id_ml, recibe_dni="1234567", recibe_nombre="titular"):
    print(str(contenido))
    try:
        sender_id = contenido["sender_id"]
    except:
        sender_id = 123
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(f"select Vendedor,Scanner from ViajesFlexs where Numero_envío = '{id_ml}'")
    resultado = cursor.fetchone()
    print(resultado)
    if len(resultado) > 0:
        nickname = resultado[0].title()
        try:
            sender_id = json.loads(str(resultado[1]).replace("'",'"'))["sender_id"]
        except:
            print("No se encontro hash del qr")
    else:
        info = set(requests.get("https://api.mercadolibre.com/users/"+str(sender_id)))
        nickname = ""
        for infoML in info:
            if "nickname" in str(infoML):
                nickname = (str(infoML).split(",")[1]).split(":")[1]
                nickname = nickname.replace('"','')
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
    print(data)
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print(response.content)
        return "Estado actualizado con éxito en Logixs"
    else:
        print(f"Se produjo un error al actualizar el estado en Logixs: {response.text}")
        return ""
    

@pd.route("/api/users/login",methods=["POST"])
def loginEmpleado():
    dataLogin = request.get_json()
    usser = dataLogin["ussername"]
    password = dataLogin["password"]
    midb = connect_db()
    cursor = midb.cursor()
    sql ="""
    SELECT 
        `empleado`.`id`
    FROM 
        `mmslogis_MMSPack`.`empleado` where correo = %s and dni = %s;
    """
    cursor.execute(sql,(usser,password))
    res = cursor.fetchone()
    midb.close()
    if res != None:
        return jsonify(success=True,message="Inicio de sesion correcto",data=res)
    else:
        return jsonify(success=False,message="password invalid",data=None)


@pd.route("/store/apps/MMSPACK-Reparto")
def descargaAppReparto():
    return send_file("static/debug/RepartoMMS.apk", as_attachment=True)
  
@pd.route("/api/user/appversion",methods=["POST"])
def appVersion():
    token = os.environ.get("TokenGit")
    # Autenticarse con su token de acceso a la API de GitHub
    g = Github(token)
    # Obtener un objeto de repositorio de GitHub
    repo = g.get_repo("Matyacc/appReparto")
    # Obtener el contenido de un archivo especifico
    content = repo.get_contents("app/build.gradle")
    # Decodificar el contenido del archivo
    decoded_content = content.decoded_content.decode('utf-8')
    # Buscar el valor de versionCode en el contenido del archivo
    version_code_index = decoded_content.index("versionCode")
    version_code_start_index = decoded_content.index(" ", version_code_index) + 1
    version_code_end_index = decoded_content.index("\n", version_code_start_index)
    version_code = decoded_content[version_code_start_index:version_code_end_index].strip()
    # devolver el valor de versionCode
    return f"0.0{version_code}"

@pd.route("/ubicacion",methods = ["POST"])
def guardarUbicacion():
    print(request.get_json())
    return "True"

@pd.route("/retirado",methods=["POST"])
def enviosRetirados():
    sql = """select V.Numero_envío,V.Comprador,V.Telefono,V.Direccion,V.Localidad,V.Vendedor,V.Latitud,V.Longitud,V.tipo_envio,choferCorreo(R.chofer),R.fecha from retirado as R inner join ViajesFlexs as V on R.Numero_envío = V.Numero_envío"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    envios = []
    for x in result:
        nEnvio = x[0]
        comprador = x[1]
        telefono = x[2]
        dirCompleta = f"{x[3]}, {x[4]}"
        vendedor = x[5]
        latitud = x[6]
        longitud = x[7]
        tipoEnvio = x[8]
        chofer = x[9]
        fecha = x[10]
        data = {"nEnvio":nEnvio,"comprador":comprador,"telefono":telefono,"direccion":dirCompleta,"vendedor":vendedor,"Latitud":latitud,"Longitud":longitud,"tipoEnvio":tipoEnvio,"chofer":chofer,"fecha":fecha}
        envios.append(data)
    return jsonify(envios)

def hiloRetirar(_midb,_cursor,_envio,_chofer,_data,_location):
    _cursor.execute("""insert into retirado
                            (fecha,hora,Numero_envío,chofer,estado,scanner,Currentlocation) 
                            values(
                                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                                %s,
                                %s,
                                'Retirado',
                                %s,
                                %s);""",
                                (_envio,_chofer,str(_data),_location))
    _midb.commit()
    _midb.close()
    
@pd.route("/retirar",methods=["POST"])
def scannerRetirar():
    data = request.get_json()
    envio = data["id"]
    chofer = data["chofer"]
    location = data["location"]
    del data["chofer"]
    del data["location"]
    try:
        threadActualizaLogixs = Thread(target=actualizar_estado_logixs, args=(1, "retiro", "MMS", data, envio))
        threadActualizaLogixs.start()
    except:
        print("Fallo informe a logixs (Retiro)")
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("SELECT fecha,choferCorreo(chofer) from retirado where Numero_envío = %s limit 1",(envio,))
    resultado = cursor.fetchone()
    if resultado == None:
        t = Thread(target=hiloRetirar, args=(midb,cursor,envio,chofer,data,location))
        t.start()
        return jsonify(success=True,message="Retirado")
    else:
        midb.close()
        return jsonify(success=False,message=f"Ya retirador por {resultado[1]} el {resultado[0]}")

def sectorizar(database,data,zona):
    nenvio = data["id"]
    chofer = data["chofer"]
    location = data["location"]
    del data["chofer"]
    del data["location"]

    cursor = database.cursor()
    cursor.execute(
        """INSERT INTO `mmslogis_MMSPack`.`sectorizado`
                (`id`,`zona`,`fecha`,`hora`,`Numero_envío`,`scanner`,`chofer`,Currentlocation)
            VALUES
                (UUID(),
                %s,
                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                %s,
                %s,
                %s,
                %s);""",(zona,nenvio,str(data),chofer,location))

    database.commit()
    database.close()

@pd.route("/sectorizar",methods=["POST"])
def scannerSectorizar():
    data = request.get_json()
    envio = data["id"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("Select Zona from ViajesFlexs where Numero_envío = %s",(envio,))
    zona = cursor.fetchone()
    midb.close()
    if zona == None:
        zona = " No esta en lista "
    else:
        zona = zona[0]
        t = Thread(target=sectorizar, args=(connect_db(),data,zona))
        t.start()
    return jsonify({"Zona":zona})

@pd.route("/pendienteschofer",methods=["POST"])
def pendientesChofer():
    data = request.get_json()
    chofer = data["chofer"]
    sql = """select V.Numero_envío from ViajesFlexs as V inner join ZonasyChoferes as Z 
                on concat(Z.`nombre Zona`,"/",tipoEnvio) = V.Zona
                where Z.`Nombre Completo` = choferCorreo(%s) and V.estado_envio in ("Lista Para Retirar","Retirado","Listo para salir (Sectorizado)");"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(chofer,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        envios.append(x[0])
    return jsonify(envios)

@pd.route("/pendienteschofer2",methods=["POST"])
def pendientesChofer2():
    data = request.get_json()
    chofer = data["chofer"]
    sql = """select V.Numero_envío,V.Comprador,V.Telefono,V.Direccion,V.Localidad,V.Vendedor,V.Latitud,V.Longitud,V.tipo_envio,V.Chofer,V.Fecha from ViajesFlexs as V inner join ZonasyChoferes as Z 
                on concat(Z.`nombre Zona`,"/",tipoEnvio) = V.Zona
                where Z.`Nombre Completo` = choferCorreo(%s) and V.estado_envio in ("Lista Para Retirar","Retirado","Listo para salir (Sectorizado)");"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(chofer,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        nEnvio = x[0]
        comprador = x[1]
        telefono = x[2]
        dirCompleta = f"{x[3]}, {x[4]}"
        vendedor = x[5]
        latitud = x[6]
        longitud = x[7]
        tipoEnvio = x[8]
        chofer = x[9]
        fecha = x[10]
        data = {"nEnvio":nEnvio,"comprador":comprador,"telefono":telefono,"direccion":dirCompleta,"vendedor":vendedor,"Latitud":latitud,"Longitud":longitud,"tipoEnvio":tipoEnvio,"chofer":chofer,"fecha":fecha}
        envios.append(data)
    return jsonify(envios)

@pd.route("/carga",methods=["POST"])
def cargar():
    data = request.get_json()
    nenvio = data["id"]
    chofer = data["chofer"]
    latlong = data["location"]
    try:
        threadActualizaLogixs = Thread(target=actualizar_estado_logixs, args=(1, "carga", "MMS", data, nenvio))
        threadActualizaLogixs.start()
    except:
        print("Fallo informe a logixs (CARGA)")
    # del data["chofer"]
    # del data["location"]
    status = False
    message = ""
    try:
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(
            """INSERT INTO `mmslogis_MMSPack`.`en_camino`
                    (`id`,`fecha`,`hora`,`Numero_envío`,`chofer`,`scanner`,Currentlocation)
                VALUES
                    (UUID(),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                    ,%s,%s,%s,%s);""",(nenvio,chofer,str(data),latlong))
        midb.commit()
        midb.close()
        status = True
        message = "Cargado"
    except Exception as err:
        print(err)
        status = False
        message = err
    return jsonify(success=status,message=message,envio=nenvio)
  
@pd.route("/mireparto/<usser>")
def miReparto(usser):
    sql = """select Numero_envío,Comprador,Telefono,Direccion,Localidad,Vendedor,Latitud,Longitud,tipo_envio,Chofer,Fecha from ViajesFlexs 
            where estado_envio in ("En Camino","Reasignado") and Correo_chofer = %s"""
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,(usser,))
    result = cursor.fetchall()
    envios = []
    for x in result:
        nEnvio = x[0]
        comprador = x[1]
        telefono = x[2]
        dirCompleta = f"{x[3]}, {x[4]}"
        vendedor = x[5]
        latitud = x[6]
        longitud = x[7]
        tipoEnvio = x[8]
        chofer = x[9]
        fecha = x[10]
        data = {"nEnvio":nEnvio,"comprador":comprador,"telefono":telefono,"direccion":dirCompleta,"vendedor":vendedor,"Latitud":latitud,"Longitud":longitud,"tipoEnvio":tipoEnvio,"chofer":chofer,"fecha":fecha}
        envios.append(data)
    return jsonify(envios)

@pd.route("/entregado",methods=["POST"])
def entregado():
    midb = connect_db()
    cursor = midb.cursor()
    data = request.get_json()
    nroEnvio = data["nEnvio"]
    chofer = data["chofer"]
    location = data["location"]
    foto,motivo,observacion,recibe,dni,quienRecibe = None,None,None,None,None,None
    if "motivo" in data.keys():
        motivo = data["motivo"]
    if "observacion" in data.keys():
        observacion = data["observacion"]
    recibe = None
    dni = None
    if "quienRecibe" in data.keys() and "dni" in data.keys():
        recibe = data["quienRecibe"] 
        dni = data["dni"]
        quienRecibe = f"{recibe} Dni: {dni}"
    try:
        threadActualizaLogixs = Thread(target=actualizar_estado_logixs, args=(1, "entrega", "MMS", data, nroEnvio, dni, recibe))
        threadActualizaLogixs.start()
    except:
        print("Fallo informe a logixs")
    if "image" in data.keys():
            imagen = data["image"]
            sql = """
        INSERT INTO `mmslogis_MMSPack`.`foto_domicilio`
            (`fecha`,
            `hora`,
            `Numero_envío`,
            `ubicacion`,
            `chofer`,
            `foto`)
            VALUES
            (DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
            DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
            %s,
            %s,
            %s,
            %s);
            """
            values = (nroEnvio,location,chofer,imagen)
            cursor.execute(sql,values)
            midb.commit()
            foto = cursor.lastrowid
    sql = """
        update ViajesFlexs set 
        `Check` = null,
        estado_envio = "Entregado",
        Motivo = %s,
        Observacion = %s,
        Recibe_otro = %s,
        Chofer = choferCorreo(%s),
        Correo_chofer = %s,
        Timechangestamp = DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
        Currentlocation = %s,
        Foto_domicilio = %s,
        reprogramaciones = reprogramaciones +1
        where Numero_envío = %s and estado_envio != "Entregado"
        
        """
    values = (motivo,observacion,quienRecibe,chofer,chofer,location,foto,nroEnvio)
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return jsonify(success=True,message="Envio Entregado",envio=nroEnvio)





@pd.route("/noentregado",methods=["POST"])
def noEntregado():
    data = request.get_json()
    nroEnvio = data["nEnvio"]
    chofer = data["chofer"]
    motivo = data["motivo"]
    imagen = data["image"]
    observacion = None
    observacion = data["observacion"]
    if "location" in data.keys():
        location = data["location"]
    else:
        location = None
    foto = ""
    midb = connect_db()
    cursor = midb.cursor()
    sql = """
    INSERT INTO `mmslogis_MMSPack`.`foto_domicilio`
        (`fecha`,
        `hora`,
        `Numero_envío`,
        `ubicacion`,
        `chofer`,
        `foto`)
        VALUES
        (DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
        DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
        %s,
        %s,
        %s,
        %s);
        """
    values = (nroEnvio,location,chofer,imagen)
    cursor.execute(sql,values)
    midb.commit()
    foto = cursor.lastrowid
    sql = """
            update ViajesFlexs 
                set `Check` = null, 
                estado_envio = 'No Entregado', 
                Motivo = %s, 
                Observacion = %s,
                foto_domicilio = %s,
                Timechangestamp = %s,
                Currentlocation = %s,
                reprogramaciones = reprogramaciones+%s
            where 
                Numero_envío = %s 
            and 
                Chofer = choferCorreo(%s)
             and estado_envio != "No Entregado"
            """
    if motivo in ("Nadie en domicilio","Rechazado"):
        reprogramaciones = 1
    else:
        reprogramaciones = 0
    values = (motivo,
              observacion,
              foto,
              datetime.now()-timedelta(hours=3),
              location,
              reprogramaciones,
              nroEnvio,
              chofer)
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return jsonify(success=False,message="Todavia no esta lista esta seccion",envio=nroEnvio)

@pd.route("/imagen",methods = ["POST"])
def subirImagen():
    sql = """
    INSERT INTO `mmslogis_MMSPack`.`foto_domicilio`
        (`fecha`,
        `hora`,
        `Numero_envío`,
        `ubicacion`,
        `chofer`,
        `foto`)
        VALUES
        (DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
        DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
        %s,
        %s,
        %s,
        %s);
        """
    data = request.get_json()
    nroEnvio = data["nEnvio"]
    chofer = data["chofer"]
    imagen = data["image"]
    if "location" in data.keys():
        location = data["location"]
    else:
        location = NotImplementedError
    values = (nroEnvio,location,chofer,imagen)
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return ""

import base64
@pd.route('/foto_rendicion_from_web', methods=['POST'])
def upload():
    image = request.files['image'].read()
    chofer = request.form["chofer"]
    encoded_image = base64.b64encode(image).decode('utf-8')

    # Hacer la solicitud POST a la URL deseada con los datos de la imagen en el cuerpo
    # La URL debe ser reemplazada por la URL a la que deseas enviar los datos de la imagen
    url = "https://www.mmspack.online/foto_rendicion"
    headers = {'Content-type': 'application/json'}
    data = {'chofer':chofer,'image': encoded_image}
    requests.post(url, headers=headers, json=data)

    # Devolver la respuesta de la URL
    return redirect("/historial/rendiciones")

@pd.route("/foto_rendicion",methods = ["POST"])
def subirRendicion():
    sql = """
        insert into foto_rendicion
        (`fecha`,
        `hora`,
        `chofer`,
        `foto`)
        VALUES
        (DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
        DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
        choferCorreo(%s),
        %s);
        """
    data = request.get_json()
    chofer = data["chofer"]
    imagen = data["image"]
    values = (chofer,imagen) 
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return ""