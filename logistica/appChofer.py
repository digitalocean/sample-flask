
import json
from flask import (
    Blueprint, jsonify, g, redirect, render_template, request, session
)
from werkzeug.security import generate_password_hash,check_password_hash

from database import database


pd = Blueprint('pendientes', __name__, url_prefix='/')

@pd.route("/retirado",methods=["POST"])
def loginEmplead2o():
    return "JOSUGATO"

@pd.route("/api/users/pending_delivery",methods=["POST"])
def loginEmpleado():
    dataLogin = request.get_json()
    print(dataLogin["nombre"])
    midb = database.connect_db()
    cursor = midb.cursor()
    sql =f"""SELECT `empleado`.`id`,
    `empleado`.`nombre`,
    `empleado`.`puesto`,
    `empleado`.`vehiculo`,
    `empleado`.`patente`,
    `empleado`.`correo`,
    `empleado`.`dni`,
    `empleado`.`cbu`,
    `empleado`.`telefono`,
    `empleado`.`direccion`,
    `empleado`.`localidad`,
    `empleado`.`fecha_alta`,
    `empleado`.`fecha_baja`,
    `empleado`.`password`,
    json_arrayagg(
    json_object(
    "check",`vf`.`Check`,
    "zona",`vf`.`Zona`,
    "fecha",`vf`.`Fecha`,
    "numeroEnvio",`vf`.`Numero_envío`,
    "nro_venta",`vf`.`nro_venta`,
    "comprador",`vf`.`comprador`,
    "telefono",`vf`.`Telefono`,
    "direccion",`vf`.`Direccion`,
    "referencia",`vf`.`Referencia`,
    "localidad",`vf`.`Localidad`,
    "cp",`vf`.`CP`,
    "vendedor",`vf`.`Vendedor`,
    "chofer",`vf`.`Chofer`,
    "motivo",`vf`.`Motivo`,
    "latitud",`vf`.`Latitud`,
    "longitud",`vf`.`Longitud`,
    "precioCliente",`vf`.`Precio_Cliente`,
    "precioChofer",`vf`.`Precio_Chofer`,
    "estadoEnvio",`vf`.`estado_envio`,
    "fotoDomicilio",`vf`.`Foto_domicilio`,
    "tipoEnvio",`vf`.`tipo_envio`,
    "correoChofer",`vf`.`Correo_chofer`,
    "cobrar",`vf`.`Cobrar`,
    "reprogramaciones",`vf`.`Reprogramaciones`
)) as pending
FROM `mmslogis_MMSPack`.`empleado` inner join ViajesFlexs as vf
on empleado.nombre = vf.Chofer and vf.Zona in 
(select `Nombre Zona` from ZonasyChoferes where `Nombre Completo` = "{dataLogin["nombre"]}") group by Zona;
"""

    cursor.execute(sql)
    res = cursor.fetchone()
    midb.close()
    if res is None:
        return jsonify(success=False,message="No se encontraron pendientes",data=None)
    else:
        data = {
            'id':res[0],
            'nombre':res[1],
            'puesto':res[2],
            'vehiculo':res[3],
            'patente':res[4],
            'correo':res[5],
            'dni':str(res[6]),
            'cbu':str(res[7]),
            'telefono':str(res[8]),
            'direccion':res[9],
            'localidad':res[10],
            'password':res[13],
            'session_token': None,
            'pending':jsonify(res[14])
        }
        resultado = str(res[14])[14:-4].replace("\\","")
        print(resultado)
        data = json.dumps(resultado)
        return jsonify(success=True,message="Envios obtenidos",data=data)
