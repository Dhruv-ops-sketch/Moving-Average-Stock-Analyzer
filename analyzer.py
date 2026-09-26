import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


class CrossoverAnalyzer:
    def __init__(self, ticker, short_window=20, long_window=50):
        if short_window <= 0 or long_window <= 0:
            raise ValueError("windows have to be positive")
        if short_window >= long_window:
            raise ValueError("short window should be smaller than the long window")

        self.ticker = ticker.upper()
        self.short_window = short_window
        self.long_window = long_window
        self.data = None

    def load_prices(self, start, end):
        df = yf.download(self.ticker, start=start, end=end,
                         progress=False, auto_adjust=True)
        if df.empty:
            raise ValueError(f"couldn't get any data for {self.ticker}")

        close = df["Close"]
        # newer versions of yfinance give back a dataframe instead of a series
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        self.set_prices(close)

    def set_prices(self, prices):
        # also used by the tests so they don't need internet
        self.data = pd.DataFrame({"Close": prices})

    def compute_averages(self):
        if self.data is None:
            raise RuntimeError("load prices first")
        if len(self.data) < self.long_window:
            raise ValueError(f"need at least {self.long_window} days of data")

        self.data["SMA_short"] = self.data["Close"].rolling(self.short_window).mean()
        self.data["SMA_long"] = self.data["Close"].rolling(self.long_window).mean()

    def find_crossovers(self):
        if "SMA_short" not in self.data:
            self.compute_averages()

        short = self.data["SMA_short"]
        long = self.data["SMA_long"]

        # 1 if short avg is above long avg, 0 if not.
        # diff() then gives +1 on the day it crosses up and -1 when it crosses down
        above = (short > long).astype(int)
        change = above.diff()

        # ignore the first few days where the long average doesn't exist yet
        change[long.isna() | long.shift(1).isna()] = 0

        self.data["Signal"] = change.fillna(0).astype(int)
        return self.data[self.data["Signal"] != 0]

    def plot(self, save_path=None):
        if "Signal" not in self.data:
            self.find_crossovers()

        d = self.data
        buys = d[d["Signal"] == 1]
        sells = d[d["Signal"] == -1]

        plt.figure(figsize=(12, 6))
        plt.plot(d.index, d["Close"], label="Close", color="gray", alpha=0.6)
        plt.plot(d.index, d["SMA_short"], label=f"{self.short_window}-day SMA")
        plt.plot(d.index, d["SMA_long"], label=f"{self.long_window}-day SMA")
        plt.scatter(buys.index, buys["SMA_short"], marker="^", s=120,
                    color="green", label="Bullish cross", zorder=3)
        plt.scatter(sells.index, sells["SMA_short"], marker="v", s=120,
                    color="red", label="Bearish cross", zorder=3)

        plt.title(f"{self.ticker} {self.short_window}/{self.long_window} SMA crossover")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=120)
            print("saved chart to", save_path)
        else:
            plt.show()
