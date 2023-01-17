from descargaLogixs.downloadSpreedSheets import cargaCamargo,cargaformatoMMS,cargaCamargoMe1,cargaRobotin
from descargaLogixs.descargaLogixs import descargaLogixs
from database.database import connect_db
from logistica.script import  geolocalizarFaltantes
import pandas as pd
from datetime import datetime
from scriptGeneral.scriptGeneral import enviar_correo
import pandas as pd

def generarInforme(midb,ruta,vendedor):
    pd.read_sql(f"select Fecha,Numero_envío,comprador,Telefono,Direccion,Localidad,Referencia,Vendedor,estado_envio,sku,Cobrar from ViajesFlexs where Vendedor = '{vendedor}' and estado_envio = 'Lista Para Retirar';",midb).to_excel(ruta)
    enviar_correo(["njb.11@hotmail.com","mmsmatiasacciaio@gmail.com","mmsjuancarrillo@gmail.com"],f"Envios cargados {vendedor} {datetime.now()}" ,ruta,"Informe.xlsx","")

def descargaDesdePlanillas():
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select Numero_envío,estado_envio from ViajesFlexs")
    nrosEnvios = {}
    for env in cursor.fetchall():
        nrosEnvios[env[0]] = env[1]
    descargaLogixs(midb,nrosEnvios)
    cargaCamargo(nrosEnvios)
    cargaCamargoMe1(nrosEnvios)
    cargaformatoMMS(nrosEnvios,"Lapiz y Papel Libreria Flex","Viajes","Lapiz y Papel")
    cargaRobotin(nrosEnvios)
    geolocalizarFaltantes(midb)

def informeEstados(vendedor):
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("select correo_electronico from Clientes where nombre_cliente = %s",(vendedor,))
    correoVendedor = cursor.fetchone()[0]
    print(correoVendedor)
    fecha = datetime.now()
    pd.read_sql(f"select Fecha,Numero_envío as Seguimiento,comprador,Direccion,Localidad,estado_envio as Estado,Motivo,Cobrar as Monto from ViajesFlexs where Vendedor = '{vendedor}' and Timechangestamp >= current_date();",midb).to_excel('descargas/informe.xlsx')
    enviar_correo([correoVendedor,"josudavidg@gmail.com","mmsmatiasacciaio@gmail.com","mmsjuancarrillo@gmail.com","njb.11@hotmail.com"],f"Informe de envios {vendedor} {fecha.day}-{fecha.month}-{fecha.year} {(fecha.hour)-3}hs","descargas/informe.xlsx","informe.xlsx"," ")


def informeFinalDia():
    midb = connect_db()
    sql = """
        select ifnull(Chofer,"Sin Chofer") as Chofer,

        count(CASE WHEN estado_envio = 'En Camino' THEN 1 END)  as En_camino_hoy,

        count(CASE WHEN estado_envio = 'Reasignado' THEN 1 END)  as Reasignados_hoy,

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
    pd.read_sql(sql,midb).to_excel('descargas/informe.xlsx')
    midb.close()
    enviar_correo(["mmsmatiasacciaio@gmail.com","mmssoniamariel@gmail.com"],f"Informe final del dia","descargas/informe.xlsx","informe.xlsx"," ")