# Kisisel Muhasebe - Gelir/Gider Takip Uygulamasi

Modern ve kullanici dostu kisisel finans yonetim uygulamasi. Flask + Firebase altyapisi ile gercek zamanli veri senkronizasyonu.

## Ozellikler

- **Gelir Takibi** - Maas, serbest calisma, yatirim gelirleri
- **Gider Takibi** - Tek seferlik ve taksitli giderler
- **Taksit Yonetimi** - Otomatik taksit hesaplama ve ilerleme takibi
- **Alacak Takibi** - Tahsilat bekleyen borclar ve odeme gecmisi
- **Gelisim Grafikleri** - Aylik/yillik finansal analiz
- **Gercek Zamanli Senkronizasyon** - Firebase Realtime Database

## Demo / Deneme

### Windows EXE Indirme

1. [Releases](../../releases) sayfasindan son surumu indirin
2. `KisiselMuhasebe.exe` dosyasini indirin
3. EXE'yi calistirin
4. Lisans anahtari girin (demo icin asagidaki anahtari kullanin)

**Demo Lisans Anahtari:** `963F-24D7-BDC6-411A`

> **Not:** Demo surum test amaclidir. Gercek kullanim icin kendi Firebase projenizi olusturmaniz gerekir.

## Kurulum (Gelistirici)

### Gereksinimler

- Python 3.10+
- Firebase hesabi
- Firebase Realtime Database

### Adimlar

1. **Repoyu klonlayin**
```bash
git clone https://https://github.com/BerkeOK67/muhasebeAPP.git
cd muhasebeAPP
```

2. **Sanal ortam olusturun**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# veya
source venv/bin/activate  # Linux/Mac
```

3. **Bagimliliklari yukleyin**
```bash
pip install -r requirements.txt
```

4. **Firebase yapilandirmasi**

Ornek dosyalari kopyalayin ve duzenleyin:

```bash
# Konfigurasyon dosyalari
copy config.py.example config.py
copy .env.example .env
copy app\static\js\firebase-config.js.example app\static\js\firebase-config.js
```

Dosyalari kendi Firebase bilgilerinizle doldurun:
- `config.py` - Backend Firebase credentials (Service Account)
- `app/static/js/firebase-config.js` - Frontend Firebase config (Web App)
- `.env` - Environment variables

Firebase credentials almak icin:
1. [Firebase Console](https://console.firebase.google.com/) gidin
2. Project Settings > Service Accounts > Generate new private key
3. JSON icerigi `config.py` veya `.env` icine yapistirilabilir

5. **Uygulamayi calistirin**
```bash
python run.py
```

Tarayicida `http://localhost:5000` adresine gidin.

## Musteri Ozel EXE Olusturma

Her musteri icin ayri Firebase projesi ve EXE olusturabilirsiniz:

1. `customers/` klasorunde yeni musteri klasoru olusturun
2. `config.json` dosyasini yapilandirin (ornek: `customers/_ornek_musteri/config.json`)
3. Build scriptini calistirin:

```bash
python scripts/build_customer.py MUSTERI_ADI
```

Detaylar icin: [MUSTERI_PAKETI.md](MUSTERI_PAKETI.md)

## Proje Yapisi

```
kisiselmuhasebe/
├── app/
│   ├── templates/          # HTML sablonlari
│   ├── static/             # CSS, JS dosyalari
│   ├── main/               # Ana sayfa route'lari
│   ├── gelirler/           # Gelir yonetimi
│   ├── giderler/           # Gider yonetimi
│   ├── alacaklilar/        # Alacak takibi
│   ├── gelisim/            # Gelisim grafikleri
│   ├── firebase_admin.py   # Firebase baglantisi
│   ├── firebase_licenses.py # Lisans kontrolu
│   └── license_check.py    # Lisans dogrulama
├── customers/              # Musteri konfigurasyonlari
├── scripts/
│   └── build_customer.py   # EXE olusturma scripti
├── dist/                   # Derlenmis EXE dosyalari
├── config.py               # Uygulama ayarlari
├── launcher.py             # EXE giris noktasi
├── run.py                  # Gelistirme sunucusu
└── KisiselMuhasebe.spec    # PyInstaller spec dosyasi
```

## Teknolojiler

- **Backend:** Flask, Python
- **Database:** Firebase Realtime Database
- **Frontend:** HTML5, CSS3, JavaScript (ES6 Modules)
- **Build:** PyInstaller
- **UI:** Custom CSS, Font Awesome icons

## Lisans

Bu proje ozel lisanslidir. Ticari kullanim icin iletisime gecin.

## Iletisim

Sorulariniz icin issue aciniz veya iletisime geciniz.
