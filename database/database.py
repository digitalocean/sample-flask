import mysql.connector

def connect_db():
    midb = mysql.connector.connect(
    host="141.136.39.86",
    user="mmslogis",
    password="Josu2019",
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