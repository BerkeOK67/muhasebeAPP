import os

from dotenv import load_dotenv
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kisisel-muhasebe-gizli-anahtar-2024'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Istanbul'
    # Firebase (gelir/gider veritabanı, gelişim grafikleri)
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS')
    FIREBASE_CREDENTIALS_JSON = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL') or \
        'https://kisiselmuhasebe-54c71-default-rtdb.europe-west1.firebasedatabase.app'

    # Lisans Firebase (lisans-takip-fdb2f) - lisans doğrulama
    # Console: https://console.firebase.google.com/project/lisans-takip-fdb2f/database
    LICENSES_FIREBASE_DATABASE_URL = os.environ.get('LICENSES_FIREBASE_DATABASE_URL') or \
        'https://lisans-takip-fdb2f-default-rtdb.firebaseio.com'
    LICENSES_FIREBASE_CREDENTIALS = os.environ.get('LICENSES_FIREBASE_CREDENTIALS')  # Service account JSON dosya yolu
    LICENSES_FIREBASE_CREDENTIALS_JSON = os.environ.get('LICENSES_FIREBASE_CREDENTIALS_JSON')  # Veya JSON string

    # Ana uygulama lisans anahtarı - env veya config'ten
    LICENSE_KEY = os.environ.get('LICENSE_KEY') or ''
