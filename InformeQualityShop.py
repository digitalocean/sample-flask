from database.database import connect_db
import pandas as pd
def escribir_informe():
    midb = connect_db()
    pd.read_sql("select Fecha,Numero_envío,comprador,Direccion,Localidad,estado_envio,Motivo from ViajesFlexs where Vendedor = 'Quality Shop' and Fecha = current_date();",midb).to_excel('descargas/informe.xlsx')

from scriptGeneral.scriptGeneral import enviar_correo
escribir_informe()
enviar_correo(["acciaiomatiassebastian@gmail.com"],"Informe","informe.xlsx","informe.xlsx"," ")