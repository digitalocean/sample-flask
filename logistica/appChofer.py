
from flask import Blueprint, jsonify, request,send_file
from threading import Thread
import requests
from database.database import connect_db
from datetime import datetime,timedelta

pd = Blueprint('pendientes', __name__, url_prefix='/')


@pd.route("/api/users/login",methods=["POST"])
def loginEmpleado():
    dataLogin = request.get_json()
    usser = dataLogin["ussername"]
    password = dataLogin["password"]
    print(usser," ",password)
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

@pd.route('/version')
def get_latest_version():
    TOKEN_GIT = "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"
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'token {TOKEN_GIT}'
    }
    url = f'https://api.github.com/repos//Matyacc/appReparto/blob/main/app/build.gradle'
    response = requests.get(url, headers=headers)


    if response.status_code == 200:
        release_info = response.json()
        return str(release_info['tag_name'])
    else:
        return 'Error getting latest version'
    
@pd.route("/api/user/appversion",methods=["POST"])
def appVersion():
    
    "https://github.com/Matyacc/appReparto/blob/main/app/build.gradle"
    return "0.01"

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


@pd.route("/retirar",methods=["POST"])
def scannerRetirar():
    data = request.get_json()
    envio = data["id"]
    sender_id = data["sender_id"]
    chofer = data["chofer"]
    del data["chofer"]
    if "location" in data.keys():
        del data["location"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("SELECT fecha,choferCorreo(chofer) from retirado where Numero_envío = %s limit 1",(envio,))
    resultado = cursor.fetchone()
    print(resultado)
    if resultado == None:
        cursor.execute("insert into retirado(fecha,hora,Numero_envío,chofer,estado,scanner) values(DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),%s,%s,'Retirado',%s);",(envio,chofer,str(data)))
        midb.commit()
        midb.close()
        return jsonify(success=True,message="Retirado")
    else:
        midb.close()
        return jsonify(success=False,message=f"Ya retirador por {resultado[1]} el {resultado[0]}")

def sectorizar(database,data,zona):
    nenvio = data["id"]
    try:
        chofer = data["chofer"]
        del data["chofer"]
    except:
        chofer = data["Chofer"]
        del data["Chofer"]
    cursor = database.cursor()
    cursor.execute(
        """INSERT INTO `mmslogis_MMSPack`.`sectorizado`
                (`id`,`zona`,`fecha`,`hora`,`Numero_envío`,`scanner`,`chofer`)
            VALUES
                (UUID(),%s,DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                ,%s,%s,%s);""",(zona,nenvio,str(data),chofer))

    database.commit()
    database.close()

@pd.route("/sectorizar",methods=["POST"])
def scannerSectorizar():
    data = request.get_json()
    print(data)
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

@pd.route("/carga",methods=["POST"])
def cargar():
    data = request.get_json()
    nenvio = data["id"]
    chofer = data["chofer"]

    status = False
    message = ""
    try:
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(
            """INSERT INTO `mmslogis_MMSPack`.`en_camino`
                    (`id`,`fecha`,`hora`,`Numero_envío`,`chofer`,`scanner`)
                VALUES
                    (UUID(),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                    ,%s,%s,%s);""",(nenvio,chofer,str(data)))
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
    data = request.get_json()
    print(data)
    nroEnvio = data["nEnvio"]
    chofer = data["chofer"]
    observacion,recibe,dni,quienRecibe,ubicacion = None,None,None,None,None
    if "observacion" in data.keys():
        observacion = data["observacion"]
    if "quienRecibe" in data.keys() and "dni" in data.keys():
        recibe = data["quienRecibe"] 
        dni = data["dni"]
        quienRecibe = f"{recibe} Dni: {dni}"
    if "location" in data.keys():
        location = data["location"]
    else:
        location = None
    sql = """
        update ViajesFlexs set 
        `Check` = null,
        estado_envio = "Entregado",
        Motivo = "Entregado sin novedades",
        Observacion = %s,
        Recibe_otro = %s,
        Chofer = choferCorreo(%s),
        Correo_chofer = %s,
        Timechangestamp = %s,
        Currentlocation = %s
        where Numero_envío = %s
        """
    values = (observacion,quienRecibe,chofer,chofer,datetime.now()-timedelta(hours=3),location,nroEnvio)
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return jsonify(success=True,message="Envio Entregado",envio=nroEnvio)

#pendiente de programar, Debe incluir los siguientes motivos:
#Nadie en domicilio(Reprogramado) --> Requiere foto
#Rechazado por el comprador --> Requiere foto
#OPCIONAL: campo de observacion
@pd.route("/noentregado",methods=["POST"])
def noEntregado():
    data = request.get_json()
    nroEnvio = data["nEnvio"]
    chofer = data["chofer"]
    motivo = data["motivo"]
    if "location" in data.keys():
        location = data["location"]
    else:
        location = None
    foto = ""
    midb = connect_db()
    cursor = midb.cursor()
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
        cursor.execute("update ViajesFlexs set Foto_domicilio = %s where Numero_envío = %s",(foto,nroEnvio))
        midb.commit()
    else:
        foto = None
    print(foto)
    
    sql = """
            update ViajesFlexs 
                set `Check` = null, 
                estado_envio = 'No Entregado', 
                Motivo = %s, 
                foto_domicilio = null,
                Timechangestamp = %s,
                Currentlocation = %s
            where 
                Numero_envío = %s 
            and 
                Chofer = choferCorreo(%s)"""
    values = (motivo,datetime.now()-timedelta(hours=3),location,nroEnvio,chofer)
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return jsonify(success=False,message="Todavia no esta lista esta seccion",envio=nroEnvio)

@pd.route("/imagen",methods = ["POST"])
def subirImagen():
    data = request.get_json()
    nroEnvio = data["nEnvio"]
    chofer = data["chofer"]
    imagen = data["image"]
    if "location" in data.keys():
        location = data["location"]
    else:
        location = NotImplementedError

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
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql,values)
    midb.commit()
    midb.close()
    return ""