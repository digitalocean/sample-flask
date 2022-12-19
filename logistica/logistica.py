from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
from .script import  geolocalizarFaltantes
from descargaLogixs import descargaLogixs

lg = Blueprint('logistica', __name__, url_prefix='/')



@lg.route("/descargalogixs")
@auth.login_required
def descargaLogixsBoton():
    tiempoinicio = datetime.now()
    midb = database.connect_db()
    descargaLogixs.descargaLogixs(midb)
    finDescargaLogixs = datetime.now()
    print(f"Tiempo de actualizacion desde logixs: {finDescargaLogixs - tiempoinicio}")
    geolocalizarFaltantes(midb)
    midb.close()
    tiempofinal = datetime.now()
    print(f"Tiempo de geolocalizacion: {tiempofinal - finDescargaLogixs}")
    duracion = tiempofinal - tiempoinicio
    print(f"Tiempo total: {duracion}")
    return redirect ("logistica/vistamapa")


@lg.route("/busquedaAdmin")
@auth.login_required
def busqueda():
    mjstbla = ""
    midb = database.connect_db()
    cursor = midb.cursor()
    busqueda = request.args.get("buscar")
    columnas = "Fecha,Hora,id,Zona,Numero_envío,Chofer,Direccion_Completa,Vendedor,Precio,Costo,estado_envio,motivo_noenvio,Correo_chofer,Foto_domicilio"
    cabezeras = ["Accion","Fecha","Hora","ID","Zona","Numero de envio","Chofer","Direccion","Vendedor","Precio","Costo","estado_envio","Motivo","Modifico","Tiene foto"]
    #  order by Numero_envío, Fecha desc,Hora desc
    if busqueda.lower() == "entregadoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' group by Numero_envío having count(Numero_envío) >1) and estado_envio = 'Entregado' and Fecha > '2022-09-01' order by Numero_envío"
    elif busqueda.lower() == "noentregadoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'No Entregado' group by Numero_envío having count(Numero_envío) >1) and motivo_noenvio in ('Nadie en Domicilio (Reprogramado)','Rechazado por el comprador') order by Numero_envío"
    elif busqueda.lower() == "encaminoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'En Camino' group by Numero_envío having count(Numero_envío) >1) and estado_envio = 'En Camino' order by Numero_envío"
    elif busqueda.lower() == "segundasvueltas":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' group by Numero_envío having count(Numero_envío) >1) order by Fecha desc, Hora desc, Numero_envío"
    elif busqueda.lower() == "tercerasvueltas":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' group by Numero_envío having count(Numero_envío) >2) order by Fecha desc, Hora desc, Numero_envío"
    elif busqueda.lower() == "sinencamino":
        sql = """
        select H.Fecha,H.Hora,H.id,H.Zona,H.Numero_envío,H.Chofer,concat(V.Direccion,V.Localidad),V.Vendedor,H.Precio,H.Costo,H.estado_envio,H.motivo_noenvio,H.Correo_chofer,H.Foto_domicilio 
	        from historial_estados as H join ViajesFlexs as V on H.Numero_envío = V.Numero_envío
		        where lower(H.estado_envio) in ('entregado','no entregado','listo para salir (sectorizado)') 
                and not H.Numero_envío in 
			        (select Numero_envío from historial_estados where estado_envio in ('En Camino') or motivo_noenvio in ('Cancelado'))
            """
    else:
        sql = f"select {columnas} from historial_estados where Numero_envío like '%{busqueda}%' or Chofer like '%{busqueda}%' or Vendedor like '%{busqueda}%' or Direccion_completa like '%{busqueda}%' or estado_envio like '%{busqueda}%' or motivo_noenvio like '%{busqueda}%' order by Fecha desc, Hora desc;"
    cursor.execute(sql)
    resultado = cursor.fetchall()
    if len(resultado) == 0:
        sql = f"select Fecha, Numero_envío, Direccion, Localidad, Vendedor,estado_envio,Motivo,ultimo_motivo from ViajesFlexs where Numero_envío like '%{busqueda}%' or Chofer like '%{busqueda}%' or Vendedor like '%{busqueda}%' or Direccion like '%{busqueda}%' order by Fecha desc"
        cursor.execute(sql)
        resultado = cursor.fetchone()
        lista = (resultado,)
        mjstbla = "No se registro historial de este envio"
        cabezeras = ["Fecha", "Numero_envío", "Direccion", "Localidad", "Vendedor","Estado","Motivo","Ultimo motivo"]
        return render_template("logistica/VistaTabla.html", titulo="Busqueda", viajes=lista ,columnas = cabezeras, cant_columnas = len(cabezeras), mensaje_tabla = mjstbla, auth = session.get("user_auth"))
    lista = []
    cobra = 0
    for x in resultado:
        lista.append(x)
    return render_template("logistica/VistaTabla.html", titulo="Busqueda", viajes=lista,cobra = cobra ,columnas = cabezeras, cant_columnas = len(cabezeras),contador = 0, historial = True, auth = session.get("user_auth"))

@lg.route("/busquedaNumeroEnvio")
@auth.login_required
def busquedaNumeroEnvio():
    busqueda = request.args.get("buscar")
    sql = f"""select fecha,hora,Numero_envío,(select Direccion from ViajesFlexs where Numero_envío = "{busqueda}"),(select Localidad from ViajesFlexs where Numero_envío = "{busqueda}"),vendedor((select Vendedor  from ViajesFlexs where Numero_envío = "{busqueda}")) ,"Retirado" from retirado where Numero_envío = "{busqueda}"
    union
    select fecha,hora,Numero_envío,(select Direccion from ViajesFlexs where Numero_envío = "{busqueda}"),(select Localidad from ViajesFlexs where Numero_envío = "{busqueda}"),vendedor((select Vendedor  from ViajesFlexs where Numero_envío = "{busqueda}")) ,"Sectorizado" from sectorizado where Numero_envío = "{busqueda}"
    union
    select fecha,hora,Numero_envío,(select Direccion from ViajesFlexs where Numero_envío = "{busqueda}"),(select Localidad from ViajesFlexs where Numero_envío = "{busqueda}"),vendedor((select Vendedor  from ViajesFlexs where Numero_envío = "{busqueda}")) ,"En Camino" from en_camino where Numero_envío = "{busqueda}"
    union
    select Fecha,Hora,Numero_envío,(select Direccion from ViajesFlexs where Numero_envío = "{busqueda}"),(select Localidad from ViajesFlexs where Numero_envío = "{busqueda}"),vendedor((select Vendedor  from ViajesFlexs where Numero_envío = "{busqueda}")) ,estado_envio from historial_estados where Numero_envío = "{busqueda}";
    """
    print(sql)
    midb = database.connect_db()
    cursor = midb.cursor()
    cabezeras = ["Fecha","Hora","Numero de envio","Direccion","Localidad","Vendedor","Estado"]
    cursor.execute(sql)
    resultado = cursor.fetchall()
    print(resultado)
    lista = []
    print(len(resultado))
    for x in resultado:
        lista.append(x)
    return render_template("logistica/VistaTabla.html", 
                            titulo="Busqueda",
                            viajes=lista,
                            columnas = cabezeras,
                            cant_columnas = len(cabezeras),
                            contador = 0,
                            auth = session.get("user_auth"))