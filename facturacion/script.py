from database import database
def consultar_clientes():
    midb = database.connect_db()
    cursor = midb.cursor()
    lista_clientes = []
    cursor.execute("SELECT Cliente FROM mmslogis_MMSPack.`Apodos y Clientes` group by Cliente")
    for cliente in cursor.fetchall():
        Cliente = cliente
        lista_clientes.append(Cliente)
    midb.close()
    return lista_clientes

def quitarAcento(string):
    string = str(string).replace("á","a")
    string = str(string).replace("é","e")
    string = str(string).replace("í","i")
    string = str(string).replace("ó","o")
    string = str(string).replace("ú","u")
    return string