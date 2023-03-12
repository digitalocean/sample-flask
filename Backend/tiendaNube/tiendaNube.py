from flask import Blueprint,render_template,redirect, request, session
import requests
import json
import os
from Backend.database.database import connect_db
TN = Blueprint('TN', __name__, url_prefix='/')

@TN.route("/bienvenido")
def vinvulacionTiendaNube():
    data = request.args
    code = data["code"]
    print(data)
    

    payload = {
        "client_id": os.environ.get("APP_ID_TN"),
        "client_secret": os.environ.get("CLIENT_SECRET_TN"),
        "grant_type": "authorization_code",
        "code": code
    }

    response = requests.post("https://www.tiendanube.com/apps/authorize/token", data=payload)
    json_data = json.loads(response.text)
    access_token = json_data["access_token"]
    token_type = json_data["token_type"]
    scope = json_data["scope"]
    user_id = json_data["user_id"]
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("""
                    INSERT INTO `mmslogis_MMSPack`.`vinculacion_tn`
                        (`access_token`,
                        `token_type`,
                        `scope`,
                        `user_id`)
                        VALUES
                        (%s,%s,%s,%s);""",(access_token,token_type,scope,user_id))
    midb.commit()
    return "Bienvenido a MMSPACK, la vinculacion se realizo correctamente"