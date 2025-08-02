from datetime import datetime
from typing import Optional, cast

import pandas as pd
from alpaca.data import BarSet, CryptoBarsRequest, CryptoHistoricalDataClient, TimeFrame
from dateutil.relativedelta import relativedelta

from liquidity.data.format import formatter_factory
from liquidity.data.metadata.fields import OHLCV, Fields
from liquidity.data.providers.base import DataProviderBase


class AlpacaCryptoDataProvider(DataProviderBase):
    """A data provider class to fetch and format cryptocurrency price data
    using Alpaca's CryptoHistoricalDataClient.
    """

    def __init__(self) -> None:
        self.client = CryptoHistoricalDataClient()

    def get_prices(
        self,
        ticker: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Fetch and format historical price data for a given cryptocurrency ticker.

        Args:
            ticker (str): The cryptocurrency ticker (e.g., "BTC/USD").
            start (Optional[datetime]): The start date for the data.
                Defaults to one year ago.
            end (Optional[datetime]): The end date for the data.
                Defaults to None (up to the latest available data).

        Returns:
            pd.DataFrame: A DataFrame containing the formatted price data, with the
            index as timestamps and columns named after OHLCV fields.

        """
        df = self._get_raw_data(
            ticker=f"{ticker}/USD",
            start=start or datetime.now() - relativedelta(years=5),
            end=end,
        )
        return self._format_dataframe(df)

    def _get_raw_data(
        self,
        ticker: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Fetch raw historical price data for a cryptocurrency ticker.

        Args:
            ticker (str): The cryptocurrency ticker (e.g., "BTC/USD").


        Returns:
            pd.DataFrame: A DataFrame containing the raw price data.

        """
        request_params = CryptoBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
        )
        result = cast(BarSet, self.client.get_crypto_bars(request_params))
        return result.df

    def _format_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format the raw dataframe fetched from the Alpaca API to the project's
        common format.

        This method performs the necessary transformations on the DataFrame,
        including:
        - Extracting and normalizing the datetime index to a consistent format.
        - Mapping columns to match the expected structure.
        - Applying a formatter to align with project-specific conventions
          for comparison across asset classes.

        Args:
            df (pd.DataFrame): The raw DataFrame fetched from the Alpaca API,
                                containing asset price data (OHLCV format).

        Returns:
            pd.DataFrame: The formatted DataFrame, adjusted to meet the project format.

        """
        # Alpaca uses MultiIndex (ticker, timestamp). Extract the 'timestamp' index
        # from the raw dataframe and convert it into a DatetimeIndex.
        timestamp_index = pd.DatetimeIndex(df.index.get_level_values("timestamp"))

        # Normalize the datetime index to remove any time zone information, ensuring
        # consistency across different data providers (e.g., stocks vs crypto) for
        # easier cross-asset class comparisons and joins.
        df.index = timestamp_index.tz_localize(None).normalize()

        alpaca_formatter = formatter_factory(
            index_name=Fields.Date.value,
            cols_mapper={val.lower(): val for val in OHLCV.all_values()},
            cols_out=OHLCV.all_values(),
        )

        return alpaca_formatter(df)

    def get_dividends(self, ticker: str) -> pd.DataFrame:
        raise RuntimeError("Not available for Crypto")

    def get_treasury_yield(self, maturity: Optional[str]) -> pd.DataFrame:
        raise RuntimeError("Not available for Crypto")
