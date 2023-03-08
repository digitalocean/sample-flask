from flask import (
    Blueprint, render_template, request, session,redirect
)
from Backend.auth import auth
from datetime import datetime

from Backend.database import database

ahora = (datetime.today())
fecha_hoy = str(ahora.year)+"/"+str(ahora.month)+"/"+str(ahora.day)
fecha_hoy_db = str(ahora.year)+"-"+str(ahora.month)+"-"+str(ahora.day)



cl = Blueprint('cliente', __name__, url_prefix='/')


@cl.route('/clientes/nuevo_cliente', methods=["GET","POST"])
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
        return render_template("cliente/nuevo_cliente.html",
                                auth = session.get("user_auth"),
                                tarifas=tarifas,urlForm = "/clientes/nuevo_cliente")
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
        return render_template("cliente/nuevo_cliente.html",titulo="Nuevo Cliente", auth = session.get("user_auth"),urlForm = "/clientes/nuevo_cliente")

@cl.route("clientes")
@auth.login_required
def verClientes():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select * from Clientes")
    clientes = []
    for x in cursor.fetchall():
        clientes.append(x)
    columnas = [i[0] for i in cursor.description]
    return render_template("cliente/VistaTabla.html",clientes=clientes,columnas=columnas, auth = session.get("user_auth"))


@cl.route("clientes/modificar",methods=["GET","POST"])
@auth.login_required
def modificarDatosClientes():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "GET":
        cursor.execute("select id, nombre from tarifa")
        tarifas = []
        for x in cursor.fetchall():
            id = x[0]
            tar = x[1]
            tarifas.append([id,tar])
        idClientes = request.args.get("idClientes")
        sql = """ select `nombre_cliente`,`razon_social`,`CUIT`,`Direccion`,`Telefono`,
                `Telefono_Alternativo`,`password`,`Modalidad_cobro`,`correo_electronico`,
                `tarifa` from Clientes where idClientes = %s"""
        values = (idClientes,)
        cursor.execute(sql,values)
        resu = cursor.fetchone()
        nombre_cliente = resu[0]
        razon_social = resu[1]
        cuit = resu[2]
        direccion = resu[3]
        telefono = resu[4]
        telefonoAlternativo = resu[5]
        password = resu[5]
        modalidadCobro = resu[7]
        correo = resu[8]
        tarifa = resu[9]
        midb.close()
        return render_template("cliente/nuevo_cliente.html",nombre_cliente = nombre_cliente,
                                razon_social = razon_social,cuit = cuit,direccion = direccion,
                                telefono = telefono,telefonoAlternativo = telefonoAlternativo,
                                password = password,modalidadCobro = modalidadCobro,correo = correo,
                                tarifa = tarifa,tarifas=tarifas,idClientes=idClientes, auth = session.get("user_auth"),
                                urlForm = "/clientes/modificar")
    else:
        idClientes = request.form.get("idClientes")
        nombre_cliente = request.form.get("nombre")
        razon_social = request.form.get("razon_social")
        cuit = request.form.get("cuit")
        direccion = request.form.get("direccion")
        telefono = request.form.get("telefono")
        telefonoAlternativo = request.form.get("telefonoAlternativo")
        password = request.form.get("password")
        modalidadCobro = request.form.get("modCobro")
        correo = request.form.get("correo_electronico")
        tarifa = request.form.get("tarifa")
        sql = """
            UPDATE `mmslogis_MMSPack`.`Clientes`
                SET
                `nombre_cliente` = %s,
                `razon_social` = %s,
                `CUIT` = %s,
                `Direccion` = %s,
                `Telefono` = %s,
                `Telefono_Alternativo` = %s,
                `password` = %s,
                `Modalidad_cobro` = %s,
                `correo_electronico` = %s,
                `tarifa` = %s
                WHERE `idClientes` = %s;
            """
        values = (nombre_cliente,razon_social,cuit,direccion,telefono,telefonoAlternativo,
                password,modalidadCobro,correo,tarifa,idClientes)
        print(values)
        cursor.execute(sql,values)
        midb.commit()
        midb.close()
        return redirect("/clientes")
