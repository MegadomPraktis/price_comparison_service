# utils/helpers.py

def safe_float(value):
    try:
        if isinstance(value, str):
            value = value.replace(",", ".")
            if value.strip().upper() == "N/A":
                return 0.0
        return float(value)
    except Exception:
        return 0.0
