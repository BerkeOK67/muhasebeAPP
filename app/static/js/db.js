/**
 * Kişisel Muhasebe - Veritabanı Modülü
 * Firebase + LocalStorage Senkronizasyonu
 */

// ==================== TOAST BİLDİRİM SİSTEMİ ====================
const Toast = {
    container: null,
    
    init() {
        if (this.container) return;
        
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.style.cssText = `
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            max-width: 380px;
        `;
        document.body.appendChild(this.container);
    },
    
    show(message, type = 'info', duration = 4000) {
        this.init();
        
        const toast = document.createElement('div');
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            firebase: '🔥',
            local: '💾',
            sync: '🔄'
        };
        
        const colors = {
            success: { bg: '#dcfce7', border: '#22c55e', text: '#166534' },
            error: { bg: '#fee2e2', border: '#ef4444', text: '#991b1b' },
            warning: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
            info: { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' },
            firebase: { bg: '#ffedd5', border: '#f97316', text: '#9a3412' },
            local: { bg: '#e0e7ff', border: '#6366f1', text: '#3730a3' },
            sync: { bg: '#f3e8ff', border: '#a855f7', text: '#6b21a8' }
        };
        
        const color = colors[type] || colors.info;
        const icon = icons[type] || icons.info;
        
        toast.style.cssText = `
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 1.25rem;
            background: ${color.bg};
            border: 1px solid ${color.border};
            border-left: 4px solid ${color.border};
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease;
            font-size: 0.9rem;
            color: ${color.text};
        `;
        
        toast.innerHTML = `
            <span style="font-size: 1.25rem;">${icon}</span>
            <span style="flex: 1; line-height: 1.4;">${message}</span>
            <button onclick="this.parentElement.remove()" style="
                background: none;
                border: none;
                font-size: 1.25rem;
                cursor: pointer;
                opacity: 0.5;
                color: inherit;
            ">×</button>
        `;
        
        this.container.appendChild(toast);
        
        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        return toast;
    },
    
    success(msg, duration) { return this.show(msg, 'success', duration); },
    error(msg, duration) { return this.show(msg, 'error', duration); },
    warning(msg, duration) { return this.show(msg, 'warning', duration); },
    info(msg, duration) { return this.show(msg, 'info', duration); },
    firebase(msg, duration) { return this.show(msg, 'firebase', duration); },
    local(msg, duration) { return this.show(msg, 'local', duration); },
    sync(msg, duration) { return this.show(msg, 'sync', duration); }
};

// Toast animasyonları için CSS ekle
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(toastStyles);

window.Toast = Toast;

// ==================== BAĞLANTI YÖNETİMİ ====================
let firebaseConnected = false;
let firebaseApp = null;
let firebaseDb = null;
let firebaseInitError = null;

function showFirebaseError() {
    const errorMsg = firebaseInitError 
        ? `Firebase bağlantı hatası: ${firebaseInitError.message || firebaseInitError}`
        : 'Firebase bağlantısı kurulamadı! Lütfen internet bağlantınızı kontrol edin ve sayfayı yenileyin.';
    
    Toast.error(errorMsg, 0); // Süresiz göster
    
    // Sayfaya hata mesajı ekle (eğer yoksa)
    if (document.getElementById('firebase-error-banner')) {
        return; // Zaten gösteriliyor
    }
    
    const errorDiv = document.createElement('div');
    errorDiv.id = 'firebase-error-banner';
    errorDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1.5rem;
        text-align: center;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    errorDiv.innerHTML = `
        <div style="max-width: 800px; margin: 0 auto;">
            <h3 style="margin: 0 0 0.5rem 0; font-size: 1.25rem;">
                <i class="fas fa-exclamation-triangle" style="margin-right: 0.5rem;"></i>
                Firebase Bağlantı Hatası
            </h3>
            <p style="margin: 0; font-size: 0.95rem; opacity: 0.95;">
                ${errorMsg}
            </p>
            <button onclick="window.location.reload()" style="
                margin-top: 1rem;
                padding: 0.5rem 1.5rem;
                background: white;
                color: #ef4444;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
            ">
                <i class="fas fa-sync-alt" style="margin-right: 0.5rem;"></i>
                Sayfayı Yenile
            </button>
        </div>
    `;
    document.body.insertBefore(errorDiv, document.body.firstChild);
}

