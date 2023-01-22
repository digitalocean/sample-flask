from flask import Blueprint, redirect, render_template, request, session,Response
import base64
from auth import auth
from database import database
hsList = Blueprint('historialEnvios', __name__, url_prefix='/')

def consultaPendientes(sql):
    viajes =[]
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()
    cant = 0
    for x in resultado:
        cant += 1
        viajes.append(x)
    return viajes,cant

def get_image(image_id):
    conn = database.connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM foto_domicilio WHERE id = %s", (image_id))
    image_64 = cursor.fetchone()[0]
    print(image_64)
    image_binary = base64.b64decode(image_64)
    cursor.close()
    return image_binary

@hsList.route('/image',methods = ["POST"])
def image():
    idFoto = request.form["idFoto"]
    
    image_binary = get_image(idFoto)
    response = Response(image_binary, content_type="image/jpeg")
    return response

@hsList.route("/logistica/almapa/<envio>",methods=["GET","POST"])
@auth.login_required
def alMapa(envio):
    user_id = session.get("user_id")
    sql = f"update ViajesFlexs set `Check` = null, estado_envio = 'Listo para salir (Sectorizado)',Motivo = null,Foto_domicilio = '{user_id}' where Numero_envío = '{envio}'"
    midb = database.connect_db()
    cursor = midb.cursor()
    print(sql)
    cursor.execute(sql)
    midb.commit()
    return redirect("/logistica/pendientes/")


@hsList.route("/logistica/pendientes/",methods=["GET","POST"])
@auth.login_required
def pendientes():
    cabezeras = ["Fecha", "Zona", "Numero_envío","Direccion","Vendedor","Localidad","Chofer","Estado envio","Motivo","QR"] 
    if request.method=="POST":
        condicion = request.form.get("filtro")
        group = request.form.get("agrupador")
        tipoEnvio = request.form.get("tipoEnvio")
        groupBy = f"group by Numero_envío order by V.Fecha desc, {group}"
        if condicion == "retirado":
            sqlPendientes = f"select V.Fecha, V.Zona, V.Numero_envío,V.Direccion,V.Localidad,vendedor(V.Vendedor),V.Chofer,V.estado_envio,V.Motivo,ifnull(ifnull(R.scanner,S.scanner),V.Scanner) from ViajesFlexs as V left join sectorizado as S on V.Numero_envío = S.Numero_envío left join retirado as R on R.Numero_envío = S.Numero_envío where V.Fecha <= current_date() and V.tipo_envio = {tipoEnvio} and V.estado_envio in('Listo para salir (Sectorizado)','Retirado') {groupBy}"
        if condicion == "EnCamino":
            sqlPendientes = f"select V.Fecha, V.Zona, V.Numero_envío,V.Direccion,V.Localidad,vendedor(V.Vendedor),V.Chofer,V.estado_envio,V.Motivo,ifnull(ifnull(R.scanner,S.Scanner),V.Scanner) from ViajesFlexs as V left join sectorizado as S on V.Numero_envío = S.Numero_envío left join retirado as R on R.Numero_envío = S.Numero_envío where V.Fecha <= current_date() and V.tipo_envio = {tipoEnvio} and V.estado_envio in('En Camino','Reasignado') {groupBy}"
        if condicion == "NoEntregado":
            sqlPendientes = f"select V.Fecha, V.Zona, V.Numero_envío,V.Direccion,V.Localidad,vendedor(V.Vendedor),V.Chofer,V.estado_envio,V.Motivo,ifnull(ifnull(R.scanner,S.Scanner),V.Scanner) from ViajesFlexs as V left join sectorizado as S on V.Numero_envío = S.Numero_envío left join retirado as R on R.Numero_envío = S.Numero_envío where V.Fecha <= current_date() and V.tipo_envio = {tipoEnvio} and V.estado_envio in('No Entregado') and not V.Motivo in ('Cancelado','Rechazado por el comprador') {groupBy}"
        viajes,cant = consultaPendientes(sqlPendientes)
        return render_template("logistica/pendientes.html", 
                                titulo="pendientes", 
                                viajes=viajes,
                                cantidad = cant,
                                columnas = cabezeras, 
                                cant_columnas = len(cabezeras), 
                                auth = session.get("user_auth"))
    else:
        sqlPendientes = f"select V.Fecha, V.Zona, V.Numero_envío,V.Direccion,V.Localidad,vendedor(V.Vendedor),V.Chofer,V.estado_envio,V.Motivo,ifnull(ifnull(R.scanner,S.scanner),V.Scanner) from ViajesFlexs as V left join sectorizado as S on V.Numero_envío = S.Numero_envío left join retirado as R on R.Numero_envío = S.Numero_envío where V.Fecha <= current_date() and V.estado_envio in('Cargado','En Camino','Listo para salir (Sectorizado)','No Entregado','Reasignado','Retirado','Lista Para Retirar') and (V.Motivo != 'Cancelado' or V.Motivo is null) order by V.Fecha desc, Chofer"
        viajes,cant = consultaPendientes(sqlPendientes)
        return render_template("logistica/pendientes.html", 
                                titulo="pendientes", 
                                viajes=viajes,
                                cantidad = cant,
                                columnas = cabezeras, 
                                cant_columnas = len(cabezeras), 
                                auth = session.get("user_auth"))

        
@hsList.route("/logistica/historial/<pagina>")
@auth.login_required
def historial(pagina):
    viajes =[]
    pagina = int(pagina)
    opcion = pagina-1
    limiteMinimo = opcion*300
    cabezeras = ["Accion","Fecha", "Hora", "id", "Numero_envío","Direccion","Vendedor","Localidad","Chofer","Estado envio","Motivo","precio","Costo","Ubicacion estado","Modifico","Tiene Foto"]
    sql = f"select Fecha, Hora, id, Numero_envío,Direccion_completa,vendedor(Vendedor),Localidad,Chofer,estado_envio,motivo_noenvio,Precio,Costo,Ubicacion_ultimoestado,Correo_chofer,Foto_domicilio from historial_estados order by id desc limit {limiteMinimo},300"
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()
    for x in resultado:
        viajes.append(x)
    if pagina < 10: pagina = 8
    listaBotones = []
    for x in range(20):
        listaBotones.append(pagina-7)
        pagina = pagina + 1
    return render_template("historial/VistaTabla.html", 
                            titulo="Busqueda", 
                            viajes=viajes,
                            tablas=True,
                            listaBotones = listaBotones,
                            contador = 0, 
                            columnas = cabezeras, 
                            cant_columnas = len(cabezeras), 
                            auth = session.get("user_auth"),historial = True)

    
@hsList.route("/logistica/historial/anular/<id>")
@auth.login_required
def eliminarHistorial(id):
    midb=database.connect_db()
    cursor = midb.cursor()
    sql = f"update historial_estados set estado_envio = concat((select estado_envio from historial_estados where id = {id}),'/anulado'), motivo_noenvio = concat((select motivo_noenvio from historial_estados where id = {id}),'/anulado') WHERE id = {id};"
    cursor.execute(sql)
    midb.commit()
    return redirect("/logistica/historial/1")