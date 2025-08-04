import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from datetime import datetime, timedelta
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException


class DataStreamer:
    def __init__(self, alpha_vantage_api_key=None, binance_api_key=None, binance_api_secret=None):
        """
        Initialize the MultiSourceDataFetcher.

        Args:
            alpha_vantage_api_key (str or None): API key for Alpha Vantage. None to disable AV.
            binance_api_key (str or None): API key for Binance.
            binance_api_secret (str or None): API secret for Binance.
        """
        assert alpha_vantage_api_key is None or isinstance(alpha_vantage_api_key, str), \
            "alpha_vantage_api_key must be a string or None."
        assert binance_api_key is None or isinstance(binance_api_key, str), \
            "binance_api_key must be a string or None."
        assert binance_api_secret is None or isinstance(binance_api_secret, str), \
            "binance_api_secret must be a string or None."

        self.alpha_vantage_api_key = alpha_vantage_api_key
        if alpha_vantage_api_key:
            self.av_ts = TimeSeries(key=alpha_vantage_api_key, output_format='pandas')
        else:
            self.av_ts = None

        if binance_api_key and binance_api_secret:
            self.binance_client = Client(binance_api_key, binance_api_secret)
        else:
            self.binance_client = None

    def _map_interval_alpha_vantage(self, interval):
        iv = interval.lower()
        if iv in ['1m', '1min']:
            return '1min'
        elif iv in ['2m', '2min']:
            raise ValueError("Alpha Vantage does NOT support 2min interval.")
        elif iv in ['5m', '5min']:
            return '5min'
        elif iv in ['15m', '15min']:
            return '15min'
        elif iv in ['30m', '30min']:
            return '30min'
        elif iv in ['60m', '60min', '1h']:
            return '60min'
        elif iv in ['1d', 'daily']:
            return 'daily'
        elif iv in ['1wk', 'weekly']:
            return 'weekly'
        elif iv in ['1mo', 'monthly']:
            return 'monthly'
        else:
            raise ValueError(f"Interval '{interval}' not supported by Alpha Vantage.")

    def _map_interval_yfinance(self, interval):
        mapping = {
            '1m': '1m',
            '2m': '2m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '60m': '60m',
            '1h': '60m',
            '1d': '1d',
            'daily': '1d',
            '1wk': '1wk',
            'weekly': '1wk',
            '1mo': '1mo',
            'monthly': '1mo'
        }
        iv = interval.lower()
        if iv not in mapping:
            raise ValueError(f"Interval '{interval}' not supported by yfinance.")
        return mapping[iv]

    def _map_interval_binance(self, interval):
        # Binance valid intervals (https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data)
        valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h',
                           '1d', '3d', '1w', '1M']
        iv = interval.lower()
        if iv in ['60m', '1h']:
            iv = '1h'
        elif iv == 'daily':
            iv = '1d'
        elif iv == 'weekly':
            iv = '1w'
        elif iv == 'monthly':
            iv = '1M'

        if iv not in valid_intervals:
            raise ValueError(f"Interval '{interval}' not supported by Binance.")
        return iv

    def _adjust_dates(self, source, interval, start_date, end_date):
        """
        Adjust start_date to max available range based on source and interval.
        """
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        if end_date is None:
            end_date = pd.Timestamp.today()

        if source == 'yfinance':
            intraday_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '1h']
            if interval.lower() in intraday_intervals:
                min_start = end_date - pd.Timedelta(days=30)
                if start_date is None or start_date < min_start:
                    print(f"[Info] Yahoo Finance intraday '{interval}' interval: adjusting start_date to {min_start.date()}")
                    start_date = min_start

        elif source == 'alpha_vantage':
            intraday_intervals = ['1min', '5min', '15min', '30min', '60min']
            if interval.lower() in intraday_intervals:
                min_start = end_date - pd.Timedelta(days=60)
                if start_date is None or start_date < min_start:
                    print(f"[Info] Alpha Vantage intraday '{interval}' interval: adjusting start_date to {min_start.date()}")
                    start_date = min_start

        elif source == 'binance':
            # Binance allows up to ~1 year of historical klines for most intervals
            if start_date is None:
                start_date = end_date - pd.Timedelta(days=365)

        if start_date > end_date:
            raise ValueError("start_date cannot be after end_date after adjustment.")

        return start_date, end_date

    def _fetch_alpha_vantage(self, ticker, interval, start_date=None, end_date=None):
        if not self.av_ts:
            print("[Alpha Vantage] API key not set, skipping Alpha Vantage fetch.")
            return None

        interval_av = self._map_interval_alpha_vantage(interval)
        try:
            start_date, end_date = self._adjust_dates('alpha_vantage', interval_av, start_date, end_date)

            if interval_av in ['1min', '5min', '15min', '30min', '60min']:
                data, meta = self.av_ts.get_intraday(symbol=ticker, interval=interval_av, outputsize='full')
            elif interval_av == 'daily':
                data, meta = self.av_ts.get_daily(symbol=ticker, outputsize='full')
            elif interval_av == 'weekly':
                data, meta = self.av_ts.get_weekly(symbol=ticker)
            elif interval_av == 'monthly':
                data, meta = self.av_ts.get_monthly(symbol=ticker)
            else:
                raise ValueError("Unexpected interval mapping.")

            data.index = pd.to_datetime(data.index)
            data.rename(columns=lambda x: x.split('. ')[1], inplace=True)

            data = data[(data.index >= start_date) & (data.index <= end_date)]
            if data.empty:
                print(f"[Alpha Vantage] No data for {ticker} in the given date range.")
                return None

            return data

        except Exception as e:
            print(f"[Alpha Vantage] Failed to fetch {ticker} @ {interval}: {e}")
            return None

    def _fetch_yfinance(self, ticker, interval, start_date=None, end_date=None):
        yf_interval = self._map_interval_yfinance(interval)
        try:
            start_date, end_date = self._adjust_dates('yfinance', yf_interval, start_date, end_date)
            data = yf.download(ticker, start=start_date, end=end_date, interval=yf_interval, progress=False)
            if data.empty:
                print(f"[Yahoo Finance] No data for {ticker} in the given date range.")
                return None
            data.index = pd.to_datetime(data.index)
            return data
        except Exception as e:
            print(f"[Yahoo Finance] Failed to fetch {ticker} @ {interval}: {e}")
            return None

    def _fetch_binance(self, ticker, interval, start_date=None, end_date=None):
        if not self.binance_client:
            print("[Binance] Binance API credentials not set, skipping Binance fetch.")
            return None

        interval_binance = self._map_interval_binance(interval)
        try:
            start_date, end_date = self._adjust_dates('binance', interval_binance, start_date, end_date)

            # Binance expects strings like "1 Jan, 2023"
            start_str = start_date.strftime("%d %b, %Y")
            end_str = (end_date + timedelta(days=1)).strftime("%d %b, %Y")  # Inclusive end_date

            klines = self.binance_client.get_historical_klines(ticker, interval_binance, start_str, end_str)

            if not klines:
                print(f"[Binance] No data returned for {ticker} @ {interval_binance}")
                return None

            # Parse klines to DataFrame
            df = pd.DataFrame(klines, columns=[
                "OpenTime", "Open", "High", "Low", "Close", "Volume",
                "CloseTime", "QuoteAssetVolume", "NumberOfTrades",
                "TakerBuyBaseAssetVolume", "TakerBuyQuoteAssetVolume", "Ignore"
            ])
            df["OpenTime"] = pd.to_datetime(df["OpenTime"], unit='ms')
            df["CloseTime"] = pd.to_datetime(df["CloseTime"], unit='ms')

            # Convert numeric columns
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df.set_index("OpenTime", inplace=True)
            df = df.loc[(df.index >= start_date) & (df.index <= end_date)]

            return df

        except BinanceAPIException as e:
            if "Service unavailable from a restricted location" in str(e):
                print(f"[Binance] API access restricted in your region. Skipping Binance for {ticker}.")
            else:
                print(f"[Binance] API error: {e}")
            return None
        except Exception as e:
            print(f"[Binance] Unexpected error: {e}")
            return None

    def fetch(self, tickers, interval='1d', source='both', start_date=None, end_date=None):
        """
        Fetch data for tickers from specified source(s).

        Args:
            tickers (list): List of ticker symbols as strings.
            interval (str): Data interval, e.g., '1m', '5m', '1d', '1wk'.
            source (str): One of 'yfinance', 'alpha_vantage', 'binance', or 'both'.
            start_date (str or datetime): Start date for data.
            end_date (str or datetime): End date for data.

        Returns:
            dict: {ticker: DataFrame} with fetched data.
        """
        assert isinstance(tickers, list), "tickers must be a list."
        assert source in ['yfinance', 'alpha_vantage', 'binance', 'both'], \
            "source must be 'yfinance', 'alpha_vantage', 'binance', or 'both'."

        results = {}

        for ticker in tickers:
            data = None

            if source == 'alpha_vantage':
                if not self.alpha_vantage_api_key:
                    print(f"[Alpha Vantage] API key not set. Skipping {ticker}.")
                else:
                    data = self._fetch_alpha_vantage(ticker, interval, start_date, end_date)

            elif source == 'yfinance':
                data = self._fetch_yfinance(ticker, interval, start_date, end_date)

            elif source == 'binance':
                data = self._fetch_binance(ticker, interval, start_date, end_date)

            elif source == 'both':
                # Try Alpha Vantage first if available
                if self.alpha_vantage_api_key:
                    data = self._fetch_alpha_vantage(ticker, interval, start_date, end_date)
                    if data is not None:
                        results[ticker] = data
                        time.sleep(12)  # Alpha Vantage rate limit
                        continue

                # Try Yahoo Finance next
                data = self._fetch_yfinance(ticker, interval, start_date, end_date)

                # If still None and ticker looks like crypto (ends with USDT), try Binance
                if data is None and ticker.upper().endswith("USDT"):
                    data = self._fetch_binance(ticker, interval, start_date, end_date)

            if data is not None:
                results[ticker] = data
            else:
                print(f"[Fetch] Failed to get data for {ticker} from {source}.")

        return results