function throwFirebaseError() {
    showFirebaseError();
    throw new Error('Firebase bağlantısı gerekli!');
}

async function initFirebase() {
    try {
        const { initializeApp } = await import('https://www.gstatic.com/firebasejs/11.0.0/firebase-app.js');
        const { getDatabase } = await import('https://www.gstatic.com/firebasejs/11.0.0/firebase-database.js');
        const { firebaseConfig } = await import('./firebase-config.js');
        
        if (firebaseConfig.apiKey === "YOUR_API_KEY" || !firebaseConfig.databaseURL) {
            firebaseInitError = new Error('Firebase yapılandırması eksik veya geçersiz!');
            firebaseConnected = false;
            throwFirebaseError();
            return false;
        }
        
        // Firebase uygulamasını ve veritabanını başlat
        firebaseApp = initializeApp(firebaseConfig);
        firebaseDb = getDatabase(firebaseApp);
        
        firebaseConnected = true;
        firebaseInitError = null;
        
        // Hata banner'ını kaldır (varsa)
        const errorBanner = document.getElementById('firebase-error-banner');
        if (errorBanner) {
            errorBanner.remove();
        }
        
        Toast.success('Firebase bağlantısı başarılı!', 3000);
        
        return true;
    } catch (error) {
        firebaseConnected = false;
        firebaseInitError = error;
        showFirebaseError();
        return false;
    }
}

export function isOnline() {
    return firebaseConnected;
}

export function getMode() {
    return 'firebase';
}

// LocalStorage desteği kaldırıldı - Sadece Firebase kullanılıyor

// ==================== FIREBASE OPERASYONLARI ====================
let firebaseRefs = null;

async function getFirebaseRefs() {
    if (!firebaseRefs) {
        const { ref, push, set, get, update, remove, onValue } = 
            await import('https://www.gstatic.com/firebasejs/11.0.0/firebase-database.js');
        firebaseRefs = { ref, push, set, get, update, remove, onValue };
    }
    return firebaseRefs;
}

// Senkronizasyon kaldırıldı - Sadece Firebase kullanılıyor

// ==================== GENERIC CRUD ====================
function createCRUD(collectionName) {
    return {
        dinle: async (callback) => {
            await init();
            
            if (!firebaseConnected) {
                showFirebaseError();
                return;
            }
            
            const { ref, onValue } = await getFirebaseRefs();
            const collectionRef = ref(firebaseDb, collectionName);
            
            onValue(collectionRef, (snapshot) => {
                const data = snapshot.val();
                const items = data ? Object.entries(data).map(([id, val]) => ({ id, ...val })) : [];
                callback(items);
            });
        },

        hepsiniGetir: async () => {
            await init();
            
            if (!firebaseConnected) {
                showFirebaseError();
                return [];
            }
            
            try {
                const { ref, get } = await getFirebaseRefs();
                const snapshot = await get(ref(firebaseDb, collectionName));
                const data = snapshot.val();
                return data ? Object.entries(data).map(([id, val]) => ({ id, ...val })) : [];
            } catch (error) {
                Toast.error('Veri okuma hatası: ' + error.message);
                throw error;
            }
        },

        getir: async (id) => {
            await init();
            
            if (!firebaseConnected) {
                showFirebaseError();
                return null;
            }
            
            try {
                const { ref, get } = await getFirebaseRefs();
                const snapshot = await get(ref(firebaseDb, `${collectionName}/${id}`));
                return snapshot.val() ? { id, ...snapshot.val() } : null;
            } catch (error) {
                Toast.error('Veri okuma hatası: ' + error.message);
                throw error;
            }
        },

        ekle: async (item) => {
            await init();
            
            if (!firebaseConnected) {
                showFirebaseError();
                throw new Error('Firebase bağlantısı gerekli!');
            }
            
            const now = new Date().toISOString();
            const itemWithDates = {
                ...item,
                olusturma_tarihi: now,
                guncelleme_tarihi: now
            };

            try {
                const { ref, push, set } = await getFirebaseRefs();
                const newRef = push(ref(firebaseDb, collectionName));
                await set(newRef, itemWithDates);
                return newRef.key;
            } catch (error) {
                Toast.error('Firebase yazma hatası: ' + error.message);
                throw error;
            }
        },

        guncelle: async (id, item) => {
            await init();
            
            if (!firebaseConnected) {
                showFirebaseError();
                throw new Error('Firebase bağlantısı gerekli!');
            }
            
            const now = new Date().toISOString();
            const updatedFields = {
                ...item,
                guncelleme_tarihi: now
            };
            
            try {
                const { ref, update } = await getFirebaseRefs();
                await update(ref(firebaseDb, `${collectionName}/${id}`), updatedFields);
            } catch (error) {
                Toast.error('Güncelleme hatası: ' + error.message);
                throw error;
            }
        },

        sil: async (id) => {
            await init();
            
            if (!firebaseConnected) {
                showFirebaseError();
                throw new Error('Firebase bağlantısı gerekli!');
            }
            
            try {
                const { ref, remove } = await getFirebaseRefs();
                await remove(ref(firebaseDb, `${collectionName}/${id}`));
            } catch (error) {
                Toast.error('Silme hatası: ' + error.message);
                throw error;
            }
        }
    };
}

