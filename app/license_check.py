"""Lisans doğrulama."""
from datetime import datetime

from app.firebase_licenses import _licenses_ref


def _find_license_by_key(key):
    key = (key or '').strip()
    if not key:
        return None, None
    ref = _licenses_ref()
    if ref is None:
        return None, None
    try:
        snap = ref.get()
    except Exception:
        return None, None
    for kid, v in (snap or {}).items():
        if v and v.get('key') == key:
            return kid, v
    return None, None


def get_license_info(key):
    """Lisans bilgisi döner (email, notes). Yoksa None."""
    _, data = _find_license_by_key(key)
    if not data:
        return None
    return {
        'email': (data.get('email') or '').strip(),
        'notes': (data.get('notes') or '').strip(),
    }


def validate_and_activate(key, device_id):
    """
    Lisansı doğrular ve ilk kullanımda bu cihaza aktive eder.
    Returns: (success: bool, error_message: str|None, info: dict|None)
    """
    key = (key or '').strip()
    device_id = (device_id or '').strip()
    if not key:
        return False, 'Lisans anahtarı gerekli.', None
    if not device_id:
        return False, 'Cihaz kimliği alınamadı. Tarayıcıyı yenileyip tekrar deneyin.', None

    kid, data = _find_license_by_key(key)
    if not kid or not data:
        return False, 'Geçersiz lisans anahtarı.', None
    if not data.get('active'):
        return False, 'Bu lisans iptal edilmiş.', None

    exp = data.get('expires_at')
    if exp:
        try:
            if datetime.utcnow() > datetime.strptime(exp, '%Y-%m-%d'):
                return False, 'Lisans süresi dolmuş.', None
        except Exception:
            pass

    info = {'email': (data.get('email') or '').strip(), 'notes': (data.get('notes') or '').strip()}
    activated_at = data.get('activated_at')
    activated_device_id = (data.get('activated_device_id') or '').strip()

    if not activated_at and not activated_device_id:
        now = datetime.utcnow().isoformat() + 'Z'
        child = _licenses_ref(f'/{kid}')
        try:
            child.update({'activated_at': now, 'activated_device_id': device_id})
        except Exception:
            return False, 'Lisans aktive edilemedi.', None
        return True, None, info

    if activated_device_id != device_id:
        return False, 'Bu lisans başka bir cihazda aktif. Başka cihazda kullanılamaz.', None
    return True, None, info


def is_valid_license(key):
    """Session'daki lisans anahtarının geçerliliğini kontrol eder."""
    if not key or not (key or '').strip():
        return False
    ref = _licenses_ref()
    if ref is None:
        return False
    try:
        snap = ref.get()
    except Exception:
        return False
    for v in (snap or {}).values():
        if v and v.get('key') == key and v.get('active'):
            exp = v.get('expires_at')
            if exp:
                try:
                    if datetime.utcnow() > datetime.strptime(exp, '%Y-%m-%d'):
                        return False
                except Exception:
                    pass
            return True
    return False
