from database import database
from flask import (
    Blueprint, g, render_template, request, session,redirect
)

from .script import consultar_clientes,quitarAcento
precios = Blueprint('precios', __name__, url_prefix='/')

@precios.route('/facturacion/verprecio', methods=["GET","POST"])
def consultarPrecio():
    midb = database.connect_db()
    cursor = midb.cursor()
    if request.method == "POST":
        tarifa = request.form["tarifa"]
        cursor.execute(f"select (select nombre from zona where id = precioCosto.id_zona) as Zona,precio,id_zona from precioCosto where id_tarifa = {tarifa} group by Zona")
        zonas = []
        for x in cursor.fetchall():
            zona = [x[0],x[1]]
            zonas.append(zona)
        return render_template("facturacion/tarifas.html",viajes=zonas,cant_columnas = 2,tarifa=tarifa)
    else:
        cursor.execute("select idTarifa from tarifa group by idTarifa")
        tarifas = []
        for x in cursor.fetchall():
            tarifas.append(x[0])
        return render_template("facturacion/tarifas.html",cant_columnas = 2,tarifas=tarifas)

@precios.route('facturacion/cambioprecio/<tarifa>/<zona>/<precio>')
def cambiarprecio():
    for x in request.form.keys():
        print(x)
    # midb = database.connect_db()
    # cursor = midb.cursor()
    # cursor = midb.cursor()
    # cursor.execute(f"select (select localidad from localidad where id = precioCosto.id_localidad) as Localidad,(select nombre from zona where id = precioCosto.id_zona) as Zona ,precio from precioCosto where id_tarifa = {tarifa} and id_zona = {zona}")
    # zonas = []
    # for x in cursor.fetchall():
    #     zona = [x[0],x[1],x[2]]
    #     zonas.append(zona)
    # return render_template("facturacion/tarifas.html",viajes=zonas,cant_columnas = 3)
    return redirect("/")