// ==================== GELİRLER ====================
export const Gelirler = {
    ...createCRUD('gelirler'),
    
    toplamGetir: async () => {
        const gelirler = await Gelirler.hepsiniGetir();
        return gelirler.reduce((toplam, g) => toplam + (parseFloat(g.tutar) || 0), 0);
    },
    
    aylikToplam: async () => {
        const gelirler = await Gelirler.hepsiniGetir();
        const buAy = new Date();
        const ayBaslangic = new Date(buAy.getFullYear(), buAy.getMonth(), 1);
        
        return gelirler
            .filter(g => new Date(g.tarih) >= ayBaslangic)
            .reduce((toplam, g) => toplam + (parseFloat(g.tutar) || 0), 0);
    }
};

// ==================== GİDERLER ====================
export const Giderler = {
    ...createCRUD('giderler'),
    
    gercekTutar: (gider) => {
        if (gider.taksitli && gider.aylik_taksit) {
            return parseFloat(gider.aylik_taksit) || 0;
        }
        return parseFloat(gider.tutar) || 0;
    },
    
    buAyTaksitTutari: (gider) => {
        if (!gider.taksitli) return parseFloat(gider.tutar) || 0;
        
        const ilkTarih = new Date(gider.ilk_taksit_tarihi || gider.tarih);
        const buAy = new Date();
        const ayFarki = (buAy.getFullYear() - ilkTarih.getFullYear()) * 12 + (buAy.getMonth() - ilkTarih.getMonth());
        const taksitSayisi = gider.taksit_sayisi || 1;
        
        if (ayFarki >= 0 && ayFarki < taksitSayisi) {
            return parseFloat(gider.aylik_taksit) || (parseFloat(gider.tutar) / taksitSayisi);
        }
        return 0;
    },
    
    toplamGetir: async () => {
        const giderler = await Giderler.hepsiniGetir();
        return giderler.reduce((toplam, g) => toplam + Giderler.gercekTutar(g), 0);
    },
    
    aylikToplam: async () => {
        const giderler = await Giderler.hepsiniGetir();
        const buAy = new Date();
        const ayBaslangic = new Date(buAy.getFullYear(), buAy.getMonth(), 1);
        const aySonu = new Date(buAy.getFullYear(), buAy.getMonth() + 1, 0);
        
        return giderler.reduce((toplam, gider) => {
            if (gider.taksitli) {
                return toplam + Giderler.buAyTaksitTutari(gider);
            } else {
                const tarih = new Date(gider.tarih);
                if (tarih >= ayBaslangic && tarih <= aySonu) {
                    return toplam + (parseFloat(gider.tutar) || 0);
                }
            }
            return toplam;
        }, 0);
    }
};

