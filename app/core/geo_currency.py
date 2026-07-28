# app/core/geo_currency.py
"""
AEGIS-Traffic — Global Geo-Currency & Traffic Law Engine
=========================================================
Converts the searched location into the correct:
  • Country code & flag emoji
  • Currency (code, symbol, ISO 4217)
  • Speed limit (urban default, km/h)
  • Traffic fine schedule in local currency
  • Number plate format pattern

Coverage: 22 major jurisdictions spanning every continent.

Detection order:
  1. Reverse-geocode via Nominatim (online, accurate)
  2. Keyword scan of location_name string (offline fallback)
  3. Default → India (INR) when nothing matches
"""

import re
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# MASTER COUNTRY TRAFFIC CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
# Fine amounts are in LOCAL CURRENCY and are representative of actual legal
# penalties (not exact; jurisdictions vary by state/province).
#
# usd_rate: approximate 1 USD = X local units (for cross-currency display)
# ─────────────────────────────────────────────────────────────────────────────

COUNTRY_CONFIG: dict[str, dict] = {
    # ── South Asia ────────────────────────────────────────────────────────────
    "IN": {
        "name": "India", "flag": "🇮🇳",
        "currency_code": "INR", "currency_symbol": "₹", "usd_rate": 83.5,
        "speed_limit_urban": 50, "speed_limit_highway": 100,
        "drive_side": "left",
        "plate_format": "XX00 XX0000",   # State-District-Series-Number
        "plate_example": "MH12 AA1234",
        "plate_keywords": ["MH", "DL", "KA", "TN", "GJ", "UP", "RJ", "WB", "AP", "TS"],
        "fines": {
            "RED_LIGHT_JUMP":  2000,
            "WRONG_LANE":       500,
            "ILLEGAL_UTURN":   1000,
            "OVERSPEEDING":    2000,
            "NO_HELMET":       1000,
            "ILLEGAL_PARKING":  500,
            "WRONG_WAY":       5000,
            "ROAD_ACCIDENT":  10000,
            "ASSAULT_DETECTED":20000,
            "VANDALISM_DETECTED":5000,
        },
    },
    "PK": {
        "name": "Pakistan", "flag": "🇵🇰",
        "currency_code": "PKR", "currency_symbol": "Rs", "usd_rate": 278.0,
        "speed_limit_urban": 50, "speed_limit_highway": 120,
        "drive_side": "left",
        "plate_format": "XXX-000",
        "plate_example": "LEA-1234",
        "plate_keywords": ["LEA", "KHI", "LHR", "ISB", "PEW"],
        "fines": {
            "RED_LIGHT_JUMP":  1000,
            "OVERSPEEDING":    2000,
            "NO_HELMET":        500,
            "ILLEGAL_PARKING":  500,
            "WRONG_WAY":       3000,
        },
    },

    # ── East Asia ─────────────────────────────────────────────────────────────
    "JP": {
        "name": "Japan", "flag": "🇯🇵",
        "currency_code": "JPY", "currency_symbol": "¥", "usd_rate": 149.5,
        "speed_limit_urban": 40, "speed_limit_highway": 100,
        "drive_side": "left",
        "plate_format": "XX 00 XX 0000",
        "plate_example": "品川 300 あ 1234",
        "plate_keywords": ["品川", "大阪", "名古屋", "横浜", "神戸"],
        "fines": {
            "RED_LIGHT_JUMP":  90000,
            "OVERSPEEDING":    35000,
            "NO_HELMET":       50000,
            "ILLEGAL_PARKING": 15000,
            "WRONG_WAY":      100000,
        },
    },
    "CN": {
        "name": "China", "flag": "🇨🇳",
        "currency_code": "CNY", "currency_symbol": "¥", "usd_rate": 7.25,
        "speed_limit_urban": 60, "speed_limit_highway": 120,
        "drive_side": "right",
        "plate_format": "X X0000X",
        "plate_example": "京 A12345",
        "plate_keywords": ["京", "沪", "粤", "苏", "浙", "Beijing", "Shanghai", "Guangzhou"],
        "fines": {
            "RED_LIGHT_JUMP":  200,
            "OVERSPEEDING":    500,
            "NO_HELMET":       200,
            "ILLEGAL_PARKING": 200,
            "WRONG_WAY":      1000,
        },
    },
    "KR": {
        "name": "South Korea", "flag": "🇰🇷",
        "currency_code": "KRW", "currency_symbol": "₩", "usd_rate": 1330.0,
        "speed_limit_urban": 50, "speed_limit_highway": 110,
        "drive_side": "right",
        "plate_format": "00X 0000",
        "plate_example": "12가 3456",
        "plate_keywords": ["Seoul", "Busan", "Incheon", "Daegu", "서울", "부산"],
        "fines": {
            "RED_LIGHT_JUMP":  70000,
            "OVERSPEEDING":    60000,
            "NO_HELMET":       20000,
            "ILLEGAL_PARKING": 40000,
            "WRONG_WAY":      130000,
        },
    },

    # ── Southeast Asia ────────────────────────────────────────────────────────
    "SG": {
        "name": "Singapore", "flag": "🇸🇬",
        "currency_code": "SGD", "currency_symbol": "S$", "usd_rate": 1.35,
        "speed_limit_urban": 50, "speed_limit_highway": 90,
        "drive_side": "left",
        "plate_format": "XXX 0000 X",
        "plate_example": "SBA 1234 A",
        "plate_keywords": ["Singapore", "Orchard", "Changi", "Sentosa"],
        "fines": {
            "RED_LIGHT_JUMP":   500,
            "OVERSPEEDING":     200,
            "NO_HELMET":        150,
            "ILLEGAL_PARKING":  100,
            "WRONG_WAY":       1000,
        },
    },
    "MY": {
        "name": "Malaysia", "flag": "🇲🇾",
        "currency_code": "MYR", "currency_symbol": "RM", "usd_rate": 4.70,
        "speed_limit_urban": 50, "speed_limit_highway": 110,
        "drive_side": "left",
        "plate_format": "XXX 0000",
        "plate_example": "WXY 1234",
        "plate_keywords": ["Kuala Lumpur", "Penang", "Johor", "Malacca", "Malaysia"],
        "fines": {
            "RED_LIGHT_JUMP":  300,
            "OVERSPEEDING":    300,
            "NO_HELMET":       150,
            "ILLEGAL_PARKING": 100,
            "WRONG_WAY":       500,
        },
    },

    # ── Middle East ───────────────────────────────────────────────────────────
    "AE": {
        "name": "United Arab Emirates", "flag": "🇦🇪",
        "currency_code": "AED", "currency_symbol": "د.إ", "usd_rate": 3.67,
        "speed_limit_urban": 60, "speed_limit_highway": 140,
        "drive_side": "right",
        "plate_format": "X 00000",
        "plate_example": "Dubai A 12345",
        "plate_keywords": ["Dubai", "Abu Dhabi", "Sharjah", "UAE", "Emirates", "Sheikh Zayed"],
        "fines": {
            "RED_LIGHT_JUMP": 1000,
            "OVERSPEEDING":    600,
            "NO_HELMET":       500,
            "ILLEGAL_PARKING": 500,
            "WRONG_WAY":      3000,
        },
    },
    "SA": {
        "name": "Saudi Arabia", "flag": "🇸🇦",
        "currency_code": "SAR", "currency_symbol": "﷼", "usd_rate": 3.75,
        "speed_limit_urban": 60, "speed_limit_highway": 120,
        "drive_side": "right",
        "plate_format": "X 000 XXX",
        "plate_example": "A 123 BCD",
        "plate_keywords": ["Riyadh", "Jeddah", "Mecca", "Medina", "Saudi"],
        "fines": {
            "RED_LIGHT_JUMP": 1000,
            "OVERSPEEDING":    600,
            "NO_HELMET":       300,
            "ILLEGAL_PARKING": 200,
            "WRONG_WAY":      2000,
        },
    },

    # ── Europe ────────────────────────────────────────────────────────────────
    "GB": {
        "name": "United Kingdom", "flag": "🇬🇧",
        "currency_code": "GBP", "currency_symbol": "£", "usd_rate": 0.79,
        "speed_limit_urban": 48, "speed_limit_highway": 112,   # 30/70 mph
        "drive_side": "left",
        "plate_format": "XX00 XXX",
        "plate_example": "AB12 CDE",
        "plate_keywords": ["London", "Manchester", "Birmingham", "Leeds", "Edinburgh",
                           "Trafalgar", "Oxford", "Cambridge", "UK", "Britain", "England", "Scotland", "Wales"],
        "fines": {
            "RED_LIGHT_JUMP": 100,
            "OVERSPEEDING":   100,
            "NO_HELMET":      100,
            "ILLEGAL_PARKING": 70,
            "WRONG_WAY":      2500,
        },
    },
    "DE": {
        "name": "Germany", "flag": "🇩🇪",
        "currency_code": "EUR", "currency_symbol": "€", "usd_rate": 0.92,
        "speed_limit_urban": 50, "speed_limit_highway": 130,   # recommended; Autobahn sections unlimited
        "drive_side": "right",
        "plate_format": "XXX XX 0000",
        "plate_example": "B AB 1234",
        "plate_keywords": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Stuttgart",
                           "Germany", "Deutschland", "Bayern", "Autobahn"],
        "fines": {
            "RED_LIGHT_JUMP":  200,
            "OVERSPEEDING":    120,
            "NO_HELMET":        65,
            "ILLEGAL_PARKING":  55,
            "WRONG_WAY":       600,
        },
    },
    "FR": {
        "name": "France", "flag": "🇫🇷",
        "currency_code": "EUR", "currency_symbol": "€", "usd_rate": 0.92,
        "speed_limit_urban": 50, "speed_limit_highway": 130,
        "drive_side": "right",
        "plate_format": "XX-000-XX",
        "plate_example": "AB-123-CD",
        "plate_keywords": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice",
                           "Arc de Triomphe", "Eiffel", "France", "French"],
        "fines": {
            "RED_LIGHT_JUMP": 135,
            "OVERSPEEDING":   135,
            "NO_HELMET":       135,
            "ILLEGAL_PARKING": 35,
            "WRONG_WAY":      750,
        },
    },
    "IT": {
        "name": "Italy", "flag": "🇮🇹",
        "currency_code": "EUR", "currency_symbol": "€", "usd_rate": 0.92,
        "speed_limit_urban": 50, "speed_limit_highway": 130,
        "drive_side": "right",
        "plate_format": "XX 000 XX",
        "plate_example": "AB 123 CD",
        "plate_keywords": ["Rome", "Milan", "Venice", "Florence", "Naples",
                           "Roma", "Milano", "Italy", "Italia", "Colosseum"],
        "fines": {
            "RED_LIGHT_JUMP": 167,
            "OVERSPEEDING":   167,
            "NO_HELMET":       100,
            "ILLEGAL_PARKING": 41,
            "WRONG_WAY":      500,
        },
    },
    "ES": {
        "name": "Spain", "flag": "🇪🇸",
        "currency_code": "EUR", "currency_symbol": "€", "usd_rate": 0.92,
        "speed_limit_urban": 50, "speed_limit_highway": 120,
        "drive_side": "right",
        "plate_format": "0000 XXX",
        "plate_example": "1234 ABC",
        "plate_keywords": ["Madrid", "Barcelona", "Seville", "Valencia", "Bilbao",
                           "Spain", "España", "Sagrada"],
        "fines": {
            "RED_LIGHT_JUMP": 200,
            "OVERSPEEDING":   100,
            "NO_HELMET":       100,
            "ILLEGAL_PARKING": 80,
            "WRONG_WAY":       500,
        },
    },
    "RU": {
        "name": "Russia", "flag": "🇷🇺",
        "currency_code": "RUB", "currency_symbol": "₽", "usd_rate": 90.0,
        "speed_limit_urban": 60, "speed_limit_highway": 110,
        "drive_side": "right",
        "plate_format": "X 000 XX 00",
        "plate_example": "А 123 ВС 77",
        "plate_keywords": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg",
                           "Russia", "Россия", "Kremlin", "Red Square"],
        "fines": {
            "RED_LIGHT_JUMP": 1000,
            "OVERSPEEDING":    500,
            "NO_HELMET":       500,
            "ILLEGAL_PARKING": 500,
            "WRONG_WAY":      5000,
        },
    },

    # ── Americas ──────────────────────────────────────────────────────────────
    "US": {
        "name": "United States", "flag": "🇺🇸",
        "currency_code": "USD", "currency_symbol": "$", "usd_rate": 1.0,
        "speed_limit_urban": 40, "speed_limit_highway": 105,   # varies by state
        "drive_side": "right",
        "plate_format": "XXX 0000",
        "plate_example": "ABC 1234",
        "plate_keywords": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
                           "Times Square", "Broadway", "Manhattan", "Brooklyn",
                           "USA", "United States", "America", "California", "Texas",
                           "Florida", "Las Vegas", "San Francisco", "Boston", "Seattle"],
        "fines": {
            "RED_LIGHT_JUMP": 250,
            "OVERSPEEDING":   150,
            "NO_HELMET":      100,
            "ILLEGAL_PARKING": 65,
            "WRONG_WAY":      500,
            "ROAD_ACCIDENT":  1500,
        },
    },
    "CA": {
        "name": "Canada", "flag": "🇨🇦",
        "currency_code": "CAD", "currency_symbol": "C$", "usd_rate": 1.36,
        "speed_limit_urban": 50, "speed_limit_highway": 100,
        "drive_side": "right",
        "plate_format": "XXX 000",
        "plate_example": "ABC 123",
        "plate_keywords": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa",
                           "Canada", "Ontario", "British Columbia", "Quebec"],
        "fines": {
            "RED_LIGHT_JUMP": 325,
            "OVERSPEEDING":   150,
            "NO_HELMET":       115,
            "ILLEGAL_PARKING":  60,
            "WRONG_WAY":       500,
        },
    },
    "BR": {
        "name": "Brazil", "flag": "🇧🇷",
        "currency_code": "BRL", "currency_symbol": "R$", "usd_rate": 4.97,
        "speed_limit_urban": 60, "speed_limit_highway": 110,
        "drive_side": "right",
        "plate_format": "XXX-0000",
        "plate_example": "ABC-1234",
        "plate_keywords": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador",
                           "Brazil", "Brasil", "Copacabana", "Carnival"],
        "fines": {
            "RED_LIGHT_JUMP":  293,
            "OVERSPEEDING":    195,
            "NO_HELMET":       195,
            "ILLEGAL_PARKING":  88,
            "WRONG_WAY":       880,
        },
    },

    # ── Africa ────────────────────────────────────────────────────────────────
    "ZA": {
        "name": "South Africa", "flag": "🇿🇦",
        "currency_code": "ZAR", "currency_symbol": "R", "usd_rate": 18.6,
        "speed_limit_urban": 60, "speed_limit_highway": 120,
        "drive_side": "left",
        "plate_format": "XXX 000 XX",
        "plate_example": "CAA 123 GP",
        "plate_keywords": ["Johannesburg", "Cape Town", "Durban", "Pretoria",
                           "South Africa", "Soweto", "Table Mountain"],
        "fines": {
            "RED_LIGHT_JUMP": 1500,
            "OVERSPEEDING":   1000,
            "NO_HELMET":       500,
            "ILLEGAL_PARKING": 500,
            "WRONG_WAY":      3000,
        },
    },
    "NG": {
        "name": "Nigeria", "flag": "🇳🇬",
        "currency_code": "NGN", "currency_symbol": "₦", "usd_rate": 1550.0,
        "speed_limit_urban": 50, "speed_limit_highway": 100,
        "drive_side": "right",
        "plate_format": "XXX-000XX",
        "plate_example": "ABC-123DE",
        "plate_keywords": ["Lagos", "Abuja", "Kano", "Ibadan", "Nigeria"],
        "fines": {
            "RED_LIGHT_JUMP": 10000,
            "OVERSPEEDING":   10000,
            "NO_HELMET":       2000,
            "ILLEGAL_PARKING": 5000,
            "WRONG_WAY":      20000,
        },
    },

    # ── Oceania ───────────────────────────────────────────────────────────────
    "AU": {
        "name": "Australia", "flag": "🇦🇺",
        "currency_code": "AUD", "currency_symbol": "A$", "usd_rate": 1.53,
        "speed_limit_urban": 50, "speed_limit_highway": 110,
        "drive_side": "left",
        "plate_format": "XXX 000",
        "plate_example": "ABC 123",
        "plate_keywords": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide",
                           "Australia", "NSW", "Victoria", "Queensland", "Harbour Bridge",
                           "Opera House"],
        "fines": {
            "RED_LIGHT_JUMP": 433,
            "OVERSPEEDING":   270,
            "NO_HELMET":      319,
            "ILLEGAL_PARKING": 110,
            "WRONG_WAY":      935,
        },
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT (fallback when no country match)
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULT_COUNTRY = "IN"


