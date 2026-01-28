# Giriş / Çıkış - tek test kullanıcı (config)
from flask import Blueprint, request, redirect, url_for, session, flash, render_template

from config import Config

bp = Blueprint('auth', __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def _inner(*a, **kw):
        if not session.get('user_email'):
            flash('Devam etmek için giriş yapın.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        return f(*a, **kw)
    return _inner


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_email'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = (request.form.get('password') or '').strip()
        if not email or not password:
            flash('E‑posta ve şifre gerekli.', 'error')
            return render_template('auth/login.html')

        if email != Config.TEST_USER_EMAIL.lower() or password != Config.TEST_USER_PASSWORD:
            flash('E‑posta veya şifre hatalı.', 'error')
            return render_template('auth/login.html')

        session['user_email'] = Config.TEST_USER_EMAIL
        session['user_id'] = 'test'
        flash('Hoş geldin!', 'success')
        raw_next = request.form.get('next') or request.args.get('next') or ''
        next_url = url_for('main.index')
        if raw_next and raw_next.startswith('/') and '://' not in raw_next:
            next_url = raw_next
        return redirect(next_url)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_id', None)
    flash('Çıkış yaptınız.', 'info')
    return redirect(url_for('auth.login'))