// ==================== ALACAKLILAR ====================
export const Alacaklilar = {
    ...createCRUD('alacaklilar'),
    
    toplamAlacak: async () => {
        const alacaklilar = await Alacaklilar.hepsiniGetir();
        return alacaklilar.reduce((toplam, a) => toplam + (parseFloat(a.kalan_borc) || 0), 0);
    },
    
    odemeYap: async (id, odemeTutari, odemeTarihi = null) => {
        const alacakli = await Alacaklilar.getir(id);
        if (!alacakli) throw new Error('Alacaklı bulunamadı');
        
        const mevcutKalan = parseFloat(alacakli.kalan_borc) || 0;
        const yeniKalan = mevcutKalan - odemeTutari;
        
        if (odemeTutari > mevcutKalan) {
            throw new Error('Ödeme tutarı kalan borçtan fazla olamaz');
        }
        
        const odemeler = alacakli.odemeler || [];
        odemeler.push({
            tutar: odemeTutari,
            tarih: odemeTarihi || new Date().toISOString(),
            id: Date.now().toString(36)
        });
        
        if (yeniKalan <= 0) {
            // Borcu bitenler listesine ekle
            const bitenKayit = {
                ...alacakli,
                kalan_borc: 0,
                odemeler: odemeler,
                tamamlanma_tarihi: odemeTarihi || new Date().toISOString()
            };
            delete bitenKayit.id; // ID'yi kaldır, yeni ID oluşturulacak
            
            await BorcuBitenler.ekle(bitenKayit);
            
            // Tahsilat listesinden sil
            await Alacaklilar.sil(id);
            return { tamamenOdendi: true, kalan: 0 };
        } else {
            await Alacaklilar.guncelle(id, {
                kalan_borc: yeniKalan,
                odemeler: odemeler
            });
            return { tamamenOdendi: false, kalan: yeniKalan };
        }
    },
    
    odemeGecmisi: async (id) => {
        const alacakli = await Alacaklilar.getir(id);
        return alacakli?.odemeler || [];
    }
};

// ==================== BORCU BİTENLER ====================
export const BorcuBitenler = {
    ...createCRUD('borcu_bitenler'),
    
    toplamTamamlanan: async () => {
        const bitenler = await BorcuBitenler.hepsiniGetir();
        return bitenler.reduce((toplam, a) => toplam + (parseFloat(a.toplam_borc) || 0), 0);
    }
};

// ==================== KATEGORİLER ====================
export const Kategoriler = {
    gelir: [
        { id: 'maas', ad: 'Maaş', icon: 'fa-money-bill-wave' },
        { id: 'ek_gelir', ad: 'Ek Gelir', icon: 'fa-hand-holding-dollar' },
        { id: 'yeni_musteri', ad: 'Yeni Müşteri', icon: 'fa-user-plus', ozel: true },
        { id: 'alacak_getirisi', ad: 'Tahsilat Getirisi', icon: 'fa-coins', ozel: true },
        { id: 'yatirim', ad: 'Yatırım Getirisi', icon: 'fa-chart-line' },
        { id: 'kira_geliri', ad: 'Kira Geliri', icon: 'fa-house' },
        { id: 'freelance', ad: 'Freelance', icon: 'fa-laptop' },
        { id: 'diger_gelir', ad: 'Diğer', icon: 'fa-plus-circle' }
    ],
    gider: [
        { id: 'market', ad: 'Market', icon: 'fa-shopping-cart' },
        { id: 'fatura', ad: 'Fatura', icon: 'fa-file-invoice' },
        { id: 'kira', ad: 'Kira', icon: 'fa-home' },
        { id: 'ulasim', ad: 'Ulaşım', icon: 'fa-car' },
        { id: 'yemek', ad: 'Yemek', icon: 'fa-utensils' },
        { id: 'saglik', ad: 'Sağlık', icon: 'fa-heart-pulse' },
        { id: 'egitim', ad: 'Eğitim', icon: 'fa-graduation-cap' },
        { id: 'eglence', ad: 'Eğlence', icon: 'fa-film' },
        { id: 'giyim', ad: 'Giyim', icon: 'fa-shirt' },
        { id: 'diger_gider', ad: 'Diğer', icon: 'fa-ellipsis' }
    ]
};

