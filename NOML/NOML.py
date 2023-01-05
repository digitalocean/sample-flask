from flask import Blueprint,render_template,redirect, request, session
from scriptGeneral import scriptGeneral
from auth import auth
from database import database
from datetime import datetime
from logistica import Envio,script
import random
NOML = Blueprint('NOML', __name__, url_prefix='/')

@NOML.route("/carga_noml", methods = ["GET","POST"])
@auth.login_required
def carga_noml():
    midb = database.connect_db()
    if request.method == "POST": 
        direccion = request.form.get("direccion")
        localidad = request.form.get("localidad")
        direccion_concatenada = f"{direccion}, {localidad}, Buenos Aires"
        cobrar = request.form.get("cobrar")
        if session.get("user_auth") == "Cliente":
            nro_envio = None
            vendedor = session.get("user_id")
            nombre = request.form.get("nombre")
            apellido = request.form.get("apellido")
            telefono = request.form.get("telefono")
            piso = request.form.get("piso")
            dpto = request.form.get("dpto")
            entre_calle1 = request.form.get("e/1")
            entre_calle2 = request.form.get("e/2")
            cp = request.form.get("cp")
            referencia = request.form.get("referencia")
            if piso != '':
                referencia = referencia + f"\npiso: {piso}"
            if dpto != '':
                referencia = referencia + f"\nDpto: {dpto}"
            if entre_calle1 != '' or entre_calle2 != '':
                referencia = referencia + f"\ne/ {entre_calle1} y {entre_calle2}"
            comprador = nombre + " " + apellido
        else:
            nro_envio = request.form.get("nro_envio")
            vendedor = request.form.get("nombre_cliente")
            comprador = None
            telefono = None
            referencia = None
            cp = None
        tipo_envio = 2
        if vendedor == "Quality Shop":
            tipo_envio = 13
        viaje = Envio.Envio(direccion,localidad,vendedor,nro_envio,comprador,telefono,referencia,cp,cobrar=cobrar,tipoEnvio=tipo_envio)
        if viaje.toDB():
            script.geolocalizarFaltantes(database.connect_db())
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

@NOML.route("/borrar/", methods = ["GET","POST"])
@auth.login_required
def generarEtiqueta():
    if request.method == "POST": 
        envio = request.form.get("envio")
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = "delete from ViajesFlexs where Numero_envío = %s and estado_envio = 'Lista Para Retirar'"
        values = (envio,)
        cursor.execute(sql,values)
        midb.commit
        redirect("/misenvios")

@NOML.route("/etiqueta/", methods = ["GET","POST"])
@auth.login_required
def generarEtiqueta():
    if request.method == "POST": 
        envio = request.form.get("envio")
        midb = database.connect_db()
        cursor = midb.cursor()
        sql = "select Vendedor,Comprador,Telefono,Direccion,Localidad,Cobrar,Referencia,sku from ViajesFlexs where Numero_envío = %s"
        values = (envio,)
        cursor.execute(sql,values)
        resultado = cursor.fetchone()
        vendedor = resultado[0]
        comprador = resultado[1]
        telefono = resultado[2]
        direccion_concatenada = resultado[3] + ", " + resultado[4]
        cobrar = resultado[5]
        referencia = resultado[6]
        producto = resultado[7]
        if str(producto) == "None":
            producto = 0
        return render_template("NOML/etiqueta.html",
                            titulo="Envio agregado", 
                            auth = session.get("user_auth"), 
                            nro_envio=envio, 
                            vendedor = vendedor,
                            comprador = comprador,
                            producto = producto,
                            telefono = telefono,
                            direccion = direccion_concatenada,
                            referencia = referencia,
                            cobrar = cobrar)                        
    else:
        return redirect("/misenvios")

from database.database import connect_db
@NOML.route("/etiquetaspendientes")
def multiplesEtiquetas():
    vendedor = session.get("user_id")
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select Numero_envío,Fecha,comprador,Telefono,Direccion,Localidad,Referencia,sku,Cobrar from ViajesFlexs where estado_envio = 'Lista Para Retirar' and Vendedor = %s",(vendedor,))
    envios = []
    for x in cursor.fetchall():
        envios.append(x)
    return render_template("NOML/etiquetas.html",
                        etiquetas=envios,
                        vendedor=vendedor)

@NOML.route("/etiqueta/impresa", methods = ["GET","POST"])
@auth.login_required
def etiquetaImpresa():
    envio = request.form.get("nroEnvio")
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(f"update ViajesFlexs set Observacion = 'Etiqueta impresa {str(datetime.now())[0:-10]}' where Numero_envío = '{envio}' and Observacion is null")
    midb.commit()
    midb.close()
    return redirect("/misenvios")