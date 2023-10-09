from flask import Blueprint
from flask import render_template


bp = Blueprint('magazines', __name__, url_prefix='/magazines')


@bp.route('/', methods=('GET', 'POST'))
def index():

    return render_template('magazines/index.html')
