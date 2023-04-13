from flask import (
    Blueprint, render_template, request, session,redirect
)
from datetime import datetime
from Backend.auth import auth
from Backend.database import database
from Backend.ftp.ftpMod import upload
from datetime import date

ahora = (datetime.today())
fecha_hoy = str(ahora.year)+"/"+str(ahora.month)+"/"+str(ahora.day)
fecha_hoy_db = str(ahora.year)+"-"+str(ahora.month)+"-"+str(ahora.day)



cl = Blueprint('cliente', __name__, url_prefix='/')

@cl.route('clientes/nuevo_responsable/<idCliente>', methods=["GET"])
@auth.login_required
def crear_responsable_get(idCliente):
    return render_template("cliente/nuevo_responsable.html",
                        idCliente = idCliente,
                        auth = session.get("user_auth"))


@cl.route('clientes/nuevo_prospecto', methods=["GET","POST"])
@auth.login_required
def crear_prospecto():
    if(request.method == "GET"):
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute("select id, `localidad` from `localidad`")
        localidades = []
        for x in cursor.fetchall():
            id = x[0]
            localidad = x[1]
            localidades.append([id,localidad])
        cursor.execute("select id, nombre from tarifa")
        tarifas = []
        for x in cursor.fetchall():
            id = x[0]
            tar = x[1]
            tarifas.append([id,tar])
        return render_template("cliente/nuevo_prospecto.html",
                                urlForm = "/clientes/nuevo_prospecto",
                                localidades=localidades,
                                tarifas=tarifas,
                                auth = session.get("user_auth"))
    elif request.method=="POST":
        
        midb=database.connect_db()
        cursor=midb.cursor()    
        nombre_cliente=request.form.get("nombre_cliente")
        razon_social=request.form.get("razon_social")
        CUIT=request.form.get("CUIT")
        passw = request.form.get("password")
        rubro=request.form.get("rubro")
        direccion=request.form.get("direccion")
        localidad=request.form.get("localidad")
        piso=request.form.get("piso")
        dpto=request.form.get("dpto")
        telefono=request.form.get("teléfono")
        URL=request.form.get("URL")
        correo_electronico=request.form.get("correo_electronico")
        locales_cantidad=request.form.get("locales_cantidad")
        como_nos_conocio=request.form.get("como_nos_conocio")
        observaciones=request.form.get("observaciones")
        estado_contacto=request.form.get("estado_contacto")
        proxima_accion=request.form.get("proxima_accion")
        fecha_proxima_accion=request.form.get("fecha_proxima_accion")
        presupuesto=request.files["presupuesto"]
        filenamePresupuesto = presupuesto.filename
        if filenamePresupuesto != "":
            presupuesto = upload("/presupuesto",presupuesto.read(),filenamePresupuesto)
        else:
            presupuesto = "No File"
        mapa_cotizacion=request.files["mapa_cotizacion"]
        filenameMapa_cotizacion = mapa_cotizacion.filename
        if filenameMapa_cotizacion != "":
            mapa_cotizacion = upload("/mapa_cotizacion",mapa_cotizacion.read(),filenameMapa_cotizacion)
        else:
            mapa_cotizacion = "No File"
        modalidad_de_cobro=request.form.get("modalidad_de_cobro")
        responsable_proxima_accion=request.form.get("responsable_proxima_accion")
        tarifa = request.form.get("tarifa")
        bonificacion = request.form.get("bonificacion")
        cantidad_retiros = request.form.get("cantidad_retiros")
        fecha_alta = request.form.get("fecha_alta")
        modifico = session.get("user_id")
        
        values=(nombre_cliente,razon_social,CUIT,passw,direccion,localidad,piso,dpto,telefono,
                modalidad_de_cobro,correo_electronico,rubro,estado_contacto,locales_cantidad,
                como_nos_conocio,proxima_accion,fecha_proxima_accion,responsable_proxima_accion,
                observaciones,presupuesto,mapa_cotizacion,modifico,URL,tarifa,bonificacion,cantidad_retiros,fecha_alta)
        cursor.execute("""INSERT INTO `mmslogis_MMSPack`.`Clientes`(
                        `nombre_cliente`,`razon_social`,`CUIT`,`password`,`Direccion`,`localidad`,
                        `piso`,`departamento`,`Telefono`,`Modalidad_cobro`,`correo_electronico`,
                        `rubro`,`estado_contacto`,`locales_cantidad`,`como_nos_conocio`,
                        `proxima_accion`,`fecha_proxima_accion`,`responsable_proxima_accion`,
                        `observaciones`,`presupuesto`,`mapa_cotizacion`,`modifico`,`URL`,`tarifa`,
                        bonificacion,cantidad_retiros,Fecha_Alta)
                        VALUES
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",values)
        midb.commit()           
        idClienteAgregado = cursor.lastrowid
        midb.close()
        return render_template("cliente/nuevo_responsable.html",
                        idCliente = idClienteAgregado,
                        auth = session.get("user_auth"))
    
@cl.route('clientes/nuevo_responsable/', methods=["POST"])
@auth.login_required
def crear_responsable():
    idCliente = request.form.get("idCliente")
    nombre = request.form.get("nombre")
    cargo = request.form.get("cargo")
    telefono = request.form.get("telefono")
    correo_electronico = request.form.get("correo_electronico")
    midb = database.connect_db()
    cursor = midb.cursor()
    sql = """
    INSERT INTO `mmslogis_MMSPack`.`responsable`(`marca_temporal`,`responsable_1_nombre`,
    `responsable_1_cargo`,`responsable_1_telefono`,`responsable_1_correo_electronico`)
    VALUES (current_timestamp(),%s,%s,%s,%s);"""
    values = (nombre,cargo,telefono,correo_electronico)
    midb.start_transaction()
    try:
        cursor.execute(sql,values)
        midb.commit()
        idResponsable = cursor.lastrowid

        sqlRelacion = """
        INSERT INTO `mmslogis_MMSPack`.`responsable_cliente`
            (`idCliente`,`id_responsable`)
            VALUES(%s,%s);
        """
        valuesRelacion = (idCliente,idResponsable)
        cursor.execute(sqlRelacion,valuesRelacion)
        midb.commit()
    except:
        midb.rollback()
        return "Se produjo un error al agregar el responsable, intente nuevamente"
    midb.close()
    return redirect("/clientes")


@cl.route("/cliente/<idCliente>")
@auth.login_required
def verCliente(idCliente):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select C.idClientes,C.nombre_cliente,C.razon_social,C.CUIT,C.CBU,C.Direccion,C.localidad,C.piso,C.departamento,C.Telefono,C.password,C.fecha_carga,C.Fecha_Alta,C.Fecha_Baja,C.Modalidad_cobro,C.correo_electronico,C.tarifa,C.marca_temporal,C.rubro,C.estado_contacto,C.locales_cantidad,C.como_nos_conocio,C.proxima_accion,C.fecha_proxima_accion,C.responsable_proxima_accion,C.observaciones,C.modifico,C.URL,C.bonificacion,C.cantidad_retiros,C.presupuesto,C.mapa_cotizacion from Clientes as C where C.idClientes = %s;",(idCliente,))
    clientes = []
    responsables = []
    columnas = [i[0] for i in cursor.description]
    idCliente = 0
    for x in cursor.fetchall():
        idCliente = x[0]
        presupuesto = x[-2]
        mapa = x[-1]
        clientes.append(x)
    cursor.execute("select R.responsable_1_nombre as Nombre,R.responsable_1_cargo as Puesto,R.responsable_1_telefono as Telefono,R.responsable_1_correo_electronico as `Correo electronico` from Clientes as C left join responsable_cliente as RC on C.idClientes = RC.idCliente left join responsable as R on RC.id_responsable = R.id where C.idClientes = %s;",(idCliente,))
    for y in cursor.fetchall():
        responsables.append(y)
    return render_template("cliente/VistaTabla.html",
                           clientes=clientes,
                           idCliente = idCliente,
                           presupuesto = presupuesto,
                           mapa = mapa,
                           responsables = responsables,
                           columnas=columnas, 
                           auth = session.get("user_auth"))


@cl.route("/clientes")
@auth.login_required
def verClientes():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select idClientes,nombre_cliente,razon_social,CUIT from Clientes order by nombre_cliente")
    # cursor.execute("select * from Clientes as C left join responsable_cliente as RC on C.idClientes = RC.idCliente left join responsable as R on RC.id_responsable = R.id order by C.nombre_cliente;")
    clientes = []
    for x in cursor.fetchall():
        clientes.append(x)
    columnas = [i[0] for i in cursor.description]
    return render_template("cliente/VistaTabla.html",
                           botonVerDatos = True,
                           clientes=clientes,
                           columnas=columnas, 
                           auth = session.get("user_auth"))

@cl.route("/cliente/baja/<id>")
@auth.login_required
def bajaCliente(id):
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("update Clientes set Fecha_Baja = current_date() where idClientes = %s",(id,))
    midb.commit()
    midb.close()
    return redirect("/clientes")


@cl.route("/clientes/modificar",methods=["GET","POST"])
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
        sql = """ select `nombre_cliente`,`razon_social`,`CUIT`,`password`,`Direccion`,`localidad`,
                        `piso`,`departamento`,`Telefono`,`Modalidad_cobro`,`correo_electronico`,
                        `rubro`,`estado_contacto`,`locales_cantidad`,`como_nos_conocio`,
                        `proxima_accion`,`fecha_proxima_accion`,`responsable_proxima_accion`,
                        `observaciones`,`presupuesto`,`mapa_cotizacion`,`URL`,`tarifa`,bonificacion,cantidad_retiros,Fecha_Alta
                        from Clientes where idClientes = %s"""
        values = (idClientes,)
        cursor.execute(sql,values)
        resu = cursor.fetchone()
        nombre_cliente = resu[0]
        razon_social = resu[1]
        cuit = resu[2]
        password = resu[3]
        direccion = resu[4]
        localidad = resu[5]
        piso = resu[6]
        departamento = resu[7]
        telefono = resu[8]
        modalidadCobro = resu[9]
        correo = resu[10]
        rubro = resu[11]
        estado_contacto = resu[12]
        locales_cantidad = resu[13]
        como_nos_conocio = resu[14]
        proxima_accion = resu[15]
        fecha_proxima_accion = resu[16]
        responsable_proxima_accion = resu[17]
        observaciones = resu[18]
        presupuesto = resu[19]
        mapa_cotizacion = resu[20]
        URL = resu[21]
        tarifa = resu[22]
        bonificacion = resu[23]
        cantidad_retiros = resu[24]
        fecha_alta = resu[25]
        midb.close()
        return render_template("cliente/nuevo_prospecto.html",nombre_cliente = nombre_cliente,
                                razon_social = razon_social,cuit = cuit,direccion = direccion,
                                localidad = localidad,piso = piso,departamento = departamento,
                                rubro = rubro,estado_contacto = estado_contacto,
                                locales_cantidad = locales_cantidad,como_nos_conocio = como_nos_conocio,
                                proxima_accion = proxima_accion,fecha_proxima_accion = fecha_proxima_accion,
                                responsable_proxima_accion = responsable_proxima_accion,
                                observaciones = observaciones,presupuesto = presupuesto,
                                mapa_cotizacion = mapa_cotizacion,URL = URL,telefono = telefono,
                                password = password,modalidadCobro = modalidadCobro,
                                bonificacion = bonificacion,cantidad_retiros = cantidad_retiros,
                                correo = correo,tarifa = tarifa,tarifas=tarifas,idClientes=idClientes,
                                fecha_alta = fecha_alta,auth = session.get("user_auth"),
                                urlForm = "/clientes/modificar")
    else:
        idClientes = request.form.get("idClientes")
        nombre_cliente=request.form.get("nombre_cliente")
        razon_social=request.form.get("razon_social")
        CUIT=request.form.get("CUIT")
        passw = request.form.get("password")
        rubro=request.form.get("Rubro")
        direccion=request.form.get("direccion")
        localidad=request.form.get("localidad")
        piso=request.form.get("piso")
        dpto=request.form.get("dpto")
        telefono=request.form.get("telefono")
        URL=request.form.get("url")
        correo_electronico=request.form.get("correo_electronico")
        locales_cantidad=request.form.get("locales_cantidad")
        como_nos_conocio=request.form.get("como_nos_conocio")
        observaciones=request.form.get("observaciones")
        estado_contacto=request.form.get("estado_contacto")
        proxima_accion=request.form.get("proxima_accion")
        fecha_proxima_accion=request.form.get("fecha_proxima_accion")
        try:
            presupuesto=request.files["presupuesto"]
            filenamePresupuesto = presupuesto.filename
            if filenamePresupuesto != "":
                presupuesto = upload("/presupuesto",presupuesto.read(),filenamePresupuesto)
            else:
                presupuesto = "No File"
        except:
            pass
        try:
            mapa_cotizacion=request.files["mapa_cotizacion"]
            filenameMapa_cotizacion = mapa_cotizacion.filename
            if filenameMapa_cotizacion != "":
                mapa_cotizacion = upload("/mapa_cotizacion",mapa_cotizacion.read(),filenameMapa_cotizacion)
            else:
                mapa_cotizacion = "No File"
        except:
            pass
        modalidad_de_cobro=request.form.get("modalidad_de_cobro")
        responsable_proxima_accion=request.form.get("responsable_proxima_accion")
        tarifa = request.form.get("tarifa")
        bonificacion = request.form.get("bonificacion")
        cantidad_retiros = request.form.get("cantidad_retiros")
        fecha_alta = request.form.get("fecha_alta")
        modifico = session.get("user_id")
        sql = """
            UPDATE `mmslogis_MMSPack`.`Clientes`
                SET
                    `nombre_cliente` = %s,
                    `razon_social` = %s,
                    `CUIT` = %s,
                    `password` = %s,
                    `Direccion` = %s,
                    `localidad` = %s,
                    `piso` = %s,
                    `departamento` = %s,
                    `Telefono` = %s,
                    `Modalidad_cobro` = %s,
                    `correo_electronico` = %s,
                    `rubro` = %s,
                    `estado_contacto` = %s,
                    `locales_cantidad` = %s,
                    `como_nos_conocio` = %s,
                    `proxima_accion` = %s,
                    `fecha_proxima_accion` = %s,
                    `responsable_proxima_accion` = %s,
                    `observaciones` = %s,
                    `modifico` = %s,
                    `URL` = %s,
                    `tarifa` = %s,
                    bonificacion = %s,
                    cantidad_retiros = %s,
                    Fecha_Alta = %s
                WHERE `idClientes` = %s;
            """
        values = (nombre_cliente,razon_social,CUIT,passw,direccion,localidad,piso,dpto,telefono,
                modalidad_de_cobro,correo_electronico,rubro,estado_contacto,locales_cantidad,
                como_nos_conocio,proxima_accion,fecha_proxima_accion,responsable_proxima_accion,
                observaciones,modifico,URL,tarifa,bonificacion,
                cantidad_retiros,fecha_alta,idClientes)
        cursor.execute(sql,values)
        midb.commit()
        midb.close()
        return redirect("/clientes")
