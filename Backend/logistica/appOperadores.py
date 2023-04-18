
from flask import Blueprint, jsonify, request,send_file,redirect
from threading import Thread
import requests
from Backend.database.database import connect_db
from Backend.logistica.actualizarLogixs import actualizar_estado_logixs

OPLG = Blueprint('operadoresLogisticos', __name__, url_prefix='/')


@OPLG.route("/api/admin/login",methods=["POST"])
def loginAdmin():
    dataLogin = request.get_json()
    usser = dataLogin["ussername"]
    password = dataLogin["password"]
    print(usser," ",password)
    midb = connect_db()
    cursor = midb.cursor()
    sql ="""
    SELECT 
        `nickname`
    FROM 
        `mmslogis_MMSPack`.`usuario` where nickname= %s and password = %s;
    """
    cursor.execute(sql,(usser,password))
    res = cursor.fetchone()
    midb.close()
    if res != None:
        return jsonify(success=True,message="Inicio de sesion correcto",data=res)
    else:
        return jsonify(success=False,message="password invalid",data=None)
    

@OPLG.route("/operadores/consultaempleados",methods=["POST"])
def consultaEmpleado():
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select id,nombre,correo from empleado where Fecha_Baja is null order by nombre")
    empleados = []
    empleado = {"id":0,"nombre":"","correo":""}
    empleados.append(empleado)
    for x in cursor.fetchall():
        empleado = {"id":x[0],"nombre":x[1],"correo":x[2]}
        empleados.append(empleado)
    return jsonify(empleados)

@OPLG.route("/operadores/retirado",methods=["POST"])
def enviosRetiradosOP():
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

@OPLG.route("/operadores/retirar",methods=["POST"])
def scannerRetirarOP():
    data = request.get_json()
    envio = data["id"]
    operador = data["operador"]
    location = data["location"]
    print(f"operador: {operador}")
    del data["operador"]
    del data["location"]
    try:
        threadActualizaLogixs = Thread(target=actualizar_estado_logixs, args=(1, "retiro", "MMS", data, envio))
        threadActualizaLogixs.start()
    except:
        print("Fallo informe a logixs (Retiro)")
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("SELECT fecha,ifnull(choferCorreo(chofer),chofer) from retirado where Numero_envío = %s limit 1",(envio,))
    resultado = cursor.fetchone()
    if resultado == None:
        cursor.execute("""insert into retirado
                            (fecha,hora,Numero_envío,chofer,estado,scanner,Currentlocation) 
                            values(
                                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                                DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),
                                %s,
                                %s,
                                'Retirado',
                                %s,
                                %s);""",
                                (envio,operador,str(data),location))
        midb.commit()
        midb.close()
        return jsonify(success=True,message="Retirado")
    else:
        midb.close()
        return jsonify(success=False,message=f"Ya retirador por {resultado[1]} el {resultado[0]}")


@OPLG.route("/operadores/ingreso",methods=["POST"])
def scannerIngreso():
    data = request.get_json()
    print(data)
    envio = data["id"]
    operador = data["operador"]
    chofer = data["chofer"]
    location = data["location"]
    del data["operador"]
    del data["chofer"]
    del data["location"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("SELECT Fecha,estado_envio,Motivo from ViajesFlexs where Numero_envío = %s ",(envio,))
    resultado = cursor.fetchone()
    print(resultado)
    
    if resultado == None:
        values = (envio,operador,chofer,"NO ESTA EN LISTA",str(data),location)
        cursor.execute("""insert into ingresado 
                        (Numero_envío,operador,chofer,estado,scanner,Currentlocation)
                        values (%s,%s,%s,%s,%s,%s);""",values)
        midb.commit()
        midb.close()
        return jsonify(success=False,message="No esta en lista")
    else:
        estado = resultado[1]
        motivo = resultado[2]
        values = (envio,operador,chofer,f"Estado: {estado}, Motivo: {motivo}",str(data),location)
        cursor.execute("""insert into ingresado 
                        (Numero_envío,operador,chofer,estado,scanner,Currentlocation)
                        values (%s,%s,%s,%s,%s,%s);""",values)
        midb.commit()
        midb.close()
        if estado != "Retirado":
            return jsonify(success=False,message=f"Estado: {estado}, Motivo: {motivo}")
        else:
            return jsonify(success=True,message=f"Envio {envio} ingresado")

        
def sectorizar(database,data,zona):
    nenvio = data["id"]
    chofer = data["operador"]
    location = data["location"]
    del data["operador"]
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

@OPLG.route("/operadores/sectorizar",methods=["POST"])
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

@OPLG.route("/operadores/encaminar", methods=["POST"])
def enCaminar():
    data = request.get_json()
    nenvio = data["id"]
    chofer = data["chofer"]
    operador = data["operador"]
    latlong = data["location"]
    del data["chofer"]
    del data["operador"]
    del data["location"]
    try:
        threadActualizaLogixs = Thread(target=actualizar_estado_logixs, args=(1, "carga", "MMS", data, nenvio))
        threadActualizaLogixs.start()
    except:
        print("Fallo informe a logixs (CARGA)")
    status = False
    message = ""
    try:
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(
            """INSERT INTO `mmslogis_MMSPack`.`en_camino`
                    (`id`,`fecha`,`hora`,`Numero_envío`,`chofer`,`scanner`,Currentlocation,asigno)
                VALUES
                    (UUID(),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                    ,%s,correoChofer(%s),%s,%s,%s);""",(nenvio,chofer,str(data),latlong,operador))
        midb.commit()
        midb.close()
        status = True
        message = "Cargado"
    except Exception as err:
        print(err)
        status = False
        message = err
    return jsonify(success=status,message=message,envio=nenvio)


@OPLG.route("/operadores/egreso", methods=["POST"])
def egresar():
    data = request.get_json()
    nenvio = data["id"]
    chofer = data["chofer"]
    operador = data["operador"]
    latlong = data["location"]
    del data["chofer"]
    del data["operador"]
    del data["location"]
    status = False
    message = ""
    try:
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(
            """INSERT INTO `mmslogis_MMSPack`.`egreso`
                    (`id`,`fecha`,`hora`,estado,`Numero_envío`,`chofer`,`scanner`,Currentlocation,operador)
                VALUES
                    (UUID(),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR)
                    ,"Lista para Devolver",%s,correoChofer(%s),%s,%s,%s);""",(nenvio,chofer,str(data),latlong,operador))
        midb.commit()
        midb.close()
        status = True
        message = "Egreso registrado"
    except Exception as err:
        print(err)
        status = False
        message = f"Ocurrio un error: {err}"
    return jsonify(success=status,message=message,envio=nenvio)


@OPLG.route("/operadores/devolucion", methods=["POST"])
def devolver():
    data = request.get_json()
    nenvio = data["id"]
    operador = data["operador"]
    latlong = data["location"]
    del data["operador"]
    del data["location"]
    status = False
    message = ""
    try:
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(
            """INSERT INTO `mmslogis_MMSPack`.`devoluciones`
                    (`id`,`fecha`,`hora`,`estado`,`Numero_envío`,`chofer`,`scanner`,Currentlocation)
                VALUES
                    (UUID(),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),DATE_SUB(current_timestamp(), INTERVAL 3 HOUR),"Lista para Devolver"
                    ,%s,ifnull(correoChofer(%s),%s),%s,%s);""",(nenvio,operador,operador,str(data),latlong))
        midb.commit()
        midb.close()
        status = True
        message = "Listo para devolver"
    except Exception as err:
        print(err)
        status = False
        message = f"Ocurrio un error: {err}"
    return jsonify(success=status,message=message,envio=nenvio)