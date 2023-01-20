import yfinance as yf
import pandas as pd
from collections import namedtuple

StockPrice = namedtuple("StockPrice", "Open High Low Close Volume")


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.first_candle = None
        self.got_multiple_candles = False
        self.interval = None

    def get_first_candle(self, interval) -> StockPrice:
        self.interval = interval
        if not self.first_candle:
            price = yf.download(tickers=self.ticker, period='1d', interval=interval).iloc[0]
            self.first_candle = StockPrice(Open=price.Open,
                                           Close=price.Close,
                                           High=price.High,
                                           Low=price.Low,
                                           Volume=price.Volume
                                           )
        return self.first_candle

    def get_current_price(self):
        if not self.got_multiple_candles:
            df = yf.download(tickers=self.ticker, period='1d', interval=self.interval)
            r, c = df.shape
            if r > 1:
                self.got_multiple_candles = True
        if self.got_multiple_candles:
            return yf.Ticker(self.ticker).info['regularMarketPrice']
