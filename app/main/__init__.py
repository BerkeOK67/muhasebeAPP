from flask import Blueprint, render_template, request, redirect, url_for, session, flash

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('main/index.html')


@bp.route('/lisans')
def lisans():
    return render_template('main/lisans.html')


@bp.route('/lisans', methods=['POST'])
def lisans_validate():
    key = (request.form.get('license_key') or '').strip()
    device_id = (request.form.get('device_id') or '').strip()
    if not key:
        flash('Lisans anahtarı girin.', 'error')
        return redirect(url_for('main.lisans'))
    try:
        from app.license_check import validate_and_activate
        ok, err, info = validate_and_activate(key, device_id)
        if ok and info is not None:
            session['license_key'] = key
            # Lisans sahibi adı: email veya not alanı
            holder = (info.get('email') or info.get('notes') or 'Lisans Sahibi').strip() or 'Lisans Sahibi'
            session['license_holder'] = holder
            flash('Lisans doğrulandı.', 'success')
            return redirect(request.form.get('next') or request.args.get('next') or url_for('main.index'))
        if err:
            flash(err, 'error')
    except Exception:
        flash('Geçersiz veya süresi dolmuş lisans.', 'error')
    return redirect(url_for('main.lisans'))


@bp.route('/lisans/cikis')
def lisans_cikis():
    session.pop('license_key', None)
    session.pop('license_holder', None)
    flash('Lisanstan çıkış yapıldı.', 'info')
    return redirect(url_for('main.lisans'))

