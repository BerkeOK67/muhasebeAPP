/**
 * Kişisel Muhasebe - Tarih/saat formatlama (sabit Europe/Istanbul)
 */

const TZ = 'Europe/Istanbul';

export function getTimezone() {
    return TZ;
}

export function formatDate(date, options = {}) {
    const d = date instanceof Date ? date : new Date(date);
    return d.toLocaleDateString('tr-TR', { timeZone: TZ, ...options });
}

export function formatTime(date, options = {}) {
    const d = date instanceof Date ? date : new Date(date);
    return d.toLocaleTimeString('tr-TR', { timeZone: TZ, hour: '2-digit', minute: '2-digit', second: '2-digit', ...options });
}

export function getTodayDate() {
    const now = new Date();
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(now);
    return `${parts.find(p => p.type === 'year').value}-${parts.find(p => p.type === 'month').value}-${parts.find(p => p.type === 'day').value}`;
}

export function formatMoney(amount, currency = '₺') {
    return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount || 0) + ' ' + currency;
}

window.i18n = { getTimezone, formatDate, formatTime, getTodayDate, formatMoney };
export default { getTimezone, formatDate, formatTime, getTodayDate, formatMoney };
