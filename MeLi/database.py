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
