"""EMA kesishuvi + RSI filtri: Pine Script indikatorining Python versiyasi.

Tashqi kutubxonasiz ishlaydi. Ishga tushirish:  python3 ema_rsi_signal.py
"""


def ema(values, length):
    """Eksponensial o'rtacha (TradingView ta.ema bilan bir xil: SMA bilan boshlanadi)."""
    out = [None] * len(values)
    if len(values) < length:
        return out
    k = 2 / (length + 1)
    out[length - 1] = sum(values[:length]) / length
    for i in range(length, len(values)):
        out[i] = values[i] * k + out[i - 1] * (1 - k)
    return out


def rsi(values, length=14):
    """Wilder RSI (TradingView ta.rsi bilan bir xil)."""
    out = [None] * len(values)
    if len(values) <= length:
        return out
    gains = [max(values[i] - values[i - 1], 0) for i in range(1, len(values))]
    losses = [max(values[i - 1] - values[i], 0) for i in range(1, len(values))]
    avg_gain = sum(gains[:length]) / length
    avg_loss = sum(losses[:length]) / length
    for i in range(length, len(values)):
        if i > length:
            avg_gain = (avg_gain * (length - 1) + gains[i - 1]) / length
            avg_loss = (avg_loss * (length - 1) + losses[i - 1]) / length
        out[i] = 100.0 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)
    return out


def signals(closes, fast_len=9, slow_len=21, rsi_len=14, rsi_buy=50, rsi_sell=50):
    """Har bir sham uchun 'BUY', 'SELL' yoki None qaytaradi."""
    fast, slow, r = ema(closes, fast_len), ema(closes, slow_len), rsi(closes, rsi_len)
    result = [None] * len(closes)
    for i in range(1, len(closes)):
        if None in (fast[i], slow[i], fast[i - 1], slow[i - 1], r[i]):
            continue
        if fast[i - 1] <= slow[i - 1] and fast[i] > slow[i] and r[i] > rsi_buy:
            result[i] = "BUY"
        elif fast[i - 1] >= slow[i - 1] and fast[i] < slow[i] and r[i] < rsi_sell:
            result[i] = "SELL"
    return result


if __name__ == "__main__":
    import math

    # Namuna narxlar: tushish, keyin ko'tarilish, keyin yana tushish
    closes = [100 + 10 * math.sin(i / 8) for i in range(120)]
    for i, s in enumerate(signals(closes)):
        if s:
            print(f"sham {i:3d}  narx {closes[i]:7.2f}  ->  {s}")
