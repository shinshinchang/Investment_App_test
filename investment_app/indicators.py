import pandas as pd
import pandas_ta as ta


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add MA20, MA60, RSI, and Stochastic KD columns."""
    if df is None or df.empty:
        return df

    result = df.copy()
    result["MA20"] = ta.sma(result["Close"], length=20)
    result["MA60"] = ta.sma(result["Close"], length=60)
    result["RSI"] = ta.rsi(result["Close"], length=14)

    kd = ta.stoch(result["High"], result["Low"], result["Close"])
    if kd is not None and not kd.empty:
        result = result.join(kd)

    return result
