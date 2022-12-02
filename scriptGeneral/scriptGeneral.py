import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def correoChoferes(database):
  correoChoferes = {}
  cursor = database.cursor()
  cursor.execute("select nombre,correo from empleado where fecha_baja is null order by nombre")
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

def enviar_correo(destinos,mensaje_asunto,ruta_adjunto,nombre_adjunto,cuerpo):
    remitente = 'mmspackcheck.informes@gmail.com'
    destinatarios = destinos
    asunto = mensaje_asunto
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))
    if ruta_adjunto != None or nombre_adjunto != None:
        archivo_adjunto = open(f"descargas/"+ruta_adjunto, 'rb')
        adjunto_MIME = MIMEBase('application', 'octet-stream')
        adjunto_MIME.set_payload((archivo_adjunto).read())
        encoders.encode_base64(adjunto_MIME)
        adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % nombre_adjunto)
        mensaje.attach(adjunto_MIME)
    sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    sesion_smtp.starttls()
    sesion_smtp.login('mmspackcheck.informes@gmail.com','vhyrdmvmfpvdgyes')
    texto = mensaje.as_string()
    sesion_smtp.sendmail(remitente, destinatarios, texto)
    sesion_smtp.quit()

enviar_correo(["acciaiomatiassebastian@gmail.com"],"test",None,None,"este es un mensaje de")