# ─────────────────────────────────────────────────────────────────────────────
# DETECTION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _keyword_detect(location_name: str) -> Optional[str]:
    """Scan location_name string against each country's keyword list."""
    loc_lower = location_name.lower()
    # Sort by keyword length descending so more specific keywords win
    candidates = []
    for cc, cfg in COUNTRY_CONFIG.items():
        for kw in cfg.get("plate_keywords", []) + [cfg["name"]]:
            if kw.lower() in loc_lower:
                candidates.append((len(kw), cc))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None


def _nominatim_detect(lat: float, lon: float, timeout: int = 4) -> Optional[str]:
    """
    Reverse-geocode lat/lon using Nominatim to get ISO country code.
    Returns 2-letter ISO code or None on failure.
    """
    try:
        import requests as _req
        r = _req.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "zoom": 5},
            headers={"User-Agent": "AegisMHR/7.0"},
            timeout=timeout,
        )
        if r.ok:
            cc = r.json().get("address", {}).get("country_code", "").upper()
            if cc in COUNTRY_CONFIG:
                return cc
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def detect_country(
    location_name: str = "",
    lat: float = 0.0,
    lon: float = 0.0,
    try_nominatim: bool = True,
) -> str:
    """
    Detect ISO country code from location context.

    Priority:
      1. Reverse-geocode via Nominatim  (accurate, needs network)
      2. Keyword scan of location_name  (offline, fast)
      3. Default → 'IN'

    Returns:
        2-letter ISO country code (always a key in COUNTRY_CONFIG).
    """
    if try_nominatim and (lat != 0.0 or lon != 0.0):
        cc = _nominatim_detect(lat, lon)
        if cc:
            return cc

    cc = _keyword_detect(location_name)
    if cc:
        return cc

    return _DEFAULT_COUNTRY


