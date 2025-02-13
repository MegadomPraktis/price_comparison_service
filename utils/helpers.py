# utils/helpers.py

def safe_float(value):
    """
    Converts a string value to a float.
    - Removes all whitespace.
    - Replaces commas with dots.
    - If the value is "N/A" (case-insensitive) or conversion fails, returns 0.0.
    """
    try:
        if isinstance(value, str):
            # Remove all whitespace (e.g., "1 400" becomes "1400")
            value = ''.join(value.split())
            # Replace commas with dots
            value = value.replace(",", ".")
            if value.strip().upper() == "N/A":
                return 0.0
        return float(value)
    except Exception:
        return 0.0
