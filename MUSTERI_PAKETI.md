# Müşteri Paketi — Hangi Dosyalar Verilir / Verilmez

Proje kökündeki **gerçek klasör yapısına** göre liste.

---

## Nasıl çalışır? (Web servis değil, tamamen local)

- Uygulama **müşterinin kendi bilgisayarında** çalışır.
- **Web sunucusu / hosting kurulması gerekmez.** EXE’ye tıklayınca veya `python run.py` / `python launcher.py` çalıştırınca, yerelde bir sunucu (127.0.0.1:5001) açar ve tarayıcı bu adrese gider.
- İnternet sadece **Firebase** (veri + lisans doğrulama) için gerekir. Veritabanı ve lisans sizin Firebase projenizde; uygulama oraya bağlanır. Ayrı bir “web servis” veya sunucu tarafında kurulum yok.
- Bu dosyalar verildiğinde, müşteri tarafında **çalışabilirlik** açısından ek bir web servisi veya kurulum gerekmez; sadece EXE veya Python ortamı yeterli.

---

## Müşteriye VERİLECEKLER (kaynak kod verirken)

| Dosya / Klasör | Ver? | Not |
|----------------|------|-----|
| **app/** | ✅ Evet | Tüm klasör (templates, static, tüm modüller). |
| **config.py** | ✅ Evet | Uygulama ayarları. |
| **launcher.py** | ✅ Evet | EXE / masaüstü başlatıcı. |
| **run.py** | ✅ Evet | Sunucu başlatma. |
| **requirements.txt** | ✅ Evet | Bağımlılıklar. |
| **Procfile** | ⚪ İsteğe bağlı | Sadece Heroku’ya deploy edecekse verin. |
| **.gitignore** | ⚪ İsteğe bağlı | Verseniz de olur; müşteri için zorunlu değil. |

---

## Müşteriye VERİLMEYECEKLER

| Dosya / Klasör | Neden |
|----------------|--------|
| **admin_app/** | Lisans yönetim paneli; sadece sizde kalmalı. (Projede yoksa zaten vermezsiniz.) |
| **run_admin.py** | Admin paneli çalıştırıcı. (Projede yoksa vermezsiniz.) |
| **KisiselMuhasebe.spec** | EXE’yi siz üretirsiniz; müşteriye gerek yok. |
| **MUSTERI_PAKETI.md** | Bu dosya; iç talimat. |
| **.env** | Gizli bilgiler (Firebase, secret key vb.); asla verilmez. |
| **build/** | PyInstaller build çıktısı. |
| **dist/** | EXE burada oluşur; kaynak verirken klasörü vermeyin. EXE tek başına verilecekse sadece `KisiselMuhasebe.exe` dosyasını verin. |
| **\*.json** (credentials) | `*-firebase-adminsdk-*.json`, `serviceAccountKey*.json`, `lisans-takip-credentials.json` vb. asla verilmez. |
| **.git/** | İsteğe bağlı; genelde müşteriye vermeyin. |

---

## Sadece EXE verirken

Müşteriye **sadece** şu dosyayı verin:

- **dist/KisiselMuhasebe.exe**

(EXE’yi `pyinstaller KisiselMuhasebe.spec` ile üretirsiniz.)

---

## Özet kontrol listesi (kaynak paketi)

Müşteri paketine **mutlaka** dahil edin:

- `app/` (içindeki her şey)
- `config.py`
- `launcher.py`
- `run.py`
- `requirements.txt`

**Kesinlikle dahil etmeyin:**

- `admin_app/`, `run_admin.py` (varsa)
- `KisiselMuhasebe.spec`, `MUSTERI_PAKETI.md`
- `.env`, credentials JSON dosyaları
- `build/`, `dist/` (veya sadece EXE verirken sadece `KisiselMuhasebe.exe`)

Bu liste, proje kökündeki mevcut klasör içeriğine göre güncellenmiştir.
