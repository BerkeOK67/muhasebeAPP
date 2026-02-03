"""
Kişisel Muhasebe - Masaüstü başlatıcı.
EXE yapıldığında çalıştırılır; sunucuyu başlatır ve tarayıcıyı açar.
"""
import sys
import threading
import time
import webbrowser

# Port sabit; EXE içinde çalışırken aynı port kullanılır
PORT = 5001
URL = f"http://127.0.0.1:{PORT}"


def open_browser():
    time.sleep(1.2)
    webbrowser.open(URL)


def main():
    # Tarayıcıyı kısa gecikmeyle aç (sunucu ayağa kalksın)
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    from app import create_app
    app = create_app()

    # EXE / tek kullanıcı: Waitress ile production benzeri sunucu (PyInstaller ile paketlenince)
    try:
        from waitress import serve
        serve(app, host="127.0.0.1", port=PORT, threads=4)
    except ImportError:
        app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
    sys.exit(0)
