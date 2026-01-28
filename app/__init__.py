from flask import Flask, request, session
from config import Config

def get_timezone():
    if 'timezone' in session:
        return session['timezone']
    return Config.BABEL_DEFAULT_TIMEZONE

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Jinja2 için global değişkenler
    @app.context_processor
    def inject_globals():
        import pytz
        from datetime import datetime
        
        tz = pytz.timezone(get_timezone())
        now = datetime.now(tz)
        
        return {
            'current_timezone': get_timezone(),
            'timezones': Config.get_grouped_timezones(),
            'current_datetime': now
        }
    
    # Saat dilimi değiştirme
    @app.route('/set-timezone/<path:timezone>')
    def set_timezone(timezone):
        import pytz
        if timezone in pytz.all_timezones:
            session['timezone'] = timezone
        return ('', 204)
    
    # Blueprint'leri kaydet
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.gelirler import bp as gelirler_bp
    app.register_blueprint(gelirler_bp, url_prefix='/gelirler')
    
    from app.giderler import bp as giderler_bp
    app.register_blueprint(giderler_bp, url_prefix='/giderler')
    
    from app.alacaklilar import bp as alacaklilar_bp
    app.register_blueprint(alacaklilar_bp, url_prefix='/alacaklilar')
    
    return app
