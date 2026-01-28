# Firebase Admin SDK - Gelişim grafikleri için gelirler/giderler okuma
import os
import json

_fb_app = None


def _init_firebase():
    global _fb_app
    if _fb_app is not None:
        return _fb_app

    import firebase_admin
    from firebase_admin import credentials

    from config import Config

    cred = None
    if Config.FIREBASE_CREDENTIALS_JSON:
        d = json.loads(Config.FIREBASE_CREDENTIALS_JSON)
        cred = credentials.Certificate(d)
    elif Config.FIREBASE_CREDENTIALS and os.path.isfile(Config.FIREBASE_CREDENTIALS):
        cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
    else:
        try:
            cred = credentials.ApplicationDefault()
        except Exception:
            cred = None

    if cred is None:
        return None

    try:
        _fb_app = firebase_admin.initialize_app(cred, options={'databaseURL': Config.FIREBASE_DATABASE_URL})
    except Exception:
        _fb_app = firebase_admin.get_app() if firebase_admin._apps else None

    return _fb_app


def _db_ref(path):
    from firebase_admin import db
    app = _init_firebase()
    if app is None:
        return None
    return db.reference(path)


def get_collection(name):
    """Firebase koleksiyonunu liste olarak döner: [{id, ...}, ...]"""
    ref = _db_ref(name)
    if ref is None:
        return []
    try:
        snap = ref.get()
    except Exception:
        return []
    if not snap:
        return []
    return [{'id': k, **(v or {})} for k, v in (snap or {}).items()]
