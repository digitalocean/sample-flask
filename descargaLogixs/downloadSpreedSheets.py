import gspread
from datetime import datetime
from logistica.Envio import Envio
from database.database import connect_db

def cargaCamargo(nrosEnvios):
    sa = gspread.service_account(filename="silken-tenure-292020-e0dbd484ad63.json")
    sh = sa.open("Flex (MMS) Diciembre")
    wks = sh.worksheet("Hoy")
    envios = wks.get(f"A2:I{wks.row_count}")
    for x in envios:
        if len(x) > 1 and x[1] in nrosEnvios.keys():
            continue
        elif len(x) > 1 and (x[1] != "" and x[3] != "" and x[4] != ""):
            day = int(x[0][0:2])
            month = int(x[0][3:5])
            year = int(x[0][6:10])
            viaje = Envio(x[3],x[4],"AJAXGOLD",x[1],x[2],referencia=x[6],recibeOtro=x[7],tipoEnvio=2)
            if viaje.toDB():
                print(f"{viaje.Numero_envío} agregado de {viaje.Vendedor}")
            else:
                print("algo fallo")
        else:
            print(f"error en {x}")

def cargaCamargoMe1(nrosEnvios):
    sa = gspread.service_account(filename="silken-tenure-292020-e0dbd484ad63.json")
    sh = sa.open("Flex (MMS) Diciembre")
    wks = sh.worksheet("Me1")
    envios = wks.get(f"A2:I{wks.row_count}")
    for x in envios:
        if len(x) > 1 and x[1] in nrosEnvios.keys():
            continue
        elif len(x) > 1 and (x[1] != "" and x[4] != "" and x[5] != ""):
            day = int(x[0][0:2])
            month = int(x[0][3:5])
            year = int(x[0][6:10])
            viaje = Envio(x[4],x[5],"AJAXGOLD",x[1],x[3],referencia=x[7],recibeOtro=x[8],tipoEnvio=2)
            print(x[7],x[8])
            if viaje.toDB():
                print(f"{viaje.Numero_envío} agregado de {viaje.Vendedor}")
            else:
                print("algo fallo")
        else:
            print(f"error en {x}")

def cargaformatoMMS(nrosEnvios):
    sa = gspread.service_account(filename="silken-tenure-292020-e0dbd484ad63.json")
    sh = sa.open("Lapiz y Papel Libreria Flex")
    wks = sh.worksheet("Viajes")
    envios = wks.get(f"A6204:k{wks.row_count}")
    for x in envios:
        if len(x) > 1 and x[1] in nrosEnvios.keys():
            continue
        elif len(x) > 1 and x[1] != "" and x[5] != "" and x[7] != "" and x[10] != "":
            day = int(x[0][0:2])
            month = int(x[0][3:5])
            year = int(x[0][6:10])
            viaje = Envio(x[5],x[7],"Lapiz y Papel",x[1],x[3],x[4],x[6],x[8],datetime(year,month,day),tipoEnvio=2)
            if viaje.toDB():
                print(f"{viaje.Numero_envío} agregado de {viaje.Vendedor}")
            else:
                print("algo fallo")
        else:
            print(f"error en {x}")