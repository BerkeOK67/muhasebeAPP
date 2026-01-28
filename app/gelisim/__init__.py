# Gelişim - Aylık / yıllık gelir, gider, net kâr grafikleri
from flask import Blueprint, send_file, Response
from io import BytesIO

from app.firebase_admin import get_collection

bp = Blueprint('gelisim', __name__, url_prefix='/gelisim')


def _parse_float(x, default=0.0):
    try:
        return float(x) if x is not None else default
    except (TypeError, ValueError):
        return default


def _gider_aylik_taksit(gider, yil, ay):
    """Taksitli giderde o aya düşen taksit tutarını döner."""
    if not gider.get('taksitli'):
        return 0.0
    ilk = gider.get('ilk_taksit_tarihi') or gider.get('tarih')
    if not ilk:
        return 0.0
    try:
        from datetime import datetime
        if isinstance(ilk, str):
            ilk = datetime.fromisoformat(ilk.replace('Z', '+00:00'))
        else:
            ilk = ilk
        if hasattr(ilk, 'year'):
            pass
        else:
            ilk = datetime.fromisoformat(str(ilk)[:10])
    except Exception:
        return 0.0
    ay_farki = (yil - ilk.year) * 12 + (ay - (ilk.month if hasattr(ilk, 'month') else 1))
    taksit_sayisi = max(1, int(gider.get('taksit_sayisi') or 1))
    aylik = _parse_float(gider.get('aylik_taksit')) or (_parse_float(gider.get('tutar')) / taksit_sayisi)
    if 0 <= ay_farki < taksit_sayisi:
        return aylik
    return 0.0


def _gider_yillik_toplam(gider, yil):
    """Taksitli: o yıla kadar ödenen taksitler; değilse o yıldaki tek seferlik tutar."""
    from datetime import datetime
    tutar = _parse_float(gider.get('tutar'))
    if not gider.get('taksitli'):
        t = gider.get('tarih')
        if not t:
            return 0.0
        try:
            if isinstance(t, str):
                dt = datetime.fromisoformat(t.replace('Z', '+00:00')[:10])
            else:
                dt = t
            y = dt.year if hasattr(dt, 'year') else int(str(t)[:4])
            return tutar if y == yil else 0.0
        except Exception:
            return 0.0
    ilk = gider.get('ilk_taksit_tarihi') or gider.get('tarih')
    if not ilk:
        return 0.0
    try:
        if isinstance(ilk, str):
            ilk_dt = datetime.fromisoformat(ilk.replace('Z', '+00:00')[:10])
        else:
            ilk_dt = ilk
        y0 = ilk_dt.year if hasattr(ilk_dt, 'year') else int(str(ilk)[:4])
        m0 = ilk_dt.month if hasattr(ilk_dt, 'month') else 1
    except Exception:
        return 0.0
    taksit_sayisi = max(1, int(gider.get('taksit_sayisi') or 1))
    aylik = _parse_float(gider.get('aylik_taksit')) or (tutar / taksit_sayisi)
    # yil sonuna kadar ödenen taksit sayısı
    ay_farki = (yil - y0) * 12 + (12 - m0 + 1)
    odenen = min(max(0, ay_farki), taksit_sayisi)
    return odenen * aylik


def _aylik_veriler():
    from datetime import date, timedelta
    simdi = date.today()
    gelirler = get_collection('gelirler')
    giderler = get_collection('giderler')
    aylar, g, d, n = [], [], [], []
    ay_ad = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
    for i in range(11, -1, -1):
        y, m = simdi.year, simdi.month - i
        while m <= 0:
            m += 12
            y -= 1
        ay_bas = date(y, m, 1)
        if m == 12:
            ay_son = date(y, 12, 31)
        else:
            ay_son = date(y, m + 1, 1) - timedelta(days=1)
        gelir = sum(_parse_float(x.get('tutar')) for x in gelirler
                    if x.get('tarih') and _tarih_in_range(x['tarih'], ay_bas, ay_son))
        gider = 0.0
        for x in giderler:
            if x.get('taksitli'):
                gider += _gider_aylik_taksit(x, y, m)
            else:
                if x.get('tarih') and _tarih_in_range(x['tarih'], ay_bas, ay_son):
                    gider += _parse_float(x.get('tutar'))
        net = gelir - gider
        aylar.append(f"{ay_ad[m - 1]} {y}")
        g.append(gelir)
        d.append(gider)
        n.append(net)
    return aylar, g, d, n


