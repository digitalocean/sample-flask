from datetime import datetime
from flask import Blueprint, render_template, request, session
from auth import auth
from database import database
from scriptGeneral import scriptGeneral

devolucion = Blueprint('devolucion', __name__, url_prefix='/')

@devolucion.route("/logistica/devolucion", methods=["GET","POST"])
@auth.login_required
def devoluciones():
    if request.method == "POST":
        contador = 0
        midb = database.connect_db()
        cursor = midb.cursor()    
        cliente = request.form["cliente"]
        fecha = request.form["fecha"]
        sql = "select Numero_envío, Direccion, Localidad, Motivo From ViajesFlexs where Vendedor = %s and Numero_envío in (select Numero_envío from devoluciones where Fecha = %s)"
        values = (cliente,fecha)
        cursor.execute(sql,values)
        viajes = []
        for x in cursor.fetchall():
            contador += 1
            viajes.append(x)
        cabezeras = ["Numero_envío","Direccion", "Motivo"]
        return render_template("logistica/devoluciones.html", 
                                titulo="Hoja de ruta", 
                                cliente=cliente,
                                viajes=viajes,
                                columnas = cabezeras,
                                clienteSeleccionado=cliente,
                                cant_columnas=len(cabezeras),
                                fecha=fecha,
                                total=contador,
                                clientes=scriptGeneral.consultar_clientes(database.connect_db()),
                                auth = session.get("user_auth"))
    elif request.method == "GET":
        hoy = str(datetime.now())[0:10]
        return render_template("logistica/devoluciones.html",
                                clientes=scriptGeneral.consultar_clientes(database.connect_db()),
                                fecha=hoy,
                                auth = session.get("user_auth"))