def get_country_config(country_code: str) -> dict:
    """Return the full config dict for a country code, defaulting to India."""
    return COUNTRY_CONFIG.get(country_code, COUNTRY_CONFIG[_DEFAULT_COUNTRY])


def get_fine(violation_type: str, country_code: str) -> int:
    """
    Return the fine amount in local currency for a given violation type.
    Falls back to India if the country has no entry for that violation.
    """
    cfg = get_country_config(country_code)
    fines = cfg.get("fines", {})
    # Try exact key, then fallback to India's schedule
    if violation_type in fines:
        return fines[violation_type]
    india_fines = COUNTRY_CONFIG["IN"]["fines"]
    # Scale India's fine to local currency (approximate)
    inr_amount = india_fines.get(violation_type, 0)
    usd_value  = inr_amount / COUNTRY_CONFIG["IN"]["usd_rate"]
    return round(usd_value * cfg["usd_rate"])


def format_fine(amount: int, country_code: str) -> str:
    """Return a formatted fine string with local currency symbol."""
    cfg = get_country_config(country_code)
    sym = cfg["currency_symbol"]
    cod = cfg["currency_symbol"]

    # Use comma formatting for amounts ≥ 1000
    amt_str = f"{amount:,}"
    return f"{sym}{amt_str}"


