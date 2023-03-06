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
    sql = f"select Fecha,Zona,Numero_envío,Direccion,Referencia,Localidad,Vendedor,Chofer,estado_envio,Motivo,Cobrar from ViajesFlexs where Cobrar > 0 and estado_envio = 'Entregado' and rendido is null order by Fecha desc;"
    cabezeras = ["Fecha","Zona","Numero_envío","Direccion","Referencia","Localidad","Vendedor","Chofer","estado_envio","Motivo","Monto"]
    cursor.execute(sql)
    lista = []
    for x in cursor.fetchall():
        lista.append(x)
    return render_template("logistica/VistaTabla.html", 
                            titulo="Busqueda", 
                            viajes=lista,
                            columnas = cabezeras, 
                            cant_columnas = len(cabezeras),
                            contador = 0, 
                            auth = session.get("user_auth"))