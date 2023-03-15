
from flask import (
    Blueprint, g, render_template, request, session,send_file,make_response
)
from datetime import datetime,timedelta
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import PatternFill, Font
import io
import xlsxwriter
from Backend.auth import auth
from .estrategiaDeFacturacion import *
from Backend.database.database import connect_db
from Backend.scriptGeneral import scriptGeneral

FcGeneral = Blueprint('facturacionGeneral', __name__, url_prefix='/')

class EnvioAFacturar():
    def __init__(self,id,fecha,nEnvio,direccionCompleta,localidad,precio,comprador,cobrar,estado,motivo,estadoActual):
        self.id = id
        self.Fecha = fecha
        self.Numero_envío = nEnvio
        self.Direccion = direccionCompleta
        self.Localidad = localidad
        self.Precio_Cliente = precio
        self.comprador = comprador
        self.Cobrar = cobrar
        self.estado_envio = estado
        self.motivo = motivo
        self.estadoActual = estadoActual

class Facturador:
    def __init__(self, strategy):
        self.strategy = strategy
        
    def facturar_viajes(self, viajes,sobreEscribir):
        return self.strategy.facturar_viajes(viajes,sobreEscribir)

def generarExcelLiquidacion(envios,_desde,_hasta,_cliente,ruta_archivo):
    viajes = []
    book = Workbook()
    sheet = book.active
    image = Image("static/logo_grande.jpeg")
    sheet.add_image(image, 'A1')
    sheet.column_dimensions['A'].width = 20
    sheet.column_dimensions['B'].width = 20
    sheet.column_dimensions['C'].width = 30
    sheet.column_dimensions['D'].width = 65
    sheet.column_dimensions['E'].width = 20
    sheet.column_dimensions['F'].width = 15
    sheet["A9"] = "Fecha"
    sheet["B9"] = "Numero de envío"
    sheet["C9"] = "Comprador"
    sheet["D9"] = "Direccion_Completa"
    sheet["E9"] = "Localidad"
    sheet["F9"] = "Precio"
    sheet["G9"] = "Monto a cobrar"
    sheet["H9"] = "Estado"
    sheet["E3"] = _desde
    sheet["E4"] = _hasta
    for row in sheet['A9:H9']:
        for cell in row:
            cell.fill = PatternFill(fgColor='FF0000', fill_type='solid')
            cell.font = Font(color='FFFFFF')
    suma = 0
    contador = 9
    sinprecio = 0
    for viajeTupla in envios:
        viaje = list(viajeTupla)
        contador += 1
        fecha = viaje[0]
        nenvio = viaje[1]
        direccionCompleta = viaje[2]
        localidad = viaje[3]
        precio = viaje[4]
        comprador = viaje[5]
        cobrar = viaje[6]
        estado = viaje[7]
        if viaje[7] != "Entregado":
            viaje[6] = "0"
        if(precio == None):
            sinprecio = sinprecio +1
            precio = "Sin precio"
        else:
            suma = suma + float(precio)
        sheet["A"+str(contador)] = fecha
        sheet["B"+str(contador)] = nenvio
        sheet["C"+str(contador)] = comprador
        sheet["D"+str(contador)] = direccionCompleta
        sheet["E"+str(contador)] = localidad
        sheet["F"+str(contador)] = precio
        if estado == "Entregado":
            sheet["G"+str(contador)] = cobrar
        else:
            sheet["G"+str(contador)] = "0"
        sheet["H"+str(contador)] = estado
        viajes.append(viaje)
    sheet["E1"] = _cliente
    sheet["E2"] = f"cantidad: {contador-9}"
    sheet["E3"] = "Subtotal: "
    sheet["E4"] = "IVA: "
    sheet["F6"] = "Total: "
    sheet["F3"] = "=SUM(F10:F"+str(contador)+")"
    sheet["F4"] = "=F3 * 0.21"
    sheet["F6"] = "=SUM(E3:E4)"
    book.save(ruta_archivo)
    return ruta_archivo

def generarExcel(envios):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    for i,viajeTupla in enumerate(envios):
        for j, value in enumerate(viajeTupla):
            worksheet.write(i, j, value)
    workbook.close()
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=datos.xlsx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

@FcGeneral.route("/facturacion/facturar",methods = ["GET","POST"])
@auth.login_required
def facturar():
    if request.method == "POST":
        cliente = request.form.get("cliente")
        desde = request.form.get("desde")
        hasta = request.form.get("hasta")
        sobreEscribir = request.form.get("sobreEscribir")
        if sobreEscribir == "True":
            sobreEscribir = True
        else:
            sobreEscribir = False
        estrategiaDeFacturacion = request.form.get("estrategiaFacturacion")
        sql = f"""select 
            H.id,
            H.Fecha, 
            H.Numero_envío,
            H.Direccion_Completa,
            H.Localidad,
            H.Precio,
            V.comprador,
            V.Cobrar,
            H.estado_envio,
            H.motivo_noenvio,
            V.estado_envio as estadoActual
        from 
            historial_estados as H 
        inner join 
            ViajesFlexs as V 
        on 
            V.Numero_envío = H.Numero_envío 
        where 
            vendedor(H.Vendedor) = '{cliente}' and H.Fecha between '{desde}' and '{hasta}';"""
        midb = connect_db()
        cursor = midb.cursor()
        cursor.execute(sql)
        viajes = []
        for x in cursor.fetchall():
            viajes.append(EnvioAFacturar(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10]))
        estrategia = EnCaminoStrategy()
        if estrategiaDeFacturacion == "strategyEnCamino":
            estrategia = EnCaminoStrategy()
        elif estrategiaDeFacturacion == "strategyPorDireccion":
            estrategia = EnCaminoUnicoStrategy()
        elif estrategiaDeFacturacion == "strategyEntregado":
            estrategia = EntregadoStrategy()      
        elif estrategiaDeFacturacion == "strategyPorVisita":
            estrategia = PorVisitaStrategy()    
        facturador = Facturador(estrategia)
        total_viajes,viajesEnCamino = facturador.facturar_viajes(viajes,sobreEscribir)
        cabeceras = ["Fecha","Numero de envío","Direccion Completa","Localidad","Precio","Comprador"]
        ruta = generarExcelLiquidacion(viajesEnCamino,desde,hasta,cliente,"Liquidacion.xlsx")
        return render_template("facturacion/tabla_viajes.html",
                            cliente=cliente,
                            desde=desde,
                            hasta=hasta,
                            titulo="Facturacion", 
                            cabeceras = cabeceras,
                            tipo_facturacion="flex", 
                            viajes=viajesEnCamino, 
                            ruta_archivo = ruta,
                            total=f"${total_viajes} y {0} viajes sin precio", 
                            clientes = scriptGeneral.consultar_clientes(midb), 
                            auth = session.get("user_auth")
                            )
    else:
        return render_template("facturacion/tabla_viajes.html",
                            titulo="Facturacion", 
                            desde=str(datetime.now()-timedelta(days=15))[0:10],
                            hasta=str(datetime.now())[0:10],
                            clientes=scriptGeneral.consultar_clientes(connect_db()), 
                            tipo_facturacion="flex", 
                            auth = session.get("user_auth"))
