import mysql.connector
import os
def connect_db():
    midb = mysql.connector.connect(
    host = os.environ.get("FLASK_DATABASE_HOST"),
    user=os.environ.get("FLASK_DATABASE_USER"),
    password=os.environ.get("FLASK_DATABASE_PASSWORD"),
    database=os.environ.get("FLASK_DATABASE")
    )
    return midb


def connect_db_ML():
    midb = mysql.connector.connect(
    host = os.environ.get("FLASK_DATABASE_HOST"),
    user=os.environ.get("FLASK_DATABASE_USER_ML"),
    password=os.environ.get("FLASK_DATABASE_PASSWORD_ML"),
    database=os.environ.get("FLASK_DATABASE")
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