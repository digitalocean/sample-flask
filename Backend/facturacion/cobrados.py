from flask import (
    Blueprint, g, render_template,redirect, request, session
)
from Backend.auth import auth
from Backend.informeErrores import informeErrores
from openpyxl import Workbook


from Backend.database import database
from Backend.scriptGeneral import scriptGeneral
cb = Blueprint('cobrados', __name__, url_prefix='/')


@cb.route("/facturacion/cobrados")
@auth.login_required
def busqueda():
    mjstbla = ""
    midb = database.connect_db()
    cursor = midb.cursor()
    sql = f"select Fecha,Numero_envío,Direccion,Referencia,Localidad,Vendedor,Chofer,estado_envio,Motivo,Cobrar from ViajesFlexs where Cobrar > 0 and estado_envio = 'Entregado' and rendido is null order by Fecha desc;"
    cabezeras = ["Fecha","Numero_envío","Direccion","Referencia","Localidad","Vendedor","Chofer","estado_envio","Motivo","Monto"]
    cursor.execute(sql)
    lista = []
    suma = 0
    for x in cursor.fetchall():
        suma += x[9]
        lista.append(x)
    return render_template("facturacion/cobrado.html", 
                            titulo="Busqueda", 
                            acciones = True,
                            viajes=lista,
                            columnas = cabezeras, 
                            cant_columnas = len(cabezeras),
                            total = suma, 
                            user = session.get("user_id"),
                            auth = session.get("user_auth"))


@cb.route("/facturacion/rendidos",methods = ["POST"])
@auth.admin_required
def rendidos():
    seleccionados = request.form.getlist('seleccionados[]')
    user = session.get("user_id")
    midb = database.connect_db()
    cursor = midb.cursor()
    cantidadRendidos = len(seleccionados)
    if cantidadRendidos == 0:
        print("no selecciono nada")
    else:
        for x in seleccionados:
            cursor.execute("""
                        update ViajesFlexs 
                            set 
                                rendido = current_timestamp(),
                                columna_2 = %s
                            where
                                Numero_envío = %s
                        """,(user,x))
            midb.commit()
            print(f"{x} Rendido")
    return redirect("/facturacion/cobrados")

@cb.route("/facturacion/rendido",methods = ["POST"])
@auth.admin_required
def rendido():
    midb = database.connect_db()
    cursor = midb.cursor()
    envio = request.json["nro_envio"]
    user = request.json["user"]
    cursor.execute("""
                    update ViajesFlexs 
                        set 
                            rendido = current_timestamp(),
                            columna_2 = %s
                        where
                            Numero_envío = %s
                    """,(user,envio))
    midb.commit()
    return ""