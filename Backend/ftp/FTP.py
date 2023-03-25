from flask import Blueprint,send_file,request
from io import BytesIO
import uuid
import mimetypes


from ftplib import FTP
ftp = Blueprint('ftpFlask', __name__, url_prefix='/')

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower() # obtener la extensión del archivo original
    unique_filename = str(uuid.uuid4()) + '.' + ext
    return unique_filename
    # filename = str(uuid.uuid4())
    # return filename + ".pdf"

def upload(patch,file,filename):
    # unique_filename = str(uuid.uuid4()) + ".pdf"
    unique_filename = generate_unique_filename(filename)
    ftp = FTP('109.106.251.113')
    ftp.login(user='appChofer@mmslogistica.com', passwd='(15042020)_')
    ftp.cwd(patch) # directorio de destino en el servidor FTP
    with BytesIO(file) as f:
        ftp.storbinary('STOR ' + unique_filename, f)
    ftp.quit()
    return unique_filename


# LECTURA DE HOSTINGER FTP
@ftp.route('/archivoftp/<patch>/<filename>')
def imageFTP(patch,filename):
    # filename = "Screenshot_1673795214.png"
    ftp = FTP('109.106.251.113')
    ftp.login(user='appChofer@mmslogistica.com', passwd='(15042020)_')
    ftp.cwd('/foto_domicilio/')
    # public_html/foto_domicilio/Screenshot_1673795214.png
    image = ftp.retrbinary(f'RETR /{patch}/{filename}', open(filename, 'wb').write)
    ftp.quit()
    return send_file(filename)