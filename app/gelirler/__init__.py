from flask import Blueprint, render_template

bp = Blueprint('gelirler', __name__)

@bp.route('/')
def liste():
    return render_template('gelirler/liste.html')

@bp.route('/ekle')
def ekle():
    return render_template('gelirler/form.html')

@bp.route('/duzenle/<id>')
def duzenle(id):
    return render_template('gelirler/form.html', id=id)

