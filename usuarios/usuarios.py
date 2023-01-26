from flask import (
    Blueprint, render_template, request, session
)
from auth import auth
from datetime import datetime

from database import database

ahora = (datetime.today())
fecha_hoy = str(ahora.year)+"/"+str(ahora.month)+"/"+str(ahora.day)
fecha_hoy_db = str(ahora.year)+"-"+str(ahora.month)+"-"+str(ahora.day)



us = Blueprint('usuarios', __name__, url_prefix='/')


@us.route('/clientes/nuevo_cliente', methods=["GET","POST"])
@auth.login_required
def crear_cliente():
    if(request.method == "GET"):
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("select id, nombre from tarifa")
        tarifas = []
        for x in cursor.fetchall():
            id = x[0]
            tar = x[1]
            tarifas.append([id,tar])
        return render_template("usuario/nuevo_cliente.html",
                                auth = session.get("user_auth"),
                                tarifas=tarifas)

    elif(request.method == "POST"):
        nombre = request.form.get("nombre")
        razon_social = request.form.get("razon_social")
        cuit = request.form.get("cuit")
        direccion = request.form.get("direccion")
        correo_electronico = request.form.get("correo_electronico")
        telefono = request.form.get("telefono")
        telefonoAlternativo = request.form.get("telefonoAlternativo")
        passw = request.form.get("password")
        modo_cobro = request.form.get("modCobro")
        tarifa = request.form.get("tarifa")
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("""
        INSERT INTO `mmslogis_MMSPack`.`Clientes`
            (`nombre_cliente`,
            `razon_social`,
            `CUIT`,
            `Direccion`,
            `Telefono`,
            `Telefono_Alternativo`,
            `password`,
            `Fecha_Alta`,
            `Modalidad_cobro`,
            `correo_electronico`,
            `tarifa`)
            VALUES(%s,%s,%s,%s,%s,%s,%s,current_date(),%s,%s,%s);""", 
            (nombre,razon_social,cuit,direccion,telefono,telefonoAlternativo,passw,
            modo_cobro,correo_electronico,tarifa))
        midb.commit()
        midb.close()
        return render_template("usuario/nuevo_cliente.html",titulo="Nuevo Cliente", auth = session.get("user_auth"))

@us.route("clientes")
@auth.login_required
def verClientes():
    midb = database.connect_db()
    cursor = midb.cursor()
    columnas = ["idClientes","nombre_cliente","razon_social","CUIT","CBU","Direccion","Latlong",
                "Telefono","Telefono_Alternativo","password","Fecha_Alta","Fecha_Baja","Modalidad_cobro",
                "correo_electronico","tarifa"]
    cursor.execute("select * from Clientes")
    clientes = []
    for x in cursor.fetchall():
        clientes.append(x)
    return render_template("usuario/VistaTabla.html",clientes=clientes,columnas=columnas, auth = session.get("user_auth"))


@us.route("clientes/modificar",methods=["GET","POST"])
@auth.login_required
def modificarDatosClientes():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "GET":
        idCliente = request.form.get("idCliente")
        sql = """ select `nombre_cliente`,`razon_social`,`CUIT`,`CBU`,`Direccion`,`Latlong`,`Telefono`,
                `Telefono_Alternativo`,`password`,`Fecha_Baja`,`Modalidad_cobro`,`correo_electronico`,
                `tarifa` from Clientes where idClientes = %s"""
        values = (idCliente,)
        cursor.execute(sql,values)
        resu = cursor.fetchone()
        print(resu)
        return render_template("usuario/formularioEdicionCliente.html")
    else:
        sql = """
            UPDATE `mmslogis_MMSPack`.`Clientes`
                SET
                `nombre_cliente` = %s,
                `razon_social` = %s,
                `CUIT` = %s,
                `CBU` = %s,
                `Direccion` = %s,
                `Latlong` = %s,
                `Telefono` = %s,
                `Telefono_Alternativo` = %s,
                `password` = %s,
                `Fecha_Baja` = %s,
                `Modalidad_cobro` = %s,
                `correo_electronico` = %s,
                `tarifa` = %s
                WHERE `idClientes` = %s AND `nombre_cliente` = %s;
            """
        values = (nombre_cliente,razon_social,cuit,cbu,direccion,latlong,telefono,telefonoAlternativo,
                password,fechaBaja,modalidadCobro,correo,tarifa)


