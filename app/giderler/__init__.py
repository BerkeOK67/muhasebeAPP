from flask import Blueprint, render_template

bp = Blueprint('giderler', __name__)

@bp.route('/')
def liste():
    return render_template('giderler/liste.html')

@bp.route('/ekle')
def ekle():
    return render_template('giderler/form.html')

@bp.route('/duzenle/<id>')
def duzenle(id):
    return render_template('giderler/form.html', id=id)