// ==================== DASHBOARD ====================
export const Dashboard = {
    istatistikler: async () => {
        const [gelirler, giderler] = await Promise.all([
            Gelirler.hepsiniGetir(),
            Giderler.hepsiniGetir()
        ]);

        const buAy = new Date();
        const ayBaslangic = new Date(buAy.getFullYear(), buAy.getMonth(), 1);
        const aySonu = new Date(buAy.getFullYear(), buAy.getMonth() + 1, 0);

        const aylikGelir = gelirler
            .filter(g => new Date(g.tarih) >= ayBaslangic && new Date(g.tarih) <= aySonu)
            .reduce((t, g) => t + (parseFloat(g.tutar) || 0), 0);

        const aylikGider = giderler.reduce((toplam, gider) => {
            if (gider.taksitli) {
                return toplam + Giderler.buAyTaksitTutari(gider);
            } else {
                const tarih = new Date(gider.tarih);
                if (tarih >= ayBaslangic && tarih <= aySonu) {
                    return toplam + (parseFloat(gider.tutar) || 0);
                }
            }
            return toplam;
        }, 0);

        const toplamGelir = gelirler.reduce((t, g) => t + (parseFloat(g.tutar) || 0), 0);
        
        const toplamGider = giderler.reduce((t, g) => {
            if (g.taksitli) {
                const ilkTarih = new Date(g.ilk_taksit_tarihi || g.tarih);
                const simdi = new Date();
                const ayFarki = (simdi.getFullYear() - ilkTarih.getFullYear()) * 12 + (simdi.getMonth() - ilkTarih.getMonth()) + 1;
                const odenenTaksit = Math.min(Math.max(ayFarki, 0), g.taksit_sayisi || 1);
                return t + (odenenTaksit * (parseFloat(g.aylik_taksit) || 0));
            }
            return t + (parseFloat(g.tutar) || 0);
        }, 0);

        const tumIslemler = [
            ...gelirler.map(g => ({ ...g, tip: 'gelir' })),
            ...giderler.map(g => ({ ...g, tip: 'gider', gosterimTutar: g.taksitli ? g.aylik_taksit : g.tutar }))
        ].sort((a, b) => new Date(b.tarih) - new Date(a.tarih));

        return {
            aylik_gelir: aylikGelir,
            aylik_gider: aylikGider,
            aylik_bakiye: aylikGelir - aylikGider,
            toplam_gelir: toplamGelir,
            toplam_gider: toplamGider,
            toplam_bakiye: toplamGelir - toplamGider,
            toplam_islem: gelirler.length + giderler.length,
            son_islemler: tumIslemler.slice(0, 10)
        };
    },

    dinle: async (callback) => {
        await init();
        
        if (!firebaseConnected) {
            showFirebaseError();
            return;
        }
        
        const { ref, onValue } = await getFirebaseRefs();
        ['gelirler', 'giderler'].forEach(col => {
            onValue(ref(firebaseDb, col), async () => {
                const stats = await Dashboard.istatistikler();
                callback(stats);
            });
        });
    },
    
    aylikGelirTablosu: async () => {
        const gelirler = await Gelirler.hepsiniGetir();
        const simdi = new Date();
        const yil = simdi.getFullYear();
        
        // Son 12 ay
        const aylikToplamlar = [];
        for (let i = 11; i >= 0; i--) {
            const ay = new Date(yil, simdi.getMonth() - i, 1);
            const ayBaslangic = new Date(ay.getFullYear(), ay.getMonth(), 1);
            const aySonu = new Date(ay.getFullYear(), ay.getMonth() + 1, 0);
            
            const ayGeliri = gelirler
                .filter(g => {
                    const tarih = new Date(g.tarih);
                    return tarih >= ayBaslangic && tarih <= aySonu;
                })
                .reduce((t, g) => t + (parseFloat(g.tutar) || 0), 0);
            
            aylikToplamlar.push({
                ay: ay.toLocaleDateString('tr-TR', { month: 'long', year: 'numeric' }),
                ayKisa: ay.toLocaleDateString('tr-TR', { month: 'short' }),
                yil: ay.getFullYear(),
                ayNumarasi: ay.getMonth(),
                tutar: ayGeliri
            });
        }
        
        return aylikToplamlar;
    },
    
    yillikGelirTablosu: async () => {
        const gelirler = await Gelirler.hepsiniGetir();
        const simdi = new Date();
        const mevcutYil = simdi.getFullYear();
        
        // Son 5 yıl
        const yillikToplamlar = [];
        for (let i = 4; i >= 0; i--) {
            const yil = mevcutYil - i;
            const yilBaslangic = new Date(yil, 0, 1);
            const yilSonu = new Date(yil, 11, 31);
            
            const yilGeliri = gelirler
                .filter(g => {
                    const tarih = new Date(g.tarih);
                    return tarih >= yilBaslangic && tarih <= yilSonu;
                })
                .reduce((t, g) => t + (parseFloat(g.tutar) || 0), 0);
            
            yillikToplamlar.push({
                yil: yil,
                tutar: yilGeliri
            });
        }
        
        return yillikToplamlar;
    }
};

