from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
from .script import  geolocalizarFaltantes
from tareasProgramadas.tareasProgramadas import descargaDesdePlanillas
from .Envio import Envio
lg = Blueprint('logistica', __name__, url_prefix='/')

@lg.route("/descargalogixs")
@auth.login_required
def descargaLogixsBoton():
    descargaDesdePlanillas()
    return redirect ("logistica/vistamapa")


@lg.route('/formularioEdicionLogistica')
def mostrarFormulario():
  direccion = request.args.get('direccion')
  localidad = request.args.get('localidad')
  vendedor = request.args.get('vendedor')
  numeroEnvio = request.args.get('numeroEnvio')
  estado = request.args.get('estado')
  return render_template('logistica/formularioEdicion.html', direccion=direccion, localidad=localidad, vendedor=vendedor, numeroEnvio=numeroEnvio, estado=estado)

@lg.route('/guardarCambiosEnvio',methods=["POST"])
def guardarCambiosEnvio():
    numEnvio = request.form.get("numEnvio")
    direccion = request.form.get("direccion")
    localidad = request.form.get("localidad")
    vendedor = request.form.get("vendedor")
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("update ViajesFlexs set Direccion = %s,Localidad = %s where Numero_envío = %s",(direccion,localidad,numEnvio))
    midb.commit()
    geolocalizarFaltantes(midb)
    return "exito"

@lg.route("/busquedaAdmin")
@auth.login_required
def busqueda():
    mjstbla = ""
    midb = database.connect_db()
    cursor = midb.cursor()
    busqueda = request.args.get("buscar")
    columnas = "Fecha,Hora,id,Zona,Numero_envío,Chofer,Direccion_Completa,Vendedor,Precio,Costo,estado_envio,motivo_noenvio,Correo_chofer,Foto_domicilio"
    cabezeras = ["Accion","Fecha","Hora","ID","Zona","Numero de envio","Chofer","Direccion","Vendedor","Precio","Costo","estado_envio","Motivo","Modifico","Tiene foto"]
    order = " order by Fecha desc, Numero_envío"
    if busqueda.lower() == "entregadoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' group by Numero_envío having count(*) >1) and estado_envio = 'Entregado' and Fecha > '2022-09-01' {order}"
    elif busqueda.lower() == "noentregadoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'No Entregado' and not motivo_noenvio in ('Domicilio no visitado','Cancelado') and not estado_envio = 'Lista para Devolver' and tipo_envio = 2 group by Numero_envío having count(*) >1) and motivo_noenvio in ('Nadie en Domicilio (Reprogramado)','Rechazado por el comprador') {order}"
    elif busqueda.lower() == "encaminoduplicado":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'En Camino' group by Numero_envío having count(*) >1) and estado_envio = 'En Camino' {order}"
    elif busqueda.lower() == "segundasvueltas":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' and not estado_envio = 'Lista para Devolver' group by Numero_envío having count(*) >1) and estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' {order}"
    elif busqueda.lower() == "tercerasvueltas":
        sql = f"select {columnas} from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' group by Numero_envío having count(*) >2) {order}"
    elif busqueda.lower() == "sinencamino":
        sql = """
        select H.Fecha,H.Hora,H.id,H.Zona,H.Numero_envío,H.Chofer,concat(V.Direccion,V.Localidad),V.Vendedor,H.Precio,H.Costo,H.estado_envio,H.motivo_noenvio,H.Correo_chofer,H.Foto_domicilio 
	        from historial_estados as H join ViajesFlexs as V on H.Numero_envío = V.Numero_envío
		        where lower(H.estado_envio) in ('entregado','no entregado','listo para salir (sectorizado)') 
                and not H.Numero_envío in 
			        (select Numero_envío from historial_estados where estado_envio in ('En Camino') or motivo_noenvio in ('Cancelado'))
            """
    else:
        cabezeras = "accion","Fecha","Hora","id","Zona","Numero de envío","Chofer","Direccion Completa","Localidad","Vendedor","Ubicacion","Estado","Motivo","Correo_chofer","Foto_domicilio"
        sql = f"""select H.Fecha,H.Hora,H.id,H.Zona,H.Numero_envío,H.Chofer,H.Direccion_completa,H.Localidad,V.Vendedor,V.Currentlocation,H.estado_envio,H.motivo_noenvio,H.Correo_chofer,H.Foto_domicilio 
        from historial_estados as H join ViajesFlexs as V on V.Numero_envío = H.Numero_envío
        where V.Numero_envío like '%{busqueda}%' or H.Chofer like '%{busqueda}%' or V.Vendedor like '%{busqueda}%' or H.Direccion_completa like '%{busqueda}%' or H.estado_envio like '%{busqueda}%' or H.motivo_noenvio like '%{busqueda}%' order by Fecha desc, Hora desc;"""
    cursor.execute(sql)
    resultado = cursor.fetchall()
    if len(resultado) == 0:
        sql = f"select Fecha, Numero_envío, Direccion, Localidad, Vendedor,estado_envio,Motivo from ViajesFlexs where Numero_envío like '%{busqueda}%' or Chofer like '%{busqueda}%' or Vendedor like '%{busqueda}%' or Direccion like '%{busqueda}%' order by Fecha desc"
        cursor.execute(sql)
        resultado = cursor.fetchone()
        lista = (resultado,)
        mjstbla = "No se registro historial de este envio"
        cabezeras = ["Fecha", "Numero_envío", "Direccion", "Localidad", "Vendedor","Estado","Motivo"]
        return render_template("logistica/VistaTabla.html", 
                                titulo="Busqueda", 
                                viajes=lista ,
                                columnas = cabezeras, 
                                cant_columnas = len(cabezeras), 
                                mensaje_tabla = mjstbla, 
                                auth = session.get("user_auth"))
    lista = []
    cobra = 0
    for x in resultado:
        lista.append(x)
    return render_template("logistica/VistaTabla.html", 
                            titulo="Busqueda", 
                            viajes=lista,
                            cobra = cobra ,
                            columnas = cabezeras, 
                            cant_columnas = len(cabezeras),
                            contador = 0, 
                            historial = True, 
                            auth = session.get("user_auth"))

