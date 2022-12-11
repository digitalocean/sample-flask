from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
hsList = Blueprint('historialEnvios', __name__, url_prefix='/')

@hsList.route("/logistica/pendientes/")
@auth.login_required
def pendientes():
    viajes =[]
    cabezeras = ["Fecha", "Numero_envío","Direccion","Vendedor","Localidad","Chofer","Estado envio","Motivo","QR"]
    sql = f"select V.Fecha, V.Numero_envío,V.Direccion,V.Localidad,vendedor(V.Vendedor),V.Chofer,V.estado_envio,V.Ultimo_motivo,ifnull(R.Scanner,S.Scanner) from ViajesFlexs as V left join historial_estados2 as S on V.Numero_envío = S.Numero_envío left join retirado as R on R.Numero_envío = S.Numero_envío where V.Fecha <= current_date() and V.estado_envio in ('Retirado','Listo para salir (Sectorizado)');"#('Cargado','En Camino','Fuera de Zona','Lista Para Retirar','Listo Para Retirar','Listo para salir (Sectorizado)','No Entregado','Reasignado','Retirado','Zona Peligrosa') and V.Ultimo_motivo != 'Cancelado' order by V.Fecha desc, Chofer"
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()
    cant = 0
    for x in resultado:
        cant += 1
        viajes.append(x)
    return render_template("logistica/pendientes.html", 
                            titulo="pendientes", 
                            viajes=viajes,
                            cantidad = cant,
                            columnas = cabezeras, 
                            cant_columnas = len(cabezeras), 
                            auth = session.get("user_auth"))

        
@hsList.route("/logistica/historial/")
@auth.login_required
def historial():
    viajes =[]
    pagina = int(pagina)
    opcion = pagina-1
    limiteMinimo = opcion*300
    cabezeras = ["Accion","Fecha", "Hora", "id", "Numero_envío","Direccion","Vendedor","Localidad","Chofer","Estado envio","Motivo","precio","Costo","Ubicacion estado","Modifico","Tiene Foto"]
    sql = f"select Fecha, Hora, id, Numero_envío,Direccion_completa,vendedor(Vendedor),Localidad,Chofer,estado_envio,motivo_noenvio,Ubicacion_ultimoestado,Correo_chofer,Foto_domicilio,Precio,Costo from historial_estados order by id desc limit {limiteMinimo},300"
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
    return render_template("logistica/VistaTabla.html", 
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
@auth.admin_required
def eliminarHistorial(id):
    midb=database.connect_db()
    cursor = midb.cursor()
    sql = f"update historial_estados set estado_envio = 'anulado', motivo_noenvio = 'anulado' WHERE id = '{id}';"
    cursor.execute(sql)
    midb.commit()
    return redirect("/logistica/historial/1")