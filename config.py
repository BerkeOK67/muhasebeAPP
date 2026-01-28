import os
import pytz
from datetime import datetime

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
    
    @staticmethod
    def get_grouped_timezones():
        """Saat dilimlerini bölgelere göre grupla"""
        groups = {
            'Europe': [],
            'America': [],
            'Asia': [],
            'Africa': [],
            'Pacific': [],
            'Australia': [],
            'Atlantic': [],
            'Indian': [],
            'Other': []
        }
        
        for tz_name in pytz.common_timezones:
            try:
                tz = pytz.timezone(tz_name)
                now = datetime.now(tz)
                offset = now.strftime('%z')
                offset_formatted = f"UTC{offset[:3]}:{offset[3:]}" if offset else "UTC"
                
                parts = tz_name.split('/')
                region = parts[0] if len(parts) > 1 else 'Other'
                city = parts[-1].replace('_', ' ') if len(parts) > 1 else tz_name
                
                if region in groups:
                    groups[region].append({
                        'value': tz_name,
                        'city': city,
                        'offset': offset_formatted,
                        'label': f"{city} ({offset_formatted})"
                    })
                else:
                    groups['Other'].append({
                        'value': tz_name,
                        'city': city,
                        'offset': offset_formatted,
                        'label': f"{city} ({offset_formatted})"
                    })
            except:
                continue
        
        for region in groups:
            groups[region].sort(key=lambda x: x['offset'])
        
        return groups
