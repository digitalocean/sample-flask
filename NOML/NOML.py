from flask import Blueprint, g, render_template, request, session
from auth import auth
from database import database
from datetime import datetime
import random
def obtenerClientes():
    midb = database.connect_db()
    clientes = []
    cursor = midb.cursor()
    cursor.execute("SELECT Cliente FROM mmslogis_MMSPack.`Apodos y Clientes` group by Cliente order by Cliente;")
    for x in cursor:
        clientes.append(x[0])
    midb.close()
    return clientes
NOML = Blueprint('NOML', __name__, url_prefix='/')

@NOML.route("/carga_noml", methods = ["GET","POST"])
@auth.login_required
def carga_noml():
    if request.method == "POST": 
        if "nro_envio" in request.form.keys():
            nro_envio = request.form.get("nro_envio")
        else:
            nro_envio = f"NoMl-{random(1,9999999999)}"
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        telefono = request.form.get("telefono")
        calle = request.form.get("calle")
        altura = request.form.get("altura")
        piso = request.form.get("piso")
        dpto = request.form.get("dpto")
        entre_calle1 = request.form.get("e/1")
        entre_calle2 = request.form.get("e/2")
        cp = request.form.get("cp")
        localidad = request.form.get("localidad")
        caba  = request.form.get("caba")
        referencia = request.form.get("referencia")
        referencia_completa = referencia + "\n" + "piso: " + piso + "\nDpto: "+dpto + "\ne/ " + entre_calle1 + " y " + entre_calle2
        if session.get("user_auth") == "Cliente":
            vendedor = session.get("user_id")
        else:
            vendedor = request.form.get("nombre_cliente")
        direccion_concatenada = calle + " " + str(altura) + localidad + ", Buenos Aires"
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = "insert into ViajesFlexs (Fecha, Numero_envío, comprador, Telefono, Direccion, Referencia, Localidad, capital, CP, Vendedor, estado_envio, Direccion_completa) values(current_date(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        values = (nro_envio,nombre + " " + apellido,telefono,calle + " " + altura, referencia_completa,localidad,caba,cp,vendedor, "Listo Para Retirar(Carga manual)",direccion_concatenada)
        cursor.execute(sql,values)
        midb.commit()
        return render_template("NOML/carga_noml.html",titulo="Carga", auth = session.get("user_auth"), nro_envio=nro_envio, clientes=obtenerClientes())

    else:
        return render_template("NOML/carga_noml.html",titulo="Carga", auth = session.get("user_auth"), clientes=obtenerClientes())


