from flask import (
    Blueprint, g, render_template, request, session
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
    return render_template("facturacion/cobrados.html", 
                            titulo="Busqueda", 
                            acciones = True,
                            viajes=lista,
                            columnas = cabezeras, 
                            cant_columnas = len(cabezeras),
                            total = suma, 
                            user = session.get("user_id"),
                            auth = session.get("user_auth"))

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