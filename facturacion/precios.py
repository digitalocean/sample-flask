from database import database
from auth import auth
from flask import (
    Blueprint, g, render_template, request, session,redirect
)


from scriptGeneral import scriptGeneral
precios = Blueprint('precios', __name__, url_prefix='/')

def obtenerIdTarifas(db):
    cursor = db.cursor()
    cursor.execute("select idTarifa from tarifa group by idTarifa")
    tarifas = []
    for x in cursor.fetchall():
        tarifas.append(x[0])
    return tarifas

def obtenerPrecios(tarifa,db):
    """Devuelve SUBlistas de 4 elementos
        nombre de la zona,
        precio de la zona,
        id tarifa,
        id zona
    """
    cursor = db.cursor()
    cursor.execute(f"""
    select (
        select nombre from zona where id = indicePrecio.id_zona
        ) as Zona,
        (
            select precio from zonaTarifaPrecio where id_tarifa = {tarifa} and id_zona = indicePrecio.id_zona
        ) as Precio,
        indicePrecio.id_tarifa,
        indicePrecio.id_zona 
        from indicePrecio where id_tarifa = {tarifa} group by Zona""")
    zonas = []
    for x in cursor.fetchall():
        zona = [x[0],x[1],x[2],x[3]]
        zonas.append(zona)
    return zonas

@precios.route('/facturacion/verprecio', methods=["GET","POST"])
@auth.login_required
@auth.admin_required
def consultarPrecio():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "POST":
        tarifa = request.form["tarifa"]
        zonas = obtenerPrecios(tarifa,midb)
        tarifas = obtenerIdTarifas(midb)
        return render_template("facturacion/tarifas.html",viajes=zonas,cant_columnas = 2,tarifa=tarifa,tarifas=tarifas,auth = session.get("user_auth"))
    else:
        tarifas = obtenerIdTarifas(midb)
        return render_template("facturacion/tarifas.html",cant_columnas = 2,tarifas=tarifas,auth = session.get("user_auth"))

@precios.route('facturacion/cambioprecio/', methods=["POST"])
@auth.login_required
@auth.admin_required
def cambiarprecio():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "POST":
        tarifa = request.form["tarifa"]
        zonas = obtenerPrecios(tarifa,midb)
        zonaCambia = request.form["zona"]
        nuevoprecio = request.form["nuevoprecio"]
        cursor.execute(f"update zonaTarifaPrecio set precio = {nuevoprecio} where id_tarifa = {tarifa} and id_zona = {zonaCambia}")
        midb.commit()
        tarifas = obtenerIdTarifas(midb)
        return render_template("facturacion/tarifas.html",viajes=zonas,cant_columnas = 2,tarifa=tarifa,tarifas=tarifas,auth = session.get("user_auth"))