from flask import Blueprint,render_template,redirect, request, session
import requests
import os
from Backend.database.database import connect_db
TN = Blueprint('TN', __name__, url_prefix='/')

@TN.route("/bienvenido")
def vinvulacionTiendaNube():
    data = request.args
    code = data["code"]
    print(data)
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("INSERT INTO `mmslogis_MMSPack`.`testTN`(`test`)VALUES(%s);",(str(data),))
    midb.commit()

    payload = {
        "client_id": "5888",
        "client_secret": os.environ.get("CLIENT_SECRET_TN"),
        "grant_type": "authorization_code",
        "code": code
    }

    response = requests.post("https://www.tiendanube.com/apps/authorize/token", data=payload)

    print(response.text)
    return "Bienvenido a MMSPACK, la vinculacion se realizo correctamente"