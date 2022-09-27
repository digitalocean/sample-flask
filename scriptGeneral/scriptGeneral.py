def correoChoferes(database):
  correoChoferes = {}
  cursor = database.cursor()
  cursor.execute("select nombre,correo from empleado where fecha_baja is null")
  for x in cursor.fetchall():
      if not x[0] in correoChoferes.keys():
          correoChoferes[x[0]] = x[1]
  return correoChoferes


def consultar_clientes(database):
    cursor = database.cursor()
    lista_clientes = []
    cursor.execute("SELECT Cliente FROM mmslogis_MMSPack.`Apodos y Clientes` group by Cliente")
    for cliente in cursor.fetchall():
        Cliente = cliente
        lista_clientes.append(Cliente[0])
    return lista_clientes

def quitarAcento(string):
    string = str(string).replace("á","a")
    string = str(string).replace("é","e")
    string = str(string).replace("í","i")
    string = str(string).replace("ó","o")
    string = str(string).replace("ú","u")
    return string