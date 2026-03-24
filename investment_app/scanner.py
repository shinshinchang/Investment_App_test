import pandas as pd


def detect_ma_golden_cross(df: pd.DataFrame, short_col: str = "MA20", long_col: str = "MA60") -> bool:
    """Return True when short MA crosses above long MA on the latest bar."""
    if df is None or len(df) < 2:
        return False

    if short_col not in df.columns or long_col not in df.columns:
        return False

    prev_row = df.iloc[-2]
    last_row = df.iloc[-1]

    return prev_row[short_col] < prev_row[long_col] and last_row[short_col] > last_row[long_col]
