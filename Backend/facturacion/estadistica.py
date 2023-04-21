
from flask import (
    Blueprint, g, render_template, request, session,send_file
)
from datetime import datetime,timedelta
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import PatternFill, Font,Alignment
from Backend.auth import auth
from .estrategiaDeFacturacion import *
from Backend.database.database import connect_db
from Backend.scriptGeneral import scriptGeneral

fcEstadistica = Blueprint('fcEstadistica', __name__, url_prefix='/')

@fcEstadistica.route("/facturacion/ver",methods = ["GET","POST"])
@auth.login_required
def facturar():
    if request.method == "POST":
        cabezeras = ["Fecha Original","En Camino","Ultimo Reasignado","Rendido","estado","Monto a rendir","Numero de envio","Direccion"]
        cliente = request.form.get("cliente")
        desde = request.form.get("desde")
        hasta = request.form.get("hasta")
        sql = f"""SELECT 
	            V.Fecha as fechaOriginal,
                    (select Fecha from historial_estados where Numero_envío = V.Numero_envío 
                        and estado_envio in ("En Camino") order by Fecha desc, Hora desc limit 1) fechaEnCamino,
                    (select Fecha from historial_estados where Numero_envío = V.Numero_envío 
                    and estado_envio in ("En Camino","Reasignado") order by Fecha desc, Hora desc limit 1) as ultimoReasignado,
                    V.rendido as fechaRendido,
                    H.estado_envio as Estado,
                    V.Cobrar as `Monto a Rendir`,
                    H.Numero_envío,H.Direccion_Completa FROM 
                    ViajesFlexs as V inner join historial_estados as H on V.Numero_envío = H.Numero_envío 
                    where vendedor(H.Vendedor) = '{cliente}'
                    and H.Fecha between '{desde}' and '{hasta}' 
                    and H.motivo_noenvio in ("Nadie en domicilio","Entregado sin novedades","Rechazado")"""
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(sql)
        viajes = []
        for x in cursor.fetchall():
            viajes.append(x)
        return render_template("facturacion/estadisticaFC.html",
                            cliente=cliente,
                            desde=desde,
                            hasta=hasta,
                            titulo="Facturacion", 
                            cabeceras = cabezeras,
                            tipo_facturacion="flex", 
                            viajes=viajes, 
                            clientes = scriptGeneral.consultar_clientes(midb), 
                            auth = session.get("user_auth")
                            )
    else:
        return render_template("facturacion/estadisticaFC.html",
                            titulo="Facturacion", 
                            desde=str(datetime.now()-timedelta(days=15))[0:10],
                            hasta=str(datetime.now())[0:10],
                            clientes=scriptGeneral.consultar_clientes(connect_db()), 
                            tipo_facturacion="flex", 
                            auth = session.get("user_auth"))


