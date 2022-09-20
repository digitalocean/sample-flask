from auth import auth
from flask import (
    Blueprint, render_template, session
)
fcBienvenida = Blueprint('fc_barracas', __name__, url_prefix='/')

@fcBienvenida.route("/facturacion")
@auth.login_required
def facturacion():
    return render_template ("facturacion.html", titulo="Bienvenido", auth = session.get("user_auth"), usuario = session.get("user_id"))
