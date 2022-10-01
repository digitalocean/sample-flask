from flask import Blueprint,render_template, request, session
from scriptGeneral import scriptGeneral
from auth import auth
from database import database
import random
NOML = Blueprint('NOML', __name__, url_prefix='/')

@NOML.route("/carga_noml", methods = ["GET","POST"])
@auth.login_required
def carga_noml():
    midb = database.connect_db()
    if request.method == "POST": 
        if "nro_envio" in request.form.keys():
            nro_envio = request.form.get("nro_envio")
        else:
            nro_envio = f"NoMl-{random.randint(1,9999999999)}"
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
        referencia = request.form.get("referencia")
        referencia_completa = referencia + "\n" + "piso: " + piso + "\nDpto: "+dpto + "\ne/ " + entre_calle1 + " y " + entre_calle2
        if session.get("user_auth") == "Cliente":
            vendedor = session.get("user_id")
        else:
            vendedor = request.form.get("nombre_cliente")
        direccion_concatenada = calle + " " + str(altura) + localidad + ", Buenos Aires"
        cobrar = request.form.get("cobrar")
        cursor = midb.cursor()
        sql = "insert into ViajesFlexs (Fecha, Numero_envío, comprador, Telefono, Direccion, Referencia, Localidad, CP, Vendedor, estado_envio, Direccion_completa,Cobrar) values(current_date(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        values = (nro_envio,nombre + " " + apellido,telefono,calle + " " + altura, referencia_completa,localidad,cp,vendedor, "Listo Para Retirar",direccion_concatenada,cobrar)
        cursor.execute(sql,values)
        midb.commit()
        return render_template("NOML/carga_noml.html",titulo="Carga", auth = session.get("user_auth"), nro_envio=nro_envio, clientes=scriptGeneral.consultar_clientes(midb))

    else:
        return render_template("NOML/carga_noml.html",titulo="Carga", auth = session.get("user_auth"), clientes=scriptGeneral.consultar_clientes(midb))


