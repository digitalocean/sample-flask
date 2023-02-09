from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database

VG = Blueprint('Vista General', __name__, url_prefix='/')

@VG.route("/logistica/vistageneral")
@auth.login_required
def descargaLogixsBoton():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select * from ViajesFlexs")
    resu = list(cursor.fetchall())
    return render_template("logistica/VistaTabla.html",viajes=resu)
