import pandas as pd


def rsi(closes: pd.Series, period: int) -> pd.Series:
    """
    :param closes: A pandas Series of closing prices.
    :param period: The number of periods to use for the RSI calculation.
    :return: A pandas Series containing the RSI values.
    """
    if not isinstance(period, int) or period <= 1:
        raise ValueError("Period must be an integer greater than 1.")

    if not isinstance(closes, pd.Series):
        raise TypeError("Input 'closes' must be a pandas Series.")

    if len(closes) < period + 1:
        raise ValueError(f"Insufficient data: closes length ({len(closes)}) must be >= period + 1 ({period + 1}).")

    if closes.isna().all():
        raise ValueError("Input 'closes' contain only NaN values.")

    delta = closes.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    alpha = 1.0 / period

    avg_gain = gain.ewm(alpha=alpha, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False, min_periods=period).mean()

    return (100.0 * avg_gain / (avg_gain + avg_loss)).fillna(50.0)
