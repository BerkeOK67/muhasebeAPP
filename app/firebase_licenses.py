# Lisans Firebase (lisans-takip-fdb2f) - Müşteri uygulaması lisans doğrulama
import os
import json

_fb_licenses_app = None
_APP_NAME = 'licenses_client'


def _init_licenses_firebase():
    global _fb_licenses_app
    if _fb_licenses_app is not None:
        return _fb_licenses_app

    import firebase_admin
    from firebase_admin import credentials

    from config import Config

    cred = None
    if getattr(Config, 'LICENSES_FIREBASE_CREDENTIALS_JSON', None):
        d = json.loads(Config.LICENSES_FIREBASE_CREDENTIALS_JSON)
        cred = credentials.Certificate(d)
    elif getattr(Config, 'LICENSES_FIREBASE_CREDENTIALS', None) and os.path.isfile(Config.LICENSES_FIREBASE_CREDENTIALS):
        cred = credentials.Certificate(Config.LICENSES_FIREBASE_CREDENTIALS)
    else:
        try:
            cred = credentials.ApplicationDefault()
        except Exception:
            cred = None

    if cred is None:
        return None

    try:
        _fb_licenses_app = firebase_admin.initialize_app(
            cred,
            options={'databaseURL': Config.LICENSES_FIREBASE_DATABASE_URL},
            name=_APP_NAME
        )
    except Exception:
        try:
            _fb_licenses_app = firebase_admin.get_app(_APP_NAME)
        except Exception:
            _fb_licenses_app = None

    return _fb_licenses_app


def _licenses_ref(path=''):
    from firebase_admin import db
    app = _init_licenses_firebase()
    if app is None:
        return None
    full_path = f'/licenses{path}' if path else '/licenses'
    return db.reference(full_path, app=app)
