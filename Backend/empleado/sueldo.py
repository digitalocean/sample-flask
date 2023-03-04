from flask import (
    Blueprint, g, render_template, request, session
)
from Backend.auth import auth
from datetime import datetime,timedelta

from Backend.database import database
from Backend.scriptGeneral import scriptGeneral
MS = Blueprint('sueldoChofer', __name__, url_prefix='/')


def consultarViajesChofer(_desde,_hasta):
    midb = database.connect_db()
    cursor = midb.cursor()
    columnas = ["Fecha","Numero de envío","Direccion completa","Localidad","Vendedor","Estado","Motivo","Chofer","Precio","Costo"]
    sql = "select Fecha,Numero_envío,Direccion_Completa,Localidad,Vendedor,estado_envio,motivo_noenvio,Chofer,Costo from sueldos where Fecha between %s and %s"
    values = (_desde,_hasta)
    cursor.execute(sql,values)
    viajes = []
    for x in cursor.fetchall():
        viajes.append(x)
    return columnas,viajes

@MS.route("/misueldo", methods=["GET","POST"])
@auth.login_required
def sueldoChofer():
    session.permanent = True
    MS.permanent_session_lifetime = timedelta(minutes=30)
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
            sqlFaltantes = f"select count(*) from sueldos where Costo is null and Fecha BETWEEN {desde} AND {hasta}"
            cursor.execute(sqlFaltantes)
            sinPrecio = cursor.fetchone()[0]
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
                try:
                    total += viaje[1]
                except:
                    sinPrecio += 1
                if viaje[1] == 0:
                    sabados +=1
                viajes.append(viaje)

            return render_template("facturacion/sueldoChofer.html",
                        desde=desde,
                        hasta=hasta,
                        mensaje_error = f"{sinPrecio} envios sin cotizar",
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
            error = 0
            levantada = 0
            ayudaDeposito = 0
            for viajeTupla in cursor.fetchall():
                if viajeTupla[4] == "Levantada":
                    levantada += 1
                elif viajeTupla[4] == "ayuda deposito":
                    ayudaDeposito += 1
                elif viajeTupla[6] == 0:
                    viajeSabado +=1
                else:
                    cantidad += 1
                try:
                    suma += viajeTupla[6]
                except:
                    error += 1
                viaje = list(viajeTupla)
                viajes.append(viaje)
            return render_template("empleado/sueldoChofer.html",
                                    cliente=chofer,
                                    desde=desde,
                                    hasta=hasta,
                                    titulo="Mi sueldo", 
                                    cabezeras = cabezeras,
                                    tipo_facturacion="flex", 
                                    viajes=viajes, 
                                    cantidad = f"Cantidad de visitas: {cantidad} || {levantada} retiros de productos || {ayudaDeposito} otros ||{error} errores ",
                                    total=f"${suma} y {viajeSabado} viajes de sabados", 
                                    clientes = scriptGeneral.consultar_clientes(midb), 
                                    auth = session.get("user_auth")
                                    )