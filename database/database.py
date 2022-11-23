import mysql.connector

def connect_db():
    midb = mysql.connector.connect(
    # host="141.136.39.86",
    host = "109.106.251.113",
    user="mmslogis_GS",
    password="12345",
    database="mmslogis_MMSPack"
    )
    return midb

def verificar_conexion(midb):
    if midb.is_connected() == False:
        print("Reconectando base de datos")
    while midb.is_connected() == False:
        try:
            midb = connect_db()
            print("Conexion exitosa")
        except:
            print("Error en la coneccion")
    return midb