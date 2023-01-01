from datetime import datetime
from flask import (
    Blueprint, g, render_template, request, session
)
from auth import auth
from informeErrores import informeErrores
from openpyxl import Workbook
from openpyxl.drawing.image import Image


from database import database
from scriptGeneral import scriptGeneral
fb = Blueprint('facturacion', __name__, url_prefix='/')



@fb.route('/consulta_flexs')
@auth.login_required
def consultaFlexs():
    hoy = str(datetime.now())[0:10]
    return render_template("facturacion/tabla_viajes.html",
                        titulo="Facturacion", 
                        desde=hoy,
                        hasta=hoy,
                        clientes=scriptGeneral.consultar_clientes(database.connect_db()), 
                        tipo_facturacion="flex", 
                        auth = session.get("user_auth"))

@fb.route("/facturacion_flex", methods=["GET"])
@auth.login_required
def facturacionFlex():
    midb = database.connect_db()
    cursor = midb.cursor()
    cliente = request.args.get("cliente")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    viajes = []
    suma = 0
    book = Workbook()
    sheet = book.active
    sheet["A1"] = "id"
    sheet["B1"] = "Numero_envío"
    sheet["C1"] = "Vendedor"
    sheet["D1"] = "Direccion_Completa"
    sheet["E1"] = "Fecha"
    sheet["F1"] = "Localidad"
    sheet["G1"] = "Recibio"
    sheet["H1"] = "Chofer"
    sheet["I1"] = "Precio"
    sheet["J1"] = "Costo"
    sheet["K1"] = "Hora"
    sheet["L1"] = "Currentlocation"
    sheet["M1"] = "estado_envio"
    sheet["N1"] = ""
    
    
    contador = 1
    sql = f"select H.Fecha, H.Numero_envío,H.Direccion_Completa,H.Localidad,H.Precio,H.Vendedor,V.comprador from historial_estados as H inner join ViajesFlexs as V on V.Numero_envío = H.Numero_envío where vendedor(H.Vendedor) = '{cliente}' and H.Fecha between '{desde}' and '{hasta}' and H.estado_envio in ('En Camino','Levantada') order by Fecha desc"
    cursor.execute(sql)
    sinprecio = 0
    for viajeTupla in cursor.fetchall():
        viaje = list(viajeTupla)
        contador += 1
        fecha = viaje[5]
        nenvio = viaje[1]
        direccionCompleta = viaje[2]
        localidad = viaje[3]
        precio = viaje[4]
        apodo = viaje[5]
        comprador = viaje[6]


        if(precio == None):
            sinprecio = sinprecio +1
            precio = "Sin precio"
        else:
            suma = suma + float(precio)
        sheet["A"+str(contador)] = fecha
        sheet["B"+str(contador)] = nenvio
        sheet["C"+str(contador)] = direccionCompleta
        sheet["D"+str(contador)] = localidad
        sheet["E"+str(contador)] = apodo
        sheet["F"+str(contador)] = precio
        sheet["G"+str(contador)] = comprador
        viajes.append(viaje)
    sheet["F"+str(contador+1)] = "=SUM(F2:F"+str(contador)+")"
    book.save("Resumen.xlsx")
    cabezeras = ["Fecha","Numero de envío","Direccion Completa","Localidad","Vendedor","Precio","Comprador"]
    return render_template("facturacion/tabla_viajes.html",
                            cliente=cliente,
                            desde=desde,
                            hasta=hasta,
                            titulo="Facturacion", 
                            cabezeras = cabezeras,
                            tipo_facturacion="flex", 
                            viajes=viajes, 
                            total=f"${suma} y {sinprecio} viajes sin precio", 
                            clientes = scriptGeneral.consultar_clientes(midb), 
                            auth = session.get("user_auth")
                            )