def _tarih_in_range(t, bas, son):
    from datetime import datetime, date
    try:
        if isinstance(t, str):
            dt = datetime.fromisoformat(t.replace('Z', '+00:00')[:10]).date()
        else:
            dt = t if isinstance(t, date) else datetime.fromisoformat(str(t)[:10]).date()
        return bas <= dt <= son
    except Exception:
        return False


def _yillik_veriler():
    from datetime import date
    simdi = date.today()
    gelirler = get_collection('gelirler')
    giderler = get_collection('giderler')
    yillar = []
    g = []
    d = []
    n = []
    for i in range(4, -1, -1):
        y = simdi.year - i
        gelir = sum(_parse_float(x.get('tutar')) for x in gelirler
                    if x.get('tarih') and _yil_icinde(x['tarih'], y))
        gider = sum(_gider_yillik_toplam(x, y) for x in giderler)
        net = gelir - gider
        yillar.append(str(y))
        g.append(gelir)
        d.append(gider)
        n.append(net)
    return yillar, g, d, n


def _yil_icinde(t, yil):
    from datetime import datetime, date
    try:
        if isinstance(t, str):
            dt = datetime.fromisoformat(t.replace('Z', '+00:00')[:10])
        else:
            dt = t
        y = dt.year if hasattr(dt, 'year') else int(str(t)[:4])
        return y == yil
    except Exception:
        return False


def _chart_aylik_png():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = 'DejaVu Sans'
    ay, gelir, gider, net = _aylik_veriler()
    x = range(len(ay))
    w = 0.25
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar([i - w for i in x], gelir, width=w, label='Gelir', color='#10b981')
    ax.bar(x, gider, width=w, label='Gider', color='#ef4444')
    ax.bar([i + w for i in x], net, width=w, label='Net kâr', color='#3b82f6')
    ax.set_xticks(x)
    ax.set_xticklabels(ay, rotation=45, ha='right')
    ax.set_ylabel('Tutar (₺)')
    ax.set_title('Aylık gelir, gider ve net kâr')
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:,.0f} ₺'))
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def _chart_yillik_png():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.rcParams['font.family'] = 'DejaVu Sans'
    yil, gelir, gider, net = _yillik_veriler()
    x = range(len(yil))
    w = 0.25
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - w for i in x], gelir, width=w, label='Gelir', color='#10b981')
    ax.bar(x, gider, width=w, label='Gider', color='#ef4444')
    ax.bar([i + w for i in x], net, width=w, label='Net kâr', color='#3b82f6')
    ax.set_xticks(x)
    ax.set_xticklabels(yil)
    ax.set_ylabel('Tutar (₺)')
    ax.set_title('Yıllık gelir, gider ve net kâr')
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:,.0f} ₺'))
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


@bp.route('/')
def index():
    from flask import render_template
    return render_template('gelisim/index.html')


@bp.route('/chart/aylik')
def chart_aylik():
    try:
        buf = _chart_aylik_png()
        return send_file(buf, mimetype='image/png', download_name='aylik.png')
    except Exception:
        from flask import Response
        return Response(status=500)


@bp.route('/chart/yillik')
def chart_yillik():
    try:
        buf = _chart_yillik_png()
        return send_file(buf, mimetype='image/png', download_name='yillik.png')
    except Exception:
        from flask import Response
        return Response(status=500)