def format_fine_with_usd(amount: int, country_code: str) -> dict:
    """
    Return fine in both local currency AND approximate USD equivalent.
    Used for cross-country comparison displays.
    """
    cfg      = get_country_config(country_code)
    usd_rate = cfg["usd_rate"]
    usd_val  = round(amount / usd_rate, 2)
    return {
        "local_amount":    amount,
        "local_formatted": format_fine(amount, country_code),
        "currency_code":   cfg["currency_code"],
        "currency_symbol": cfg["currency_symbol"],
        "usd_equivalent":  usd_val,
        "usd_formatted":   f"≈ ${usd_val:,.2f}",
    }


def get_plate_pool(country_code: str) -> list[str]:
    """
    Return a pool of realistic plate strings for the given country,
    used by the ANPR module for simulated OCR output.
    """
    import random
    cfg = get_country_config(country_code)
    fmt = cfg.get("plate_format", "XX 0000")
    kws = cfg.get("plate_keywords", ["AB"])

    def _make_plate() -> str:
        s = fmt
        # Replace X with letter, 0 with digit, keep space/hyphen/dash
        result = []
        letter_pool = kws[0][:2].upper() if kws else "AB"
        for ch in s:
            if ch == "X":
                result.append(random.choice("ABCDEFGHJKLMNPRSTUVWXYZ"))
            elif ch == "0":
                result.append(str(random.randint(0, 9)))
            else:
                result.append(ch)
        return "".join(result)

    # Generate 12 unique plates
    plates = []
    seen = set()
    attempts = 0
    while len(plates) < 12 and attempts < 100:
        p = _make_plate()
        if p not in seen:
            plates.append(p)
            seen.add(p)
        attempts += 1
    return plates
