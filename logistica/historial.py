from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
lgHS = Blueprint('historialEnvios', __name__, url_prefix='/')

@lgHS.route("/logistica/historial/<pagina>")
@auth.login_required
def historial(pagina):
    viajes =[]
    pagina = int(pagina)
    opcion = pagina-1
    limiteMinimo = opcion*300
    cabezeras = ["Accion","Fecha", "Hora", "id", "Numero_envío","Direccion","Vendedor","Localidad","Chofer","Estado envio","Motivo","precio","Costo","Ubicacion estado","Modifico","Tiene Foto"]
    sql = f"select Fecha, Hora, id, Numero_envío,Direccion_completa,vendedor(Vendedor),Localidad,Chofer,estado_envio,motivo_noenvio,Ubicacion_ultimoestado,Correo_chofer,Foto_domicilio,Precio,Costo from historial_estados where estado_envio != 'Listo para salir (Sectorizado)' order by id desc limit {limiteMinimo},300"
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()
    for x in resultado:
        fecha = x[0]
        hora = x[1]
        id = x[2]
        nenvio = x[3]
        direccion = x[4]
        vendedor = x[5]
        localidad = x[6]
        chofer = x[7]
        estado = x[8]
        motivo = x[9]
        ubicacion = x[10]
        correo = x[11]
        foto = x[12]
        precio = x[13]
        costo = x[14]
        paquete = [fecha,hora,id,nenvio,direccion,vendedor,localidad,chofer,estado,motivo,precio,costo,ubicacion,correo,foto]
        viajes.append(paquete)
    if pagina < 10: pagina = 8
    listaBotones = []
    for x in range(20):
        listaBotones.append(pagina-7)
        pagina = pagina + 1
    return render_template("logistica/VistaTabla.html", titulo="Busqueda", viajes=viajes,tablas=True,listaBotones = listaBotones,contador = 0, columnas = cabezeras, cant_columnas = len(cabezeras), auth = session.get("user_auth"),historial = True)

    
@lgHS.route("/logistica/historial/delete/<id>")
@auth.login_required
@auth.admin_required
def eliminarHistorial(id):
    midb=database.connect_db()
    cursor = midb.cursor()
    sql = f"DELETE FROM historial_estados WHERE id = '{id}';"
    cursor.execute(sql)
    midb.commit()
    return redirect("/logistica/historial/1")