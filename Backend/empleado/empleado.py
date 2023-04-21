from flask import Blueprint, redirect, render_template, request, session,url_for
from Backend.auth import auth
from Backend.database import database
em = Blueprint('empleado', __name__, url_prefix='/')

@em.route("/empleado")
@auth.login_required
def empleado():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select id,nombre,puesto,vehiculo,patente,correo,dni,cbu,telefono,telefono_alternativo,direccion,fecha_alta,fecha_baja from empleado")
    empleados = []
    for x in cursor.fetchall():
        empleados.append(x)
    cabezeras = ["id","Nombre","Puesto","Vehiculo","Patente","Correo","dni","cbu","Telefono","Telefono alternativo","Direccion","Fecha alta","Fecha baja","Accion"]
    return render_template("empleado/VistaTabla.html", empleados = empleados,cabezeras=cabezeras, auth = session.get("user_auth"))

@em.route("empleado/nuevoempleado",methods=["GET","POST"])
@auth.login_required
def nuevoEmpleado():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        puesto = request.form.get("puesto")
        vehiculo = request.form.get("vehiculo")
        marca = request.form.get("marca")
        modelo = request.form.get("modelo")
        patente = request.form.get("patente")
        correo = request.form.get("correo")
        dni = request.form.get("dni")
        cbu = request.form.get("cbu")
        telefono = request.form.get("telefono")
        telefonoAlternativo = request.form.get("telefonoAlternativo")
        direccion = request.form.get("direccion")
        localidad = request.form.get("localidad")
        nrolegajo = request.form.get("nrolegajo")
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = """INSERT INTO `mmslogis_MMSPack`.`empleado`
            (
            `nombre`,`puesto`,`vehiculo`,`marca`,`modelo`,`patente`,`correo`,`dni`,`cbu`,`telefono`,
            `telefono_alternativo`,`direccion`,`legajo nro`,`dni_frente`,`dni_dorso`,
            `cedula_frente`,`cedula_dorso`,`registro_frente`,`registro_dorso`,`monotributo`,
            `seguro`,`poliza_art`,`vtv`,`satelital`,`registro_vencimiento`,
            `cedula_vencimiento`,`vtv_vencimiento`,`disponibilidad_horaria`,`elementos_seguridad`,`contrato_locacion`,
            `foto`)
            VALUES(
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s);
            """
        values = (nombre,puesto,vehiculo,marca,modelo,patente,correo,int(dni),cbu,telefono,telefonoAlternativo,
                f"{direccion}, {localidad}",nrolegajo,None,None,None,None,None,None,None,None,None,None,None,
                None,None,None,None,None,None,None)
        cursor.execute(sql,values)
        midb.commit()
        midb.close()
        return render_template("empleado/nuevo_empleado.html",titulo="Nuevo empleado", auth = session.get("user_auth"),mensaje=f"{nombre} Agregado",confirmacion=True)
    else:
        return render_template("empleado/nuevo_empleado.html",titulo="Nuevo empleado", auth = session.get("user_auth"))
        

@em.route("/empleado/baja", methods=["POST"])
@auth.login_required
def bajaEmpleado():
    idEmpleado = request.form["idEmpleado"]
    sql = f"update empleado set fecha_baja = current_date() where id = {idEmpleado}"
    print(sql)
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    midb.commit()
    return redirect("/empleado",session.get("user_auth"))

@em.route("/empleado/alta", methods=["POST"])
@auth.login_required
def altaEmpleado():
    idEmpleado = request.form["idEmpleado"]
    sql = f"update empleado set fecha_baja = null where id = {idEmpleado}"
    print(sql)
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    midb.commit()
    return redirect(url_for("empleado.empleado"),session.get("user_auth"))
