from flask import flask, Blueprint,send_file,request
import uuid


from ftplib import FTP
ftp = Blueprint('cliente', __name__, url_prefix='/')

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower() # obtener la extensión del archivo original
    unique_filename = str(uuid.uuid4()) + '.' + ext
    return unique_filename

def upload(patch,nombreArchivo,file):
    file = request.files['file']
    filename = file.filename
    unique_filename = generate_unique_filename(filename) # función que genera un nombre de archivo único
    file.save(unique_filename)
    
    ftp = FTP('ftp.example.com') # dirección del servidor FTP
    ftp.login(user='username', passwd='password') # credenciales de acceso al servidor FTP
    ftp.cwd('/upload_directory') # directorio de destino en el servidor FTP
    with open(unique_filename, 'rb') as f:
        ftp.storbinary('STOR ' + unique_filename, f)
    ftp.quit()
    
    return 'Archivo cargado con éxito'


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