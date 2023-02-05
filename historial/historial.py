from flask import Blueprint, redirect, render_template, request, session,Response,send_file
from ftplib import FTP
from base64 import b64decode
from auth import auth
from database import database
hsList = Blueprint('historialEnvios', __name__, url_prefix='/')
 

columnas = """ H.Fecha, H.Hora, H.id, H.Numero_envío,H.Direccion_completa,vendedor(H.Vendedor),H.Localidad,H.Chofer,
                H.estado_envio,H.motivo_noenvio,H.Precio,H.Costo,H.Currentlocation,H.Correo_chofer,H.Foto_domicilio"""

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

def get_image_from_db(id):
    # Obtiene una conexión a la base de datos
    conn = database.connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM foto_domicilio WHERE id = %s", (id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result[0]

@hsList.route('/imageget/<fileId>')
def imageGet(fileId):
    image_base64_encoded = get_image_from_db(fileId)
    image_binary = b64decode(image_base64_encoded)        
    with open("temp_image.jpg", "wb") as f:
        f.write(image_binary)
    return send_file("temp_image.jpg", mimetype="image/jpeg")

@hsList.route('/image',methods=["POST"])
def image():
    idImage = request.form["idFoto"]
    image_base64_encoded = get_image_from_db(idImage)
    image_binary = b64decode(image_base64_encoded)        
    with open("temp_image.jpg", "wb") as f:
        f.write(image_binary)
    return send_file("temp_image.jpg", mimetype="image/jpeg")

# LECTURA DE HOSTINGER FTP
@hsList.route('/imageFTP/<filename>')
def imageFTP(filename):
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

