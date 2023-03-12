from flask import Blueprint,render_template,redirect, request, session
from database.database import connect_db
TN = Blueprint('TN', __name__, url_prefix='/')

@TN.route("/bienvenido")
def vinvulacionTiendaNube():
    data = request.args
    print(data)
    midb = connect_db()
    cursor = midb.cursor()
    cursor.execute("INSERT INTO `mmslogis_MMSPack`.`testTN`(`test`)VALUES(%s);",(data,))
    midb.commit()
    return 
