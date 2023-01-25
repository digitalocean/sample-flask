from descargaLogixs.downloadSpreedSheets import cargaCamargo,cargaformatoMMS,cargaCamargoMe1,cargaRobotin
from descargaLogixs.descargaLogixs import descargaLogixs
from database.database import connect_db
from logistica.script import  geolocalizarFaltantes
from scriptGeneral.scriptGeneral import enviar_correo
import pandas as pd
import openpyxl
from datetime import datetime


def generarInforme(midb,ruta,vendedor):
    pd.read_sql(f"select Fecha,Numero_envío,comprador,Telefono,Direccion,Localidad,Referencia,Vendedor,estado_envio,sku,Cobrar from ViajesFlexs where Vendedor = '{vendedor}' and estado_envio = 'Lista Para Retirar';",midb).to_excel(ruta)
    enviar_correo(["njb.11@hotmail.com","mmsmatiasacciaio@gmail.com","mmsjuancarrillo@gmail.com"],f"carga de envios de {vendedor} {datetime.now()}" ,ruta,"Informe.xlsx","")

def descargaDesdePlanillas():
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select Numero_envío,estado_envio from ViajesFlexs")
    nrosEnvios = {}
    for env in cursor.fetchall():
        nrosEnvios[env[0]] = env[1]
    try:
        descargaLogixs(midb,nrosEnvios)
    except Exception as e:
        enviar_correo(["mmsmatiasacciaio@gmail.com","acciaiomatiassebastian@gmail.com"],"Error del sistema (Descarga Logixs)","","",e)
    try:
        cargaCamargo(nrosEnvios)
    except Exception as e:
        enviar_correo(["mmsmatiasacciaio@gmail.com","acciaiomatiassebastian@gmail.com"],"Error del sistema (Carga Camargo(HOY))","","",e)
    try:
        cargaCamargoMe1(nrosEnvios)
    except Exception as e:
        enviar_correo(["mmsmatiasacciaio@gmail.com","acciaiomatiassebastian@gmail.com"],"Error del sistema (Carga Camargo ME1)","","",e)
    try:
        cargaformatoMMS(nrosEnvios,"Lapiz y Papel Libreria Flex","Viajes","Lapiz y Papel")
    except Exception as e:
        enviar_correo(["mmsmatiasacciaio@gmail.com","acciaiomatiassebastian@gmail.com"],"Error del sistema (Carga Lapiz y Papel)","","",e)
    try:
        cargaRobotin(nrosEnvios)
    except Exception as e:
        enviar_correo(["mmsmatiasacciaio@gmail.com","acciaiomatiassebastian@gmail.com"],"Error del sistema (Carga Robotin)","","",e)
    try:
        geolocalizarFaltantes(midb)
    except Exception as e:
        enviar_correo(["mmsmatiasacciaio@gmail.com","acciaiomatiassebastian@gmail.com"],"Error del sistema (Geolocalizacion)","","",e)

def informeEstados(vendedor):
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select correo_electronico from Clientes where nombre_cliente = %s",(vendedor,))
    correoVendedor = cursor.fetchone()[0]
    print(correoVendedor)
    fecha = datetime.now()
    pd.read_sql(f"select Fecha,Numero_envío as Seguimiento,comprador,Direccion,Localidad,estado_envio as Estado,Motivo,Cobrar as Monto from ViajesFlexs where Vendedor = '{vendedor}' and Fecha = current_date() and estado_envio != 'Lista Para Retirar';",midb).to_excel('descargas/informe.xlsx')
    enviar_correo([correoVendedor,"josudavidg@gmail.com","mmsmatiasacciaio@gmail.com","mmsjuancarrillo@gmail.com","njb.11@hotmail.com"],f"Informe de envios {vendedor} {fecha.day}-{fecha.month}-{fecha.year} {(fecha.hour)-3}hs","descargas/informe.xlsx","informe.xlsx"," ")


def informeFinalDia():
    midb = connect_db()
    sql = """
        select ifnull(Chofer,"Sin Chofer") as Chofer,

        count(CASE WHEN estado_envio = 'En Camino' THEN 1 END)  as En_camino,

        count(CASE WHEN estado_envio = 'Reasignado' THEN 1 END)  as Reasignados,

        count(CASE when estado_envio in ("Entregado") then 1 end) as Entregados,

        count(CASE when motivo_noenvio = "Nadie en Domicilio (Reprogramado)" then 1 end) as Nadie_en_domicilio,

        count(case when motivo_noenvio = "Domicilio no visitado" then 1 end) as No_visitado,
        
        ABS(count(CASE WHEN estado_envio in ('En Camino','Reasignado') THEN 1 END)-
        count(CASE when estado_envio in ("Entregado") then 1 end)-
        count(CASE when motivo_noenvio = "Nadie en Domicilio (Reprogramado)" then 1 end)-
        count(case when motivo_noenvio = "Domicilio no visitado" then 1 end)) as Diferencia_cargados_Entregados,

        (select Hora from historial_estados as H2 where estado_envio in ("En Camino","Reasignado") 
        and Fecha = current_date()-1 and H1.Chofer = H2.Chofer order by Hora desc limit 1) as Horario_salida,

        (select Hora from historial_estados as H2 where Fecha = current_date()-1 and 
        H1.Chofer = H2.Chofer order by Hora desc limit 1) as Horario_fin,

        concat(((100 / COUNT(CASE WHEN estado_envio IN ('En Camino','Reasignado') THEN 1 END)  * 
        COUNT(CASE WHEN estado_envio IN ("Entregado") THEN 1 END) )),"%") as efectividad

        from historial_estados as H1 where Fecha = current_date()-1 and estado_envio != "Lista Para Devolver" group by Chofer;"""
    df = pd.read_sql(sql,midb)
    horaSalida = "Horario_salida"
    horaFin = "Horario_fin"
    df[horaSalida] = df[horaSalida].astype(str)
    df[horaSalida] = [i.split(" ")[-1] for i in df[horaSalida]]
    df[horaFin] = df[horaFin].astype(str)
    df[horaFin] = [i.split(" ")[-1] for i in df[horaFin]]

    book = openpyxl.Workbook()
    writer = pd.ExcelWriter('descargas/informeFinalDia.xlsx', engine='openpyxl')
    
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    worksheet = writer.book['Sheet1']
    worksheet.column_dimensions['A'].width = 20
    worksheet.column_dimensions['B'].width = 20
    worksheet.column_dimensions['C'].width = 20
    worksheet.column_dimensions['D'].width = 20
    worksheet.column_dimensions['E'].width = 20
    worksheet.column_dimensions['F'].width = 20
    worksheet.column_dimensions['G'].width = 35
    worksheet.column_dimensions['H'].width = 20
    worksheet.column_dimensions['I'].width = 20
    worksheet.column_dimensions['J'].width = 20
    worksheet.column_dimensions['K'].width = 20
    writer.save()
    midb.close()
    enviar_correo(["mmsmatiasacciaio@gmail.com","mmssoniamariel@gmail.com","njb.11@hotmail.com","josudavidg@gmail.com"],f"final del dia","descargas/informeFinalDia.xlsx","informe.xlsx"," ")