@hsList.route("/busquedaAdmin")
@auth.login_required
def busqueda():
    mjstbla = ""
    midb = database.connect_db()
    cursor = midb.cursor()
    busqueda = request.args.get("buscar")
    cabezeras = ["Accion","Fecha","Hora","ID","Zona","Numero de envio","Chofer","Direccion","Vendedor","Precio","Costo","estado_envio","Motivo","Modifico","Tiene foto"]
    order = " order by H.Fecha desc, H.Numero_envío"
    if busqueda.lower() == "entregadoduplicado":
        sql = f"select {columnas} from historial_estados as H where H.Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' group by Numero_envío having count(*) >1) and estado_envio = 'Entregado' and Fecha > '2022-09-01' {order}"
    elif busqueda.lower() == "noentregadoduplicado":
        sql = f"select {columnas} from historial_estados as H where H.Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'No Entregado' and not motivo_noenvio in ('Domicilio no visitado','Cancelado') and not estado_envio = 'Lista para Devolver' and tipo_envio = 2 group by Numero_envío having count(*) >1) and motivo_noenvio in ('Nadie en Domicilio (Reprogramado)','Rechazado por el comprador') {order}"
    elif busqueda.lower() == "encaminoduplicado":
        sql = f"select {columnas} from historial_estados as H where H.Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'En Camino' group by Numero_envío having count(*) >1) and estado_envio = 'En Camino' {order}"
    elif busqueda.lower() == "segundasvueltas":
        sql = f"select {columnas} from historial_estados as H where H.Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' and not estado_envio = 'Lista para Devolver' group by Numero_envío having count(*) >1) and estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' {order}"
    elif busqueda.lower() == "tercerasvueltas":
        sql = f"select {columnas} from historial_estados as H where H.Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'Entregado' or motivo_noenvio = 'Nadie en Domicilio (Reprogramado)' group by Numero_envío having count(*) >2) {order}"
    elif busqueda.lower() == "sinencamino":
        sql = f"""
        select {columnas} from historial_estados as H join ViajesFlexs as V on H.Numero_envío = V.Numero_envío
        where 
            (H.estado_envio = 'entregado' or motivo_noenvio in 
                    ("Nadie en Domicilio (Reprogramado)","Rechazado por el comprador"))
        and 
            not H.Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'En Camino')
        """
    #H.Fecha,H.Hora,H.id,H.Zona,H.Numero_envío,H.Chofer,H.Direccion_completa,H.Localidad,V.Vendedor,V.Currentlocation,H.estado_envio,H.motivo_noenvio,H.Correo_chofer,H.Foto_domicilio 
    else:
        cabezeras = "accion","Fecha","Hora","id","Zona","Numero de envío","Chofer","Direccion Completa","Localidad","Vendedor","Ubicacion","Estado","Motivo","Correo_chofer","Foto_domicilio"
        sql = f"""select {columnas} from historial_estados as H join ViajesFlexs as V on V.Numero_envío = H.Numero_envío
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
        return render_template("historial/VistaTabla.html", 
                                titulo="Busqueda", 
                                viajes=lista ,
                                columnas = cabezeras, 
                                cant_columnas = len(cabezeras), 
                                mensaje_tabla = mjstbla, 
                                historial = True, 
                                auth = session.get("user_auth"))
    lista = []
    cobra = 0
    for x in resultado:
        lista.append(x)
    return render_template("historial/VistaTabla.html", 
                            titulo="Busqueda", 
                            viajes=lista,
                            cobra = cobra ,
                            columnas = cabezeras, 
                            cant_columnas = len(cabezeras),
                            contador = 0, 
                            historial = True, 
                            auth = session.get("user_auth"))

@hsList.route("/busquedaNumeroEnvio")
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
    return render_template("historial/VistaTabla.html", 
                            titulo="Busqueda",
                            viajes=lista,
                            columnas = cabezeras,
                            cant_columnas = len(cabezeras),
                            contador = 0,
                            auth = session.get("user_auth"))



@hsList.route("/logistica/pendientes/",methods=["GET","POST"])
@auth.login_required
def pendientes():
    cabezeras = ["Fecha", "Zona", "Numero_envío","Direccion","Vendedor","Localidad","Chofer","Estado envio","Motivo","QR"] 
    sql = f"select V.Fecha, V.Zona, V.Numero_envío,V.Direccion,V.Localidad,vendedor(V.Vendedor),V.Chofer,V.estado_envio,V.Motivo,R.scanner from ViajesFlexs as V left join sectorizado as S on V.Numero_envío = S.Numero_envío left join retirado as R on R.Numero_envío = V.Numero_envío where V.Fecha <= current_date() "
    if request.method=="POST":
        condicion = request.form.get("filtro")
        group = request.form.get("agrupador")
        tipoEnvio = request.form.get("tipoEnvio")
        groupBy = f"group by V.Numero_envío order by V.Fecha desc, {group}"
        if condicion == "retirado":
            sqlPendientes = f"{sql} and V.tipo_envio = {tipoEnvio} and V.estado_envio in ('Listo para salir (Sectorizado)','Retirado') {groupBy}"
        if condicion == "EnCamino":
            sqlPendientes = f"{sql} and V.tipo_envio = {tipoEnvio} and V.estado_envio in ('En Camino','Reasignado') {groupBy}"
        if condicion == "NoEntregado":
            sqlPendientes = f"{sql} and V.tipo_envio = {tipoEnvio} and V.estado_envio in ('No Entregado') and not V.Motivo in ('Cancelado','Rechazado por el comprador') {groupBy}"
        if condicion == "Lista Para Retirar":
            sqlPendientes = f"{sql} and V.tipo_envio = {tipoEnvio} and V.estado_envio in ('Lista Para Retirar') {groupBy}"
        print(sqlPendientes)
        viajes,cant = consultaPendientes(sqlPendientes)
        return render_template("historial/pendientes.html", 
                                titulo="pendientes", 
                                viajes=viajes,
                                cantidad = cant,
                                columnas = cabezeras, 
                                cant_columnas = len(cabezeras), 
                                auth = session.get("user_auth"))
    else:
        sqlPendientes = f"{sql} and V.estado_envio in ('Cargado','En Camino','Listo para salir (Sectorizado)','No Entregado','Reasignado','Retirado') and (V.Motivo != 'Cancelado' or V.Motivo is null) group by Numero_envío order by V.Fecha desc,V.Chofer"
        viajes,cant = consultaPendientes(sqlPendientes)
        return render_template("historial/pendientes.html", 
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
    sql = f"select {columnas} from historial_estados as H order by id desc limit {limiteMinimo},300"
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