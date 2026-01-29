# Gelişim - Aylık / yıllık gelir, gider, net kâr (Chart.js ile client-side sütun grafikleri)
from flask import Blueprint, render_template

bp = Blueprint('gelisim', __name__, url_prefix='/gelisim')


@bp.route('/')
def index():
    return render_template('gelisim/index.html')
