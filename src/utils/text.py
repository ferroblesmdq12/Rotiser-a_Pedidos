def safe_str(x) -> str:
    return "" if x is None else str(x).strip()
