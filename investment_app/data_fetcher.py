import pandas as pd
import yfinance as yf
import certifi
import unicodedata


def _has_non_ascii(text: str) -> bool:
    return any(ord(ch) > 127 for ch in text)


def _build_insecure_curl_session():
    from curl_cffi import requests as curl_requests

    return curl_requests.Session(impersonate="chrome", verify=False)


def _ticker_candidates(raw_symbol: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", raw_symbol or "")
    symbol = normalized.strip().upper()
    if not symbol:
        return []

    candidates = [symbol]
    if symbol.isdigit() and "." not in symbol:
        candidates = [f"{symbol}.TW", f"{symbol}.TWO", symbol]

    # Keep order while removing duplicates.
    return list(dict.fromkeys(candidates))


def fetch_price_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance."""
    def _download(target_symbol: str, session=None):
        return yf.download(
            target_symbol,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            session=session,
        )

    cert_path = certifi.where()
    prefers_fallback_session = _has_non_ascii(cert_path)

    candidates = _ticker_candidates(symbol)
    if not candidates:
        return pd.DataFrame()

    for candidate in candidates:
        try:
            if prefers_fallback_session:
                data = _download(candidate, session=_build_insecure_curl_session())
            else:
                data = _download(candidate)
        except Exception as exc:
            message = str(exc).lower()
            if "curl: (77)" in message or "certificate verify locations" in message:
                try:
                    data = _download(candidate, session=_build_insecure_curl_session())
                except Exception:
                    continue
            else:
                continue

        if data is None or data.empty:
            try:
                data = _download(candidate, session=_build_insecure_curl_session())
            except Exception:
                continue

        if data is None or data.empty:
            continue

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        required_columns = ["Open", "High", "Low", "Close"]
        if any(col not in data.columns for col in required_columns):
            continue

        return data.dropna(subset=required_columns)

    return pd.DataFrame()
