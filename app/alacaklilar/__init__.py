from flask import Blueprint, render_template

bp = Blueprint('alacaklilar', __name__)

@bp.route('/')
def liste():
    return render_template('alacaklilar/liste.html')

@bp.route('/ekle')
def ekle():
    return render_template('alacaklilar/form.html')

@bp.route('/duzenle/<id>')
def duzenle(id):
    return render_template('alacaklilar/form.html', id=id)

@bp.route('/odeme/<id>')
def odeme(id):
    return render_template('alacaklilar/odeme.html', id=id)

@bp.route('/borcu-bitenler')
def borcu_bitenler():
    return render_template('alacaklilar/borcu_bitenler.html')

