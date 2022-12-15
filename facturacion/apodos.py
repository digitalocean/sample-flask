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
        apodo = request.form["apodo"]
        cliente = request.form["cliente"]
        sql = f"update `Apodos y Clientes` set Cliente = '{cliente}',id_cliente = (select idClientes from Clientes where nombre_cliente = '{cliente}') where Apodo = '{apodo}';"
        midb = database.connect_db()
        cursor = midb.cursor()
        cursor.execute(sql)
        midb.commit()
        midb.close()
        print(sql)
        return redirect("/facturacion/apodos")
    else:
        midb = database.connect_db()
        cursor = midb.cursor()
        clientes = []
        cursor.execute("select nombre_cliente from Clientes")
        for x in cursor.fetchall():
            clientes.append(x[0])
        apodos = []
        cursor.execute("select Apodo,Cliente from `Apodos y Clientes` order by Cliente")
        for x in cursor.fetchall():
            apodoCliente = [x[0],x[1]]
            apodos.append(apodoCliente)
        return render_template("facturacion/apodos.html",
                                clientes = clientes,
                                apodos = apodos,
                                auth = session.get("user_auth"))