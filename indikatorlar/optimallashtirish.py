"""Indikatorni tarixiy ma'lumotda "o'qitish": eng yaxshi sozlamalarni qidirish.

Ma'lumotni 2 qismga bo'ladi:
  - o'qitish (train, 70%) — sozlamalar shu qismda tanlanadi;
  - sinov (test, 30%)     — tanlangan sozlamalar ko'rmagan ma'lumotda tekshiriladi.
Sinovdagi natija o'qitishdagidan ancha yomon bo'lsa — bu overfitting belgisi.

Ishga tushirish:
  python3 optimallashtirish.py narxlar.csv   # 'close' ustunli CSV (TradingView/Binance eksporti)
  python3 optimallashtirish.py               # namunaviy (tasodifiy) ma'lumot bilan
"""

import csv
import random
import sys

from ema_rsi_signal import signals


def load_closes(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    key = next(k for k in rows[0] if k.strip().lower() == "close")
    return [float(r[key]) for r in rows if r[key]]


def sample_closes(n=3000, seed=42):
    random.seed(seed)
    price, out, drift = 100.0, [], 0.0
    for i in range(n):
        if i % 200 == 0:
            drift = random.uniform(-0.002, 0.002)  # vaqti-vaqti bilan trend o'zgaradi
        price *= 1 + drift + random.gauss(0, 0.01)
        out.append(price)
    return out


def backtest(closes, fee=0.001, **params):
    """Faqat long: BUY da kiradi, SELL da chiqadi. Natija: (umumiy foyda %, savdolar soni)."""
    equity, entry, trades = 1.0, None, 0
    for i, s in enumerate(signals(closes, **params)):
        if s == "BUY" and entry is None:
            entry = closes[i]
        elif s == "SELL" and entry is not None:
            equity *= closes[i] / entry * (1 - fee) ** 2
            entry, trades = None, trades + 1
    if entry is not None:
        equity *= closes[-1] / entry * (1 - fee) ** 2
        trades += 1
    return (equity - 1) * 100, trades


def grid():
    for fast in range(5, 21, 3):
        for slow in range(20, 61, 10):
            for rsi_buy in (40, 50, 60):
                yield {"fast_len": fast, "slow_len": slow, "rsi_buy": rsi_buy, "rsi_sell": 100 - rsi_buy}


def main():
    closes = load_closes(sys.argv[1]) if len(sys.argv) > 1 else sample_closes()
    split = int(len(closes) * 0.7)
    train, test = closes[:split], closes[split:]
    print(f"Jami {len(closes)} sham: o'qitish {len(train)}, sinov {len(test)}\n")

    results = []
    for p in grid():
        profit, trades = backtest(train, **p)
        if trades >= 5:  # juda kam savdo — tasodif bo'lishi mumkin
            results.append((profit, trades, p))
    results.sort(key=lambda r: r[0], reverse=True)

    print("Eng yaxshi 5 ta sozlama (o'qitish -> sinov):")
    for profit, trades, p in results[:5]:
        test_profit, test_trades = backtest(test, **p)
        print(f"  {p}\n     o'qitish: {profit:7.2f}% ({trades} savdo) | sinov: {test_profit:7.2f}% ({test_trades} savdo)")

    default = {"fast_len": 9, "slow_len": 21, "rsi_buy": 50, "rsi_sell": 50}
    print(f"\nStandart {default}: sinov {backtest(test, **default)[0]:.2f}%")
    print(f"Shunchaki sotib olib ushlab turish (sinov): {(test[-1] / test[0] - 1) * 100:.2f}%")


if __name__ == "__main__":
    main()
