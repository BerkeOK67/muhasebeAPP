import os
import sys

from flask import Flask, session, request, redirect, url_for

from config import Config


def create_app():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
        app = Flask(__name__,
                    template_folder=os.path.join(base, 'app', 'templates'),
                    static_folder=os.path.join(base, 'app', 'static'),
                    static_url_path='/static')
    else:
        app = Flask(__name__)
    app.config.from_object(Config)

    @app.before_request
    def require_license():
        if request.endpoint in (None, 'static'):
            return None
        if request.path.startswith('/static/'):
            return None
        if request.endpoint in ('main.lisans', 'main.lisans_validate'):
            return None
        key = session.get('license_key') or Config.LICENSE_KEY
        if not key:
            return redirect(url_for('main.lisans', next=request.full_path.rstrip('?') or request.path))
        try:
            from app.license_check import is_valid_license
            if not is_valid_license(key):
                session.pop('license_key', None)
                return redirect(url_for('main.lisans', next=request.full_path.rstrip('?') or request.path))
        except Exception:
            return redirect(url_for('main.lisans', next=request.full_path.rstrip('?') or request.path))
        return None

    # Jinja2 için global değişkenler (sabit Europe/Istanbul + lisans sahibi)
    @app.context_processor
    def inject_globals():
        import pytz
        from datetime import datetime
        tz = pytz.timezone(Config.BABEL_DEFAULT_TIMEZONE)
        now = datetime.now(tz)
        return {
            'current_datetime': now,
            'license_holder': session.get('license_holder'),
        }
    
    # Blueprint'leri kaydet
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.gelirler import bp as gelirler_bp
    app.register_blueprint(gelirler_bp, url_prefix='/gelirler')
    
    from app.giderler import bp as giderler_bp
    app.register_blueprint(giderler_bp, url_prefix='/giderler')
    
    from app.alacaklilar import bp as alacaklilar_bp
    app.register_blueprint(alacaklilar_bp, url_prefix='/alacaklilar')
    
    from app.gelisim import bp as gelisim_bp
    app.register_blueprint(gelisim_bp)
    
    return app
