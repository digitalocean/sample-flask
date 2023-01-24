from flask import Blueprint, redirect, render_template, request, session,Response,send_file
from ftplib import FTP
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


@hsList.route('/image/<filename>')
def image(filename):
    # filename = "Screenshot_1673795214.png"
    ftp = FTP('109.106.251.113')
    ftp.login(user='appChofer@mmslogistica.com', passwd='(15042020)_')
    ftp.cwd('/foto_domicilio/')
    # public_html/foto_domicilio/Screenshot_1673795214.png
    image = ftp.retrbinary('RETR ' + filename, open('image.png', 'wb').write)
    ftp.quit()
    return send_file("image.png")


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
    sql = f"select V.Fecha, V.Zona, V.Numero_envío,V.Direccion,V.Localidad,vendedor(V.Vendedor),V.Chofer,V.estado_envio,V.Motivo,ifnull(ifnull(R.scanner,S.scanner),V.Scanner) from ViajesFlexs as V inner join sectorizado as S on V.Numero_envío = S.Numero_envío inner join retirado as R on R.Numero_envío = S.Numero_envío where V.Fecha <= current_date() "
    if request.method=="POST":
        condicion = request.form.get("filtro")
        group = request.form.get("agrupador")
        tipoEnvio = request.form.get("tipoEnvio")
        groupBy = f"group by V.Numero_envío order by V.Fecha desc, {group}"
        if condicion == "retirado":
            sqlPendientes = f" and V.tipo_envio = {tipoEnvio} and V.estado_envio in ('Listo para salir (Sectorizado)','Retirado') {groupBy}"
        if condicion == "EnCamino":
            sqlPendientes = f"{sql} and V.tipo_envio = {tipoEnvio} and V.estado_envio in ('En Camino','Reasignado') {groupBy}"
        if condicion == "NoEntregado":
            sqlPendientes = f"{sql} and V.tipo_envio = {tipoEnvio} and V.estado_envio in ('No Entregado') and not V.Motivo in ('Cancelado','Rechazado por el comprador') {groupBy}"
        if condicion == "Lista Para Retirar":
            sqlPendientes = f"{sql} and V.tipo_envio = {tipoEnvio} and V.estado_envio in ('Lista Para Retirar') {groupBy}"
        viajes,cant = consultaPendientes(sqlPendientes)
        return render_template("logistica/pendientes.html", 
                                titulo="pendientes", 
                                viajes=viajes,
                                cantidad = cant,
                                columnas = cabezeras, 
                                cant_columnas = len(cabezeras), 
                                auth = session.get("user_auth"))
    else:
        sqlPendientes = f"{sql} and V.estado_envio in('Cargado','En Camino','Listo para salir (Sectorizado)','No Entregado','Reasignado','Retirado') and (V.Motivo != 'Cancelado' or V.Motivo is null) group by Numero_envío order by V.Fecha desc,V.Chofer"
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
    sql = f"select Fecha, Hora, id, Numero_envío,Direccion_completa,vendedor(Vendedor),Localidad,Chofer,estado_envio,motivo_noenvio,Precio,Costo,Currentlocation,Correo_chofer,Foto_domicilio from historial_estados order by id desc limit {limiteMinimo},300"
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