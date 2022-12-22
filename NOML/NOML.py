from flask import Blueprint,render_template,redirect, request, session
from scriptGeneral import scriptGeneral
from auth import auth
from database import database
from datetime import datetime
from logistica import Envio
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
            cursor = midb.cursor()
            cursor.execute("select count(*) from ViajesFlexs")
            res = cursor.fetchone()
            caracteres = len(str(res[0]))
            agregar = 10 - caracteres
            nro_envio = "NoMl-"+ "0"*agregar + str(res[0])
            # nro_envio = f"NoMl-{random.randint(1,9999999999)}"
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")
        piso = request.form.get("piso")
        dpto = request.form.get("dpto")
        entre_calle1 = request.form.get("e/1")
        entre_calle2 = request.form.get("e/2")
        cp = request.form.get("cp")
        localidad = request.form.get("localidad")
        referencia = request.form.get("referencia")
        if piso != '':
            referencia = referencia + f"\npiso: {piso}"
        if dpto != '':
            referencia = referencia + f"\nDpto: {dpto}"
        if entre_calle1 != '' or entre_calle2 != '':
            referencia = referencia + f"\ne/ {entre_calle1} y {entre_calle2}"
        if session.get("user_auth") == "Cliente":
            vendedor = session.get("user_id")
        else:
            vendedor = request.form.get("nombre_cliente")
        direccion_concatenada = f"{direccion}, {localidad}, Buenos Aires"
        comprador = nombre + " " + apellido
        cobrar = request.form.get("cobrar")
        viaje = Envio.Envio(nro_envio,direccion,localidad,vendedor,comprador,telefono,referencia,cp,cobrar=cobrar)
        if viaje.toDB():
            return render_template("NOML/etiqueta.html",
                                titulo="Envio agregado", 
                                auth = session.get("user_auth"), 
                                nro_envio=nro_envio, 
                                vendedor = vendedor,
                                comprador = comprador,
                                telefono = telefono,
                                direccion = f"{direccion}, {localidad}",
                                referencia = referencia,
                                cobrar = cobrar)
        else:
            return render_template("NOML/carga_noml.html",
                                    mensaje_error="El numero de envio ya existe",
                                    titulo="Carga", 
                                    auth = session.get("user_auth"), 
                                    clientes=scriptGeneral.consultar_clientes(midb))

    else:
        return render_template("NOML/carga_noml.html",
                                titulo="Carga",
                                auth = session.get("user_auth"), 
                                clientes=scriptGeneral.consultar_clientes(midb))


@NOML.route("/etiqueta/", methods = ["GET","POST"])
@auth.login_required
def generar_etiqueta_post():
    envio = request.form.get("envio")
    midb = database.connect_db()
    cursor = midb.cursor()
    sql = "select Vendedor,Comprador,Telefono,Direccion,Localidad,Cobrar,Referencia from ViajesFlexs where Numero_envío = %s"
    values = (envio,)
    cursor.execute(sql,values)
    resultado = cursor.fetchone()
    vendedor = resultado[0]
    comprador = resultado[1]
    telefono = resultado[2]
    direccion_concatenada = resultado[3] + ", " + resultado[4]
    cobrar = resultado[5]
    referencia = resultado[6]
    return render_template("NOML/etiqueta.html",
                        titulo="Envio agregado", 
                        auth = session.get("user_auth"), 
                        nro_envio=envio, 
                        vendedor = vendedor,
                        comprador = comprador,
                        telefono = telefono,
                        direccion = direccion_concatenada,
                        referencia = referencia,
                        cobrar = cobrar)                        


@NOML.route("/etiqueta/impresa", methods = ["GET","POST"])
@auth.login_required
def etiquetaImpresa():
    envio = request.form.get("nroEnvio")
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"update ViajesFlexs set Observacion = 'Etiqueta impresa {str(datetime.now())[0:-10]}' where Numero_envío = '{envio}'")
    midb.commit()
    midb.close()
    return redirect("/misenvios")