@fb.route("/facturacion/borrar_repetido")
@auth.login_required
@auth.admin_required
def borrarRepetidos():
    midb = database.connect_db()
    cursor = midb.cursor()
    cursor.execute("select id, Numero_envío, estado_envio from historial_estados where Numero_envío in (select Numero_envío from historial_estados where estado_envio = 'En Camino' group by Numero_envío having count(Numero_envío) >1) and estado_envio = 'En Camino'")
    envios = {}
    for x in cursor.fetchall():
        if x[1] in envios.keys():
            envios[str(x[1])].append(x[2])
        else:
            envios[x[1]] = [x[2]]
    cantidad = 0
    enviosDuplicados = []
    for x in envios:
        if (len(envios[x])) > 1:
            enviosDuplicados.append(x)
            cantidad += 1
    print(f"{cantidad} a revisar antes de facturar")
    borrados = 0
    controlado = 0
    errores = []
    for y in enviosDuplicados:
        controlado += 1
        # midb = database.verificar_conexion(midb)
        sql = f"select id from historial_estados where estado_envio = 'En Camino' and Numero_envío = '{y}'"
        cursor.execute(sql)
        enCaminos = 0
        seGuarda = 99999999999999999999999999999999999999999999999999999999999999999999999
        for x in cursor.fetchall():
            if x[0] < seGuarda:
                seGuarda = x[0]
            else:
                sql = f"DELETE FROM historial_estados WHERE id = '{x[0]}';"
                borrados+=1
                try:
                    cursor.execute(sql)
                    midb.commit()
                except Exception as err:
                    errores.append(err)

    cursor = midb.cursor()
    cursor.execute("select id, Numero_envío, estado_envio from historial_estados where estado_envio = 'Entregado' and Fecha >= '2022-09-01' group By Numero_envío having count(Numero_envío)>1 ")
    envios = {}
    entregadosBorrados = 0
    mayor = 0
    for y in cursor.fetchall():
        cursor.execute(f"select id, Numero_envío, estado_envio from historial_estados where Numero_envío = '{y[1]}'")
        for x in cursor.fetchall():
            if x[0] > mayor:
                sql = f"delete from historial_estados where id = {mayor}"
                entregadosBorrados += 1
                mayor = x[0]
            else:
                sql = f"delete from historial_estados where id = {x[0]}"
                entregadosBorrados += 1
            print(sql)
            print(entregadosBorrados)
            try:
                cursor.execute(sql)
                midb.commit()
            except Exception as err:
                errores.add(err)
    fechaEnvio = []
    agregados = 0
    cursor.execute(f"""select H.Fecha,H.Numero_envío,V.Localidad,V.Vendedor,V.Direccion,V.Precio_Cliente
        from historial_estados as H join ViajesFlexs as V on H.Numero_envío = V.Numero_envío
            where lower(H.estado_envio) in ('entregado','no entregado','listo para salir (sectorizado)') 
            and not H.Numero_envío in 
                (select Numero_envío from historial_estados where estado_envio in ('En Camino') or motivo_noenvio in ('Cancelado'))
                """)
    for x in cursor.fetchall():
        datoEnvio = [x[0],x[1],x[2],x[3],x[4],x[5]]
        fechaEnvio.append(datoEnvio)
    for enCamino in fechaEnvio:
        sql = f"insert into historial_estados (Fecha, Numero_envío,estado_envio,Localidad,Vendedor,Direccion_completa,Precio) values('{enCamino[0]}','{enCamino[1]}','En Camino','{enCamino[2]}','{enCamino[3]}','{enCamino[4]}','{enCamino[5]}');"
        agregados += 1
        cursor = midb.cursor()
        cursor.execute(sql)
        midb.commit()
    cant_err = len(errores)
    if cant_err != 0:
        return f"Se borraron {borrados} En Camino, {entregadosBorrados} Entregados y se agregaron {agregados} En Camino faltantes.\nSe produjeron {cant_err} errores"
    else:
        return f"Se borraron {borrados} En Camino, {entregadosBorrados} Entregados y se agregaron {agregados} En Camino faltantes."