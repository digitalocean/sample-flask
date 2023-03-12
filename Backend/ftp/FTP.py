from flask import flask, Blueprint,send_file


from ftplib import FTP
ftp = Blueprint('cliente', __name__, url_prefix='/')

def upload(patch,nombreArchivo,file):
    # Conexión FTP
    ftp = FTP('ftp.servidor.com')
    ftp.login('usuario', 'contraseña')

    # Carga del archivo
    ftp.cwd(patch)
    ftp.storbinary('STOR {}.pdf'.format(nombreArchivo), file)

    # Cierre de la conexión FTP
    ftp.quit()

    return 'Archivos cargados exitosamente'


# LECTURA DE HOSTINGER FTP
@ftp.route('/imageFTP/<filename>')
def imageFTP(filename):
    # filename = "Screenshot_1673795214.png"
    ftp = FTP('109.106.251.113')
    ftp.login(user='appChofer@mmslogistica.com', passwd='(15042020)_')
    ftp.cwd('/foto_domicilio/')
    # public_html/foto_domicilio/Screenshot_1673795214.png
    image = ftp.retrbinary('RETR ' + filename, open('image.png', 'wb').write)
    ftp.quit()
    return send_file("image.png")