USAGE_TEXT = """
Müşteriye özel EXE oluşturma scripti.

Kullanım:
    python scripts/build_customer.py <musteri_adi>
    python scripts/build_customer.py --list

Örnek:
    python scripts/build_customer.py ahmet
    python scripts/build_customer.py mehmet_ticaret
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

# Proje kök dizini
ROOT = Path(__file__).parent.parent
CUSTOMERS_DIR = ROOT / "customers"
CONFIG_TEMPLATE = ROOT / "config.py"
DIST_DIR = ROOT / "dist"


def list_customers():
    """Mevcut müşteri konfigürasyonlarını listele."""
    if not CUSTOMERS_DIR.exists():
        print("❌ 'customers' klasörü bulunamadı!")
        print(f"   Oluşturun: {CUSTOMERS_DIR}")
        return []
    
    configs = list(CUSTOMERS_DIR.glob("*/config.json"))
    if not configs:
        print("❌ Hiç müşteri konfigürasyonu bulunamadı!")
        print(f"   Örnek: {CUSTOMERS_DIR}/ahmet/config.json")
        return []
    
    print("\n📋 Mevcut Müşteriler:")
    print("-" * 40)
    customers = []
    for cfg in sorted(configs):
        customer_name = cfg.parent.name
        customers.append(customer_name)
        with open(cfg, 'r', encoding='utf-8') as f:
            data = json.load(f)
        holder = data.get('license_holder', 'Belirtilmemiş')
        print(f"  • {customer_name:<20} ({holder})")
    print()
    return customers


def load_customer_config(customer_name: str) -> dict:
    """Müşteri konfigürasyonunu yükle."""
    config_path = CUSTOMERS_DIR / customer_name / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Konfigürasyon bulunamadı: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_config_py(customer_config: dict) -> str:
    """Müşteriye özel config.py içeriği oluştur."""
    # Firebase credentials JSON string olarak embed et
    firebase_creds = customer_config.get('firebase_credentials', {})
    firebase_creds_json = json.dumps(firebase_creds) if firebase_creds else ''
    
    licenses_creds = customer_config.get('licenses_firebase_credentials', {})
    licenses_creds_json = json.dumps(licenses_creds) if licenses_creds else ''
    
    config_content = f'''import os\nfrom datetime import timedelta

from dotenv import load_dotenv
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kisisel-muhasebe-gizli-anahtar-2024'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=3650)
    BABEL_DEFAULT_TIMEZONE = 'Europe/Istanbul'
    
    # Firebase (gelir/gider veritabanı, gelişim grafikleri)
    FIREBASE_CREDENTIALS = None
    FIREBASE_CREDENTIALS_JSON = {repr(firebase_creds_json) if firebase_creds_json else "os.environ.get('FIREBASE_CREDENTIALS_JSON')"}
    FIREBASE_DATABASE_URL = {repr(customer_config.get('firebase_database_url', ''))} or \\
        os.environ.get('FIREBASE_DATABASE_URL')

    # Lisans Firebase (lisans-takip-fdb2f) - lisans doğrulama
    LICENSES_FIREBASE_DATABASE_URL = {repr(customer_config.get('licenses_firebase_database_url', ''))} or \\
        os.environ.get('LICENSES_FIREBASE_DATABASE_URL')
    LICENSES_FIREBASE_CREDENTIALS = None
    LICENSES_FIREBASE_CREDENTIALS_JSON = {repr(licenses_creds_json) if licenses_creds_json else "os.environ.get('LICENSES_FIREBASE_CREDENTIALS_JSON')"}

    # Ana uygulama lisans anahtarı - kullanıcıdan sorulacak
    LICENSE_KEY = os.environ.get('LICENSE_KEY') or ''
'''
    return config_content


FIREBASE_CONFIG_JS = ROOT / "app" / "static" / "js" / "firebase-config.js"

def generate_firebase_config_js(customer_config: dict) -> str:
    """Müşteriye özel firebase-config.js içeriği oluştur."""
    # Firebase web config bilgilerini al
    web_config = customer_config.get('firebase_web_config', {})
    
    # Eğer web_config yoksa, credentials'tan project_id kullanarak oluştur
    if not web_config:
        firebase_creds = customer_config.get('firebase_credentials', {})
        project_id = firebase_creds.get('project_id', '')
        database_url = customer_config.get('firebase_database_url', '')
        
        # Basit config oluştur (API key olmadan çalışmayabilir)
        config_content = f'''// Firebase Configuration - {customer_config.get('license_holder', 'Customer')}
// NOT: Bu config otomatik olarak oluşturuldu
const firebaseConfig = {{
    databaseURL: "{database_url}",
    projectId: "{project_id}"
}};

export {{ firebaseConfig }};
'''
    else:
        # Tam web config varsa kullan
        config_content = f'''// Firebase Configuration - {customer_config.get('license_holder', 'Customer')}
const firebaseConfig = {{
    apiKey: "{web_config.get('apiKey', '')}",
    authDomain: "{web_config.get('authDomain', '')}",
    databaseURL: "{customer_config.get('firebase_database_url', '')}",
    projectId: "{web_config.get('projectId', '')}",
    storageBucket: "{web_config.get('storageBucket', '')}",
    messagingSenderId: "{web_config.get('messagingSenderId', '')}",
    appId: "{web_config.get('appId', '')}"
}};

export {{ firebaseConfig }};
'''
    return config_content

def clear_pycache(directory):
    """__pycache__ klasörlerini temizle."""
    import glob
    patterns = [
        os.path.join(directory, '**', '__pycache__'),
        os.path.join(directory, '**', '*.pyc'),
        os.path.join(directory, '**', '*.pyo'),
    ]
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception:
                pass


def build_exe(customer_name: str):
    """Müşteri için EXE oluştur."""
    print(f"\n🔨 {customer_name} için EXE oluşturuluyor...")
    print("=" * 50)
    
    # 0. Önce cache temizle (eski config kalıntılarını sil)
    print("🗑️  Cache temizleniyor...")
    clear_pycache(ROOT)
    # PyInstaller build cache temizle
    build_dir = ROOT / "build"
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
            print("✅ PyInstaller build cache temizlendi")
        except Exception as e:
            print(f"⚠️  Build cache temizlenemedi: {e}")
    
    # 1. Müşteri config'ini yükle
    try:
        customer_config = load_customer_config(customer_name)
    except FileNotFoundError as e:
        print(f"❌ Hata: {e}")
        return False
    
    print(f"✅ Konfigürasyon yüklendi: {customer_config.get('license_holder', customer_name)}")
    
    # Debug: Firebase URL'lerini göster
    print(f"   📌 Firebase URL: {customer_config.get('firebase_database_url', 'Belirtilmemiş')[:50]}...")
    print(f"   📌 Lisans Firebase URL: {customer_config.get('licenses_firebase_database_url', 'Belirtilmemiş')[:50]}...")
    
    # 2. Müşteriye özel config.py oluştur
    new_config = generate_config_py(customer_config)
    with open(CONFIG_TEMPLATE, 'w', encoding='utf-8') as f:
        f.write(new_config)
    print("✅ Müşteriye özel config.py oluşturuldu")
    
    # Debug: Oluşturulan config.py içinde doğru URL'ler var mı kontrol et
    with open(CONFIG_TEMPLATE, 'r', encoding='utf-8') as f:
        written_content = f.read()
    if customer_config.get('firebase_database_url', '') in written_content:
        print("   ✓ Firebase URL doğru yazıldı")
    else:
        print("   ⚠️ UYARI: Firebase URL config.py'de bulunamadı!")
    if customer_config.get('licenses_firebase_database_url', '') in written_content:
        print("   ✓ Lisans Firebase URL doğru yazıldı")
    else:
        print("   ⚠️ UYARI: Lisans Firebase URL config.py'de bulunamadı!")
    
    # 2.5 Frontend firebase-config.js dosyasını güncelle
    new_firebase_config = generate_firebase_config_js(customer_config)
    with open(FIREBASE_CONFIG_JS, 'w', encoding='utf-8') as f:
        f.write(new_firebase_config)
    print("✅ Frontend firebase-config.js güncellendi")
    
    # 3. PyInstaller ile EXE derle
    print("\n📦 PyInstaller çalıştırılıyor...")
    result = subprocess.run(
        [sys.executable, '-m', 'PyInstaller', 'KisiselMuhasebe.spec', '--noconfirm'],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ PyInstaller hatası:\n{result.stderr}")
        return False
    
    print("✅ EXE başarıyla derlendi")
    
    # 4. EXE'yi müşteri klasörüne kopyala
    exe_source = DIST_DIR / "KisiselMuhasebe.exe"
    customer_dist = CUSTOMERS_DIR / customer_name / "dist"
    customer_dist.mkdir(exist_ok=True)
    
    exe_dest = customer_dist / f"KisiselMuhasebe_{customer_name}.exe"
    shutil.copy(exe_source, exe_dest)
    print(f"✅ EXE kopyalandı: {exe_dest}")
    
    print("\n" + "=" * 50)
    print(f"🎉 {customer_name} için EXE hazır!")
    print(f"📁 Konum: {exe_dest}")
    return True


def create_sample_config():
    """Örnek müşteri konfigürasyonu oluştur."""
    sample_dir = CUSTOMERS_DIR / "_ornek_musteri"
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    sample_config = {
        "license_holder": "Örnek Şirket A.Ş.",
        "license_key": "XXXX-XXXX-XXXX-XXXX",
        "firebase_database_url": "https://PROJE-ADI-default-rtdb.europe-west1.firebasedatabase.app",
        "firebase_credentials": {
            "type": "service_account",
            "project_id": "PROJE-ADI",
            "private_key_id": "...",
            "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-xxxxx@PROJE-ADI.iam.gserviceaccount.com",
            "client_id": "...",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        },
        "licenses_firebase_database_url": "https://lisans-takip-fdb2f-default-rtdb.firebaseio.com",
        "licenses_firebase_credentials": {
            "type": "service_account",
            "project_id": "lisans-takip-fdb2f",
            "private_key_id": "...",
            "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
            "client_email": "...",
            "client_id": "..."
        }
    }
    
    config_path = sample_dir / "config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Örnek konfigürasyon oluşturuldu: {config_path}")
    print("   Bu dosyayı düzenleyerek yeni müşteri ekleyebilirsiniz.")
    print("\n   Adımlar:")
    print("   1. _ornek_musteri klasörünü kopyalayın (örn: ahmet_ticaret)")
    print("   2. config.json içindeki bilgileri güncelleyin")
    print("   3. python scripts/build_customer.py ahmet_ticaret")


def main():
    if len(sys.argv) < 2:
        print(USAGE_TEXT)
        print("\n" + "=" * 50)
        list_customers()
        return
    
    arg = sys.argv[1].lower()
    
    if arg in ('--list', '-l', 'list'):
        list_customers()
    elif arg in ('--sample', '-s', 'sample', 'ornek'):
        create_sample_config()
    elif arg in ('--help', '-h', 'help'):
        print(USAGE_TEXT)
    else:
        customer_name = sys.argv[1]
        success = build_exe(customer_name)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
