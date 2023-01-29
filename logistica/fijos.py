from datetime import datetime
from flask import Blueprint, render_template, request, session,redirect
from auth import auth
from database import database
from scriptGeneral import scriptGeneral

fj = Blueprint('fijos', __name__, url_prefix='/')

@fj.route("/logistica/fijos", methods=["GET","POST"])
@auth.login_required
def fijos():
    midb = database.connect_db()
    cursor = midb.cursor()
    listaFijos = []
    cursor.execute("SELECT * FROM fijos limit 100")
    correoChoferes = scriptGeneral.correoChoferes(database.connect_db())
    for x in cursor.fetchall():
        listaFijos.append(x)
    if request.method == "GET":
        return render_template("logistica/fijos.html",fijos=listaFijos,choferes = correoChoferes,auth = session.get("user_auth"))
    elif request.method == "POST":
        fecha = request.form.get("fecha")
        chofer = request.form.get("chofer")
        costo = request.form.get("costo")
        cantidad = request.form.get("cantidad")
        sql = """
                INSERT INTO `mmslogis_MMSPack`.`fijos`
                    (`fecha`,
                    `chofer`,
                    `monto`,
                    `cantidad`)
                    VALUES
                    (%s,%s,%s,%s);
            """
        values = (fecha,chofer,costo,cantidad)
        cursor.execute(sql,values)
        midb.commit()
        return redirect("/logistica/fijos")
        