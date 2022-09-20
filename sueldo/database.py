import mysql.connector

def connect_db():
    conn = mysql.connector.connect(
        host='141.136.39.86',
        user='mmslogis_GS',
        passwd='12345',
        db='mmslogis_MMSPack'
        )
    return conn

def verificar_conexion(midb):
    if midb.is_connected() == False:
        print("Reconectando base de datos")
    while midb.is_connected() == False:
        try:
            midb = connect_db()
            conexion = midb.is_connected()
            if conexion == True:
                print("Conexion exitosa")
        except:
            print("Error en la conexion")
    return midb