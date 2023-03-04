from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session
from Backend.auth import auth
from Backend.database import database

VG = Blueprint('Vista General', __name__, url_prefix='/')

@VG.route("/logistica/vistageneral")
@auth.login_required
def descargaLogixsBoton():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select * from ViajesFlexs limit 100")
    resu = list(cursor.fetchall())
    return render_template("logistica/VistaTabla.html",viajes=resu)
