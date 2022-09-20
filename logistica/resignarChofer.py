from flask import Blueprint, redirect, render_template, request, session
from auth import auth
from database import database
from datetime import datetime
from .script import correoChoferes
lgRs = Blueprint('reasignarChofer', __name__, url_prefix='/logistica')

@lgRs.route("/reasignar/<nro_envio,chofer>",)
@auth.login_required
def historial(nro_envio,chofer):
    midb = database.connect_db()
    cursor = midb.cursor()
    siEnCamino = []
    # chofer = "Santiago Schefer"
    list_nro_envio = ["4141410483","41640122159","41641142769","41641381896","41642042909"]
    cursor.execute(f"select Numero_envío from historial_estados where Numero_envío in {tuple(list_nro_envio)} and estado_envio = 'En Camino'")
    for x in cursor.fetchall():
        siEnCamino.append(x[0])
    for nro_envio in list_nro_envio:
        if nro_envio in siEnCamino:
            sql = f"update ViajesFlexs set `Check` = 'En Camino', Chofer = {chofer},estado_envio = 'En Camino', Ultimo_motivo = 'En Camino' where Numero_envío = '{nro_envio}'" 
            print (sql)
        else:
            print(x)
# cursor.execute()