@lg.route("/busquedaNumeroEnvio")
@auth.login_required
def busquedaNumeroEnvio():
    busqueda = request.args.get("buscar")
    direccion = f"(select Direccion from ViajesFlexs where Numero_envío = '{busqueda}')"
    localidad = f"(select Localidad from ViajesFlexs where Numero_envío = '{busqueda}')"
    vendedor = f"vendedor((select Vendedor from ViajesFlexs where Numero_envío = '{busqueda}'))"
    sql = f"""select fecha,hora,"",Numero_envío,{direccion},{localidad},{vendedor},choferCorreo(chofer),"Retirado",scanner from retirado where Numero_envío = "{busqueda}"
    union
    select fecha,hora,zona,Numero_envío,{direccion},{localidad},{vendedor},choferCorreo(chofer),"Sectorizado",scanner from sectorizado where Numero_envío = "{busqueda}"
    union
    select fecha,hora,"",Numero_envío,{direccion},{localidad},{vendedor},choferCorreo(chofer),"En Camino",scanner from en_camino where Numero_envío = "{busqueda}"
    union
    select Fecha,Hora,Zona,Numero_envío,{direccion},{localidad},{vendedor},Chofer,estado_envio,motivo_noenvio from historial_estados where Numero_envío = "{busqueda}";
    """
    print(sql)
    midb = database.connect_db()
    cursor = midb.cursor()
    cabezeras = ["Fecha","Hora","Zona","Numero de envio","Direccion","Localidad","Vendedor","Chofer","Estado","Motivo"]
    cursor.execute(sql)
    resultado = cursor.fetchall()
    lista = []
    for x in resultado:
        lista.append(x)
    return render_template("logistica/VistaTabla.html", 
                            titulo="Busqueda",
                            viajes=lista,
                            columnas = cabezeras,
                            cant_columnas = len(cabezeras),
                            contador = 0,
                            auth = session.get("user_auth"))



@lg.route("/logistica/ruteo")
@auth.login_required
def RuteoPrimera():
    from .mapa import consultaMapa
    midb = database.connect_db()
    cursor = midb.cursor()
    cabezeras = ["Zona","Fecha","Numero de envío","Direccion","Localidad","CP","vendedor","Chofer","Estado"]
    if "valuesMapa" in session.keys():
        valueMapa = session["valuesMapa"]
        cursor.execute(consultaMapa,(valueMapa,))
    else:
        cursor.execute(consultaMapa,(2,))
    resultado = cursor.fetchall()
    lista = []
    for x in resultado:
        zona = x[9]
        fecha = x[6]
        nEnvio = x[0]
        direccion = x[1]
        localidad = x[2]
        cp = x[13]
        vendedor = x[3]
        chofer = x[7]
        estado = x[8]
        lista.append([zona,fecha,nEnvio,direccion,localidad,cp,vendedor,chofer,estado])
    return render_template("logistica/VistaTabla.html", 
                            titulo="Ruteo",
                            viajes=lista,
                            columnas = cabezeras,
                            cant_columnas = len(cabezeras),
                            contador = 0,
                            auth = session.get("user_auth"))
