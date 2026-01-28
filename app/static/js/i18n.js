/**
 * Kişisel Muhasebe - Saat Dilimi Modülü
 */

let currentTimezone = localStorage.getItem('kisiselmuhasebe_timezone') || 'Europe/Istanbul';

// Saat dilimi değiştirme
export function setTimezone(tz) {
    currentTimezone = tz;
    localStorage.setItem('kisiselmuhasebe_timezone', tz);
    fetch(`/set-timezone/${tz}`);
    window.dispatchEvent(new CustomEvent('timezone-change', { detail: { timezone: tz } }));
    return true;
}

export function getTimezone() {
    return currentTimezone;
}

// Tarih formatla
export function formatDate(date, options = {}) {
    const d = date instanceof Date ? date : new Date(date);
    return d.toLocaleDateString('tr-TR', { timeZone: currentTimezone, ...options });
}

// Saat formatla
export function formatTime(date, options = {}) {
    const d = date instanceof Date ? date : new Date(date);
    return d.toLocaleTimeString('tr-TR', { timeZone: currentTimezone, hour: '2-digit', minute: '2-digit', second: '2-digit', ...options });
}

// Bugünün tarihi
export function getTodayDate() {
    const now = new Date();
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: currentTimezone, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(now);
    return `${parts.find(p => p.type === 'year').value}-${parts.find(p => p.type === 'month').value}-${parts.find(p => p.type === 'day').value}`;
}

// Para formatla
export function formatMoney(amount, currency = '₺') {
    return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount || 0) + ' ' + currency;
}

// Global erişim
window.i18n = { setTimezone, getTimezone, formatDate, formatTime, getTodayDate, formatMoney };

export default { setTimezone, getTimezone, formatDate, formatTime, getTodayDate, formatMoney };
