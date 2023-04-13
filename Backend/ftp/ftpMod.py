from flask import Blueprint,send_file,request
from io import BytesIO
import uuid
import os


from ftplib import FTP
ftpMod = Blueprint('ftpFlask', __name__, url_prefix='/')

def generate_unique_filename(filename):
    if "." in filename:
        ext = filename.rsplit('.', 1)[1].lower() # obtener la extensión del archivo original
        unique_filename = str(uuid.uuid4()) + '.' + ext
        return unique_filename
    else:
        return "NoFile"
    # filename = str(uuid.uuid4())
    # return filename + ".pdf"

def upload(patch,file,filename):
    # unique_filename = str(uuid.uuid4()) + ".pdf"
    unique_filename = generate_unique_filename(filename)
    if unique_filename != "NoFile":
        ftp_server = os.environ.get("FTP_SERVER")
        ftp_user = os.environ.get("FTP_USER")
        ftp_password = os.environ.get("FTP_PASSWORD") 
        ftp = FTP(ftp_server )
        ftp.login(user=ftp_user, passwd=ftp_password)
        ftp.cwd(patch) # directorio de destino en el servidor FTP
        with BytesIO(file) as f:
            ftp.storbinary('STOR ' + unique_filename, f)
        ftp.quit()
    return unique_filename

@ftpMod.route('/archivoftp/<path>/<filename>')
def lecturaFtp(path, filename):
    server = os.environ.get("FTP_SERVER")
    user = os.environ.get("FTP_USER")
    passw = os.environ.get("FTP_PASSWORD")
    ftp = FTP(server)
    ftp.login(user=user, passwd=passw)
    filedata = BytesIO()
    ftp.retrbinary(f"RETR {path}/{filename}", filedata.write)
    ftp.quit()
    filedata.seek(0)
    return send_file(filedata, attachment_filename=filename)
