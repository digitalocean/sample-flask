from descargaLogixs.downloadSpreedSheets import cargaCamargo,cargaformatoMMS,cargaCamargoMe1
from descargaLogixs.descargaLogixs import descargaLogixs
from database.database import connect_db
from logistica.script import  geolocalizarFaltantes
import pandas as pd
from datetime import datetime
from scriptGeneral.scriptGeneral import enviar_correo


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
    geolocalizarFaltantes(midb)
    midb.close()

def informeQualityShop():
    midb = connect_db()
    fecha = datetime.now()
    pd.read_sql("select Fecha,Numero_envío as Seguimiento,comprador,Direccion,Localidad,estado_envio as Estado,Motivo,Cobrar as Monto from ViajesFlexs where Vendedor = 'Quality Shop' and Fecha = current_date();",midb).to_excel('descargas/informe.xlsx')
    enviar_correo(["qualityshopargentina@gmail.com","josudavidg@gmail.com","acciaiomatiassebastian@gmail.com","mmsjuancarrillo@gmail.com","njb.11@hotmail.com"],f"Informe de envios {fecha.day}-{fecha.month}-{fecha.year} {(fecha.hour)-3}hs","informe.xlsx","informe.xlsx"," ")