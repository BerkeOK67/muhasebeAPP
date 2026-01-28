from flask import Flask, request, session, redirect, url_for

from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Auth blueprint (login/logout)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    # Koruma: giriş yoksa /login'e yönlendir
    @app.before_request
    def require_login():
        if request.endpoint in ('auth.login', 'auth.logout', 'static'):
            return None
        if request.path.startswith('/static/'):
            return None
        if not session.get('user_email'):
            return redirect(url_for('auth.login', next=request.full_path.rstrip('?') or request.path))
        return None
    
    # Jinja2 için global değişkenler (sabit Europe/Istanbul)
    @app.context_processor
    def inject_globals():
        import pytz
        from datetime import datetime
        tz = pytz.timezone(Config.BABEL_DEFAULT_TIMEZONE)
        now = datetime.now(tz)
        return {
            'current_datetime': now,
            'current_user_email': session.get('user_email'),
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
