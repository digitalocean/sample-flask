from datetime import datetime
from flask import Blueprint, render_template, request, session
from auth import auth
from database import database
from scriptGeneral import scriptGeneral

hojaRuta = Blueprint('hojaRuta', __name__, url_prefix='/')

@hojaRuta.route("/logistica/hojaruta", methods=["GET","POST"])
@auth.login_required
def hojaDeRuta():
    if request.method == "POST":
        contador = 0
        midb = database.connect_db()
        cursor = midb.cursor()    
        chofer = request.form["chofer"]
        fecha = request.form["fecha"]
        sql = f"select Numero_envío, Direccion, Localidad, Referencia,vendedor(Vendedor) From ViajesFlexs where Numero_envío in (select Numero_envío from historial_estados where Fecha = '{fecha}' and estado_envio in ('En Camino', 'Reasignado') and Chofer = '{chofer}' )"
        # sql  = F"select Numero_envío from historial_estados where Chofer = '{chofer}' and Fecha = '{fecha}' and estado_envio in ('En Camino', 'Reasignado')"
        print(sql)
        cursor.execute(sql)
        viajes = []
        for x in cursor.fetchall():
            contador += 1
            viajes.append(x)
        cabezeras = ["Numero_envío","Direccion", "Referencia","Vendedor"]
        return render_template("logistica/hojaDeRuta.html", titulo="Hoja de ruta", viajes=viajes,columnas = cabezeras,cant_columnas=len(cabezeras),fecha=fecha,total=contador,choferSeleccionado=chofer,choferes=scriptGeneral.correoChoferes(database.connect_db()),auth = session.get("user_auth"))
    elif request.method == "GET":
        hoy = str(datetime.now())[0:10]
        return render_template("logistica/hojaDeRuta.html",choferes=scriptGeneral.correoChoferes(database.connect_db()),fecha=hoy, auth = session.get("user_auth"))
