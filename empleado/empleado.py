from flask import Blueprint, redirect, render_template, request, session,url_for
from auth import auth
from database import database
em = Blueprint('empleado', __name__, url_prefix='/')

@em.route("/empleado")
@auth.login_required
def empleado():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select id,nombre,puesto,vehiculo,patente,correo,dni,cbu,telefono,direccion,localidad,fecha_alta,fecha_baja from empleado")
    empleados = []
    for x in cursor.fetchall():
        empleados.append(x)
    cabezeras = ["id","Nombre","Puesto","Vehiculo","Patente","Correo","dni","cbu","Telefono","Fireccion","Localidad","Fecha alta","Fecha baja","Accion"]
    return render_template("empleado/VistaTabla.html", empleados = empleados,cabezeras=cabezeras, auth = session.get("user_auth"))

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
    return redirect(url_for("empleado.empleado"),session.get("user_auth"))

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