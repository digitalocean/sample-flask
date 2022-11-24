from database import database
from auth import auth
from flask import (
    Blueprint, g, render_template, request, session,redirect
)
from scriptGeneral import scriptGeneral
ap = Blueprint('apodos', __name__, url_prefix='/')

@ap.route("/facturacion/apodos", methods=["GET","POST"])
@auth.login_required
def apodos():
    if request.method == "POST":
        return "POST"
    else:
        midb = database.connect_db()
        cursor = midb.cursor()
        clientes = []
        cursor.execute("select nombre_cliente from Clientes")
        for x in cursor.fetchall():
            clientes.append(x[0])
        apodos = []
        cursor.execute("select Apodo,Cliente from `Apodos y Clientes`")
        for x in cursor.fetchall():
            apodos.append(x[0])
        return render_template("facturacion/apodos.html",
                                clientes = clientes,
                                apodos = apodos)