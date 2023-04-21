from Backend.database.database import connect_db
from Backend.auth import auth
from flask import (
    Blueprint, g, render_template, request, session,redirect
)
cont = Blueprint('contadores', __name__, url_prefix='/')

@cont.route("/logistica/contadores", methods=["GET","POST"])
@auth.login_required
def apodos():
    sql = f"select chofer, count(distinct(Numero_envío)) from ingresado where fecha = current_date() group by Chofer;"
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    retirado = []
    ingresado = []
    for x in cursor.fetchall():
        print(x)
        ingresado.append(x)
    cursor.execute("select ifnull(choferCorreo(chofer),chofer),count(*) from retirado where fecha = current_date() group by Chofer")
    for y in cursor.fetchall():
        retirado.append(y)
    midb.close()
    return render_template("/contadores/index.html",
                                retirados = retirado,
                                ingresados = ingresado,
                                columnas = ["Chofer","Cantidad"],
                                auth = session.get("user_auth"))