import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kisisel-muhasebe-gizli-anahtar-2024'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Istanbul'
    # Tek test kullanıcı (local / 2 gün canlı debug)
    TEST_USER_EMAIL = 'cenkerhalat@gmail.com'
    TEST_USER_PASSWORD = 'Cenker3131'
    # Firebase Admin (Gelişim grafikleri için gelirler/giderler okuma)
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS')
    FIREBASE_CREDENTIALS_JSON = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL') or \
        'https://kisiselmuhasebe-54c71-default-rtdb.europe-west1.firebasedatabase.app'