// ==================== YARDIMCI FONKSİYONLAR ====================
// Saat dilimi desteği
function getStoredTimezone() {
    return localStorage.getItem('kisiselmuhasebe_timezone') || 'Europe/Istanbul';
}

function getStoredLanguage() {
    return localStorage.getItem('kisiselmuhasebe_language') || 'tr';
}

export const Yardimci = {
    paraFormat: (tutar) => {
        const lang = getStoredLanguage();
        const locale = lang === 'ar' ? 'ar-SA' : 
                       lang === 'ru' ? 'ru-RU' :
                       lang === 'de' ? 'de-DE' :
                       lang === 'en' ? 'en-US' : 'tr-TR';
        
        return new Intl.NumberFormat(locale, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(tutar || 0) + ' ₺';
    },

    tarihFormat: (tarih) => {
        if (!tarih) return '-';
        const lang = getStoredLanguage();
        const tz = getStoredTimezone();
        const locale = lang === 'ar' ? 'ar-SA' : 
                       lang === 'ru' ? 'ru-RU' :
                       lang === 'de' ? 'de-DE' :
                       lang === 'en' ? 'en-US' : 'tr-TR';
        
        return new Date(tarih).toLocaleDateString(locale, { timeZone: tz });
    },

    saatFormat: (tarih) => {
        if (!tarih) return '-';
        const lang = getStoredLanguage();
        const tz = getStoredTimezone();
        
        return new Date(tarih).toLocaleTimeString('tr-TR', { 
            timeZone: tz,
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    tarihSaatFormat: (tarih) => {
        if (!tarih) return '-';
        const lang = getStoredLanguage();
        const tz = getStoredTimezone();
        const locale = lang === 'ar' ? 'ar-SA' : 
                       lang === 'ru' ? 'ru-RU' :
                       lang === 'de' ? 'de-DE' :
                       lang === 'en' ? 'en-US' : 'tr-TR';
        
        return new Date(tarih).toLocaleString(locale, { timeZone: tz });
    },

    kategoriGetir: (tip, kategoriId) => {
        const kategoriler = Kategoriler[tip] || [];
        return kategoriler.find(k => k.id === kategoriId) || { ad: 'Bilinmiyor', icon: 'fa-question' };
    },

    bugunTarih: () => {
        // Saat dilimine göre bugünün tarihini al
        const tz = getStoredTimezone();
        const now = new Date();
        
        // Intl.DateTimeFormat ile saat dilimine göre parçaları al
        const parts = new Intl.DateTimeFormat('en-CA', {
            timeZone: tz,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).formatToParts(now);
        
        const year = parts.find(p => p.type === 'year').value;
        const month = parts.find(p => p.type === 'month').value;
        const day = parts.find(p => p.type === 'day').value;
        
        return `${year}-${month}-${day}`;
    },

    simdikiZaman: () => {
        const tz = getStoredTimezone();
        return new Date().toLocaleString('tr-TR', { timeZone: tz });
    },

    saatDilimi: () => getStoredTimezone(),
    dil: () => getStoredLanguage()
};

// ==================== BAŞLATMA ====================
let initPromise = null;

export async function init() {
    if (initPromise) return initPromise;
    
    initPromise = (async () => {
        Toast.init();
        await initFirebase();
        
        if (!firebaseConnected) {
            showFirebaseError();
            return false;
        }
        
        window.DB = {
            isOnline,
            getMode,
            Gelirler,
            Giderler,
            Alacaklilar,
            BorcuBitenler,
            Kategoriler,
            Dashboard,
            Yardimci,
            Toast
        };
        
        return true;
    })();
    
    return initPromise;
}

// Otomatik başlat
init();

export default {
    init,
    isOnline,
    getMode,
    Gelirler,
    Giderler,
    Alacaklilar,
    BorcuBitenler,
    Kategoriler,
    Dashboard,
    Yardimci
};
