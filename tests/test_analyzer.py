import sys
import os

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analyzer import CrossoverAnalyzer


# using fake prices so the tests work offline
def make_analyzer(prices, short=2, long=3):
    dates = pd.date_range("2024-01-01", periods=len(prices))
    a = CrossoverAnalyzer("test", short, long)
    a.set_prices(pd.Series(prices, index=dates, dtype=float))
    return a


def test_moving_averages():
    a = make_analyzer([1, 2, 3, 4, 5])
    a.compute_averages()
    assert a.data["SMA_short"].tolist()[1:] == [1.5, 2.5, 3.5, 4.5]
    assert a.data["SMA_long"].tolist()[2:] == [2.0, 3.0, 4.0]


def test_up_then_down():
    # goes down, then up (should be bullish), then down again (bearish)
    a = make_analyzer([10, 9, 8, 7, 6, 8, 10, 12, 10, 8, 6, 4])
    crosses = a.find_crossovers()
    assert crosses["Signal"].tolist() == [1, -1]


def test_no_crosses_when_always_going_up():
    a = make_analyzer(list(range(1, 20)))
    assert len(a.find_crossovers()) == 0


def test_short_bigger_than_long():
    with pytest.raises(ValueError):
        CrossoverAnalyzer("AAPL", short_window=50, long_window=20)


def test_too_little_data():
    a = make_analyzer([1, 2])
    with pytest.raises(ValueError):
        a.compute_averages()
