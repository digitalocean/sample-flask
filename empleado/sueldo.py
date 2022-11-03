from flask import (
    Blueprint, g, render_template, request, session
)
from auth import auth
from datetime import datetime

from database import database
from scriptGeneral import scriptGeneral
MS = Blueprint('sueldoChofer', __name__, url_prefix='/')

@MS.route("/misueldo", methods=["GET","POST"])
@auth.login_required
def sueldoChofer():
    hoy = str(datetime.now())[0:10]
    if request.method == "GET":
        return render_template("empleado/sueldoChofer.html",
                        titulo="Facturacion", 
                        desde=hoy,
                        hasta=hoy,
                        clientes=scriptGeneral.consultar_clientes(database.connect_db()), 
                        tipo_facturacion="flex", 
                        auth = session.get("user_auth"))
    elif request.method == "POST":
        midb = database.connect_db()
        cursor = midb.cursor()
        chofer = session.get("user_id")
        desde = request.form["desde"]
        hasta = request.form["hasta"]
        
        viajes = []
        if session.get("user_auth") != "Chofer":
            cabezeras = ["Chofer","Sueldo"]
            sql = f"""
            select 
                Chofer,sum(Costo)
            from 
                sueldos 
            where  
                Fecha between '{desde}' and '{hasta}' 
            GROUP BY Chofer;"""

            cursor.execute(sql)
            sabados = 0
            sinPrecio = 0
            total = 0
            for viajeTupla in cursor.fetchall():
                viaje = list(viajeTupla)
                total += viaje[1]
                if viaje[1] == 0:
                    sabados +=1
                if viaje[1] == None:
                    sinPrecio += 1
                viajes.append(viaje)
            return render_template("facturacion/sueldoChofer.html",
                        desde=desde,
                        hasta=hasta,
                        titulo="Sueldos Flexs", 
                        cabezeras = cabezeras,
                        tipo_facturacion="flex", 
                        viajes=viajes,
                        total = total,
                        auth = session.get("user_auth")
                        )
        else:
            cabezeras = ["Fecha","Numero de envío","Direccion","Vendedor","Estado","Motivo","A cobrar"]
            sql = f"""
                    SELECT 
                        Fecha,Numero_envío,Direccion_Completa,Vendedor,estado_envio,motivo_noenvio,Costo 
                    FROM 
                        mmslogis_MMSPack.sueldos 
                    where 
                        Chofer = '{chofer}' and Fecha between '{desde}' and '{hasta}';"""
            cursor.execute(sql)
            viajeSabado = 0
            suma = 0
            cantidad = 0
            for viajeTupla in cursor.fetchall():
                cantidad += 1
                if type(viajeTupla[6]) == float:
                    suma += viajeTupla[6]
                viaje = list(viajeTupla)
                if viajeTupla[6] == 0:
                    viajeSabado +=1
                viajes.append(viaje)
            return render_template("empleado/sueldoChofer.html",
                                    cliente=chofer,
                                    desde=desde,
                                    hasta=hasta,
                                    titulo="Mi sueldo", 
                                    cabezeras = cabezeras,
                                    tipo_facturacion="flex", 
                                    viajes=viajes, 
                                    cantidad = f"Cantidad de visitas: {cantidad}",
                                    total=f"${suma} y {viajeSabado} viajes de sabados", 
                                    clientes = scriptGeneral.consultar_clientes(midb), 
                                    auth = session.get("user_auth")
                                    )