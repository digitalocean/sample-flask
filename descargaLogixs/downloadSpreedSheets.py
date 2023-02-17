import gspread
from datetime import datetime
from logistica.Envio import Envio
from database.database import connect_db

def cargaCamargo(nrosEnvios):
    sa = gspread.service_account(filename="silken-tenure-292020-e0dbd484ad63.json")
    sh = sa.open("Flex (MMS) Febrero")
    wks = sh.worksheet("Hoy")
    envios = wks.get(f"A2:I{wks.row_count}")
    for x in envios:
        if len(x) > 7 and x[1] in nrosEnvios.keys():
            continue
        elif len(x) > 4 and (x[1] != "" and x[3] != "" and x[4] != ""):
            viaje = Envio(x[3],x[4],"AJAXGOLD",x[1],x[2],referencia=x[6],recibeOtro=x[7],tipoEnvio=2)
            if viaje.toDB():
                print(f"{viaje.Numero_envío} agregado de {viaje.Vendedor}")
            else:
                print(f"algo fallo con {x}")
        else:
            print(f"error en {x}")

def cargaCamargoMe1(nrosEnvios):
    sa = gspread.service_account(filename="silken-tenure-292020-e0dbd484ad63.json")
    sh = sa.open("Flex (MMS) Febrero")
    wks = sh.worksheet("Me1")
    envios = wks.get(f"A2:I{wks.row_count}")
    for x in envios:
        if len(x) > 7 and x[1] in nrosEnvios.keys():
            continue
        elif len(x) > 14 and (x[1] != "" and x[4] != "" and x[5] != ""):
            viaje = Envio(x[3],x[4],"AJAXGOLD",x[1],x[2],referencia=x[6],recibeOtro=x[7],tipoEnvio=2,sku=x[11])
            print(x[7],x[8])
            if viaje.toDB():
                print(f"{viaje.Numero_envío} agregado de {viaje.Vendedor}")
            else:
                print(f"algo fallo con {x}")
        elif len(x) > 7 and (x[1] != "" and x[4] != "" and x[5] != ""):
            viaje = Envio(x[3],x[4],"AJAXGOLD",x[1],x[2],referencia=x[6],recibeOtro=x[7],tipoEnvio=2)
            print(x[7],x[8])
            if viaje.toDB():
                print(f"{viaje.Numero_envío} agregado de {viaje.Vendedor}")
            else:
                print(f"algo fallo con {x}")
        else:
            print(f"error en {x}")

def cargaformatoMMS(nrosEnvios,planilla,hoja,vendedor=None):
    sa = gspread.service_account(filename="silken-tenure-292020-e0dbd484ad63.json")
    sh = sa.open(planilla)
    wks = sh.worksheet(hoja)
    envios = wks.get(f"A6204:i{wks.row_count}") 
    for x in envios:
        if len(x) > 7 and x[1] in nrosEnvios.keys():
            continue
        elif len(x) > 7 and x[1] != "" and x[5] != "" and x[7] != "":
            cp = None
            if len(x) > 8:
                cp = x[8]
            viaje = Envio(x[5],x[7],vendedor,x[1],x[3],x[4],x[6],cp,tipoEnvio=2)
            if viaje.toDB():
                print(f"{viaje.Numero_envío} agregado de {viaje.Vendedor}")
            else:
                print(f"algo fallo con {x}")
        else:
            print(f"error en {x}")


def cargaRobotin(nrosEnvios):
    sa = gspread.service_account(filename="silken-tenure-292020-e0dbd484ad63.json")
    sh = sa.open("Cargas de Robotin")
    wks = sh.worksheet("Como Ruteo de Primera")
    envios = wks.get(f"B2:V{wks.row_count}") 
    for x in envios:
        if len(x) > 7 and x[1] in nrosEnvios.keys():
            continue
        elif len(x) > 7 and x[1] != "" and x[5] != "" and x[7] != "":
            cp = None
            if len(x) > 8:
                cp = x[8]
            viaje = Envio(x[5],x[7],x[10],x[1],x[2],referencia=x[6],valorDeclarado=x[20],cp=cp,tipoEnvio=2)
            if viaje.toDB():
                print(f"{viaje.Numero_envío} agregado de {viaje.Vendedor}")
            else:
                print(f"algo fallo con {x}")
        else:
            print(f"error en {x}")