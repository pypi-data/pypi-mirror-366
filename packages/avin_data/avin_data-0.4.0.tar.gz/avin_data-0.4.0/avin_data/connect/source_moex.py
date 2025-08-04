#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import time
from datetime import UTC
from datetime import date as Date
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

import httpx
import moexalgo
import polars as pl

from avin_data.manager.category import Category
from avin_data.manager.iid import Iid
from avin_data.manager.iid_cache import IidCache
from avin_data.manager.market_data import MarketData
from avin_data.manager.source import Source
from avin_data.utils import (
    CategoryNotFound,
    Cmd,
    TickerNotFound,
    cfg,
    dt_to_ts,
    log,
    now,
    prev_month,
)

SOURCE = Source.MOEX
MSK_OFFSET = TimeDelta(hours=3)
MSK_OFFSET_TS = 3 * 60 * 60 * 1_000_000_000  # ts_nanos offset
AVAILIBLE = [
    MarketData.BAR_1M,
    MarketData.BAR_10M,
    MarketData.BAR_1H,
    MarketData.BAR_D,
    MarketData.BAR_W,
    MarketData.BAR_M,
    MarketData.TIC,
    MarketData.TRADE_STATS,
    MarketData.ORDER_STATS,
    MarketData.OB_STATS,
]


class SourceMoex:
    __auth = False

    # public
    @classmethod
    def cache_instruments_info(cls) -> None:
        log.info("Caching instruments info from MOEX")

        # Without authorization - not work
        cls.__authorizate()

        # moex_categories = ["index", "shares", "currency", "futures"]
        moex_categories = ["index", "shares", "futures", "currency"]
        for i in moex_categories:
            try:
                df = cls.__request_instruments(i)
                category = cls.__to_avin_category(i)
                cache = IidCache(SOURCE, category, df)
                IidCache.save(cache)

            except httpx.ConnectError as e:
                log.warning(f"ConnectError: {e}. Try again after 5 sec")
                time.sleep(5)

            except httpx.ConnectTimeout as e:
                log.warning(f"ConnectTimeout: {e}. Try again after 5 sec")
                time.sleep(5)

    @classmethod
    def find(
        cls,
        s: str,
    ) -> Iid:
        """Get instrument id from str.

        Args:
            s: search querry. Example: "moex_share_sber", "moex_index_imoex2".

        Returns:
            Iid.

        Raises:
            TickerNotFound if not exists.
        """
        # parse str
        exchange_str, category_str, ticker_str = s.upper().split("_")
        assert exchange_str == "MOEX", (
            f"Not supported {exchange_str}, only MOEX"
        )
        category = Category.from_str(category_str)

        # load cache
        cache = IidCache.load(SOURCE, category)
        df = cache.df()

        # try find ticker
        df = df.filter(pl.col("ticker") == ticker_str)
        if len(df) != 1:
            raise TickerNotFound(f"Cannot find ticker {ticker_str}")

        match category:
            case Category.SHARE:
                lotsize = df.item(0, "lotsize")
                step = df.item(0, "minstep")
            case Category.FUTURE:
                lotsize = 1
                step = df.item(0, "minstep")
            case Category.INDEX:
                lotsize = 1
                step = 10 ** -float(df.item(0, "decimals"))
            case _:
                raise CategoryNotFound(
                    f"Not implemented category {category_str}, {df}"
                )

        # NOTE: MOEX not provide figi... using unique fake value
        info = {
            "exchange": exchange_str,
            "category": category_str,
            "ticker": ticker_str,
            "figi": f"figi_MOEX_{category_str}_{ticker_str}",
            "name": df.item(0, "shortname"),
            "lot": lotsize,
            "step": step,
        }

        return Iid(info)

    @classmethod
    def get_market_data(
        cls,
        iid: Iid,
        market_data: MarketData,
        *,
        begin: DateTime | None = None,
        end: DateTime | None = None,
        tradeno: int | None = None,
    ) -> pl.DataFrame:
        # check
        if market_data not in AVAILIBLE:
            log.error(f"Market data unavailible {iid}-{market_data}")
            exit(1)

        # Without authorization - not work
        cls.__authorizate()

        match market_data:
            case MarketData.BAR_1M:
                assert begin is not None
                assert end is not None
                df = cls.__get_bars(iid, market_data, begin, end)
            case MarketData.BAR_10M:
                assert begin is not None
                assert end is not None
                df = cls.__get_bars(iid, market_data, begin, end)
            case MarketData.BAR_1H:
                assert begin is not None
                assert end is not None
                df = cls.__get_bars(iid, market_data, begin, end)
            case MarketData.BAR_D:
                assert begin is not None
                assert end is not None
                df = cls.__get_bars(iid, market_data, begin, end)
            case MarketData.BAR_W:
                assert begin is not None
                assert end is not None
                df = cls.__get_bars(iid, market_data, begin, end)
            case MarketData.BAR_M:
                assert begin is not None
                assert end is not None
                df = cls.__get_bars(iid, market_data, begin, end)
            case MarketData.TIC:
                df = cls.__get_tics(iid, market_data, tradeno)
            case _:
                log.error("Not implemented")
                exit(1)

        return df

    # private
    @classmethod
    def __authorizate(cls) -> None:
        # if auth true -> return
        if cls.__auth:
            return

        # get login / password
        account_path = cfg.moex_account
        if Cmd.is_exist(account_path):
            login, password = Cmd.read_text(account_path)
            login, password = login.strip(), password.strip()
        else:
            log.error(
                "MOEX not exist account file, operations with "
                "market data unavailible. Register and put the file with "
                f"login and password in '{account_path}'. Read more: "
                "https://passport.moex.com/registration"
            )
            exit(1)

        # try auth
        cls.__auth = moexalgo.session.authorize(login, password)
        if cls.__auth:
            log.info("MOEX Authorization successful")
        else:
            log.error(
                "MOEX authorization fault, check your login and password. "
                "Operations with market data unavailible. "
                f"Login='{login}' Password='{password}'"
            )
            exit(1)

    @classmethod
    def __request_instruments(cls, moex_category: str) -> pl.DataFrame:
        market = moexalgo.Market(moex_category)
        response = market.tickers(use_dataframe=True)
        df = pl.from_pandas(response)

        match moex_category:
            case "index":
                return _format_indexes_info(df)
            case "shares":
                return _format_shares_info(df)
            case "futures":
                return _format_futures_info(df)
            case "currency":
                return _format_currencies_info(df)

        raise CategoryNotFound(
            f"Not implemented category {moex_category}, {df}"
        )

    @classmethod
    def __to_avin_category(cls, name: str) -> Category:
        names = {
            "index": Category.INDEX,
            "shares": Category.SHARE,
            "futures": Category.FUTURE,
            "currency": Category.CURRENCY,
            "INDEX": Category.INDEX,
            "SHARE": Category.SHARE,
            "FUTURE": Category.FUTURE,
            "CURRENCY": Category.CURRENCY,
            "SNDX": Category.INDEX,
            "TQBR": Category.SHARE,
            "RFUD": Category.FUTURE,
            "CETS": Category.CURRENCY,
        }

        return names[name]

    @classmethod
    def __to_moex_ticker(cls, iid: Iid) -> moexalgo.AnyTickers:
        MAX_ATTEMPT = 5
        attempt = 0

        while attempt < MAX_ATTEMPT:
            try:
                moex_ticker = moexalgo.Ticker(iid.ticker())
                return moex_ticker

            except httpx.ConnectError as e:
                log.warning(f"ConnectError: {e}. Try again after 3 sec")
                time.sleep(3)

            except httpx.ConnectTimeout as e:
                log.warning(f"ConnectTimeout: {e}. Try again after 3 sec")
                time.sleep(3)

            attempt += 1

        log.error(f"Request ticker failed: {iid}")
        exit(1)

    @classmethod
    def __to_moex_period(
        cls, market_data: MarketData
    ) -> moexalgo.CandlePeriod:
        moex_periods = {
            "1M": moexalgo.CandlePeriod.ONE_MINUTE,
            "10M": moexalgo.CandlePeriod.TEN_MINUTES,
            "1H": moexalgo.CandlePeriod.ONE_HOUR,
            "D": moexalgo.CandlePeriod.ONE_DAY,
            "W": moexalgo.CandlePeriod.ONE_WEEK,
            "M": moexalgo.CandlePeriod.ONE_MONTH,
        }

        period = moex_periods[market_data.value]

        return period

    @classmethod
    def __to_msk(cls, utc_dt: DateTime) -> DateTime:
        return (utc_dt + MSK_OFFSET).replace(tzinfo=None)

    @classmethod
    def __correct_end_dt(
        cls, end: DateTime, market_data: MarketData
    ) -> DateTime:
        # 1. Выравниваем время по начало свечи. Например для 1H из 12:39
        # будет получено 12:00. Для D - начало дня. Для M - 1 число месяца.
        # Если end и так выровнен (как при запросах исторических данных), то
        # останется без изменений.
        corrected = market_data.prev_dt(end)

        # 2. Если запрос и так был выровнен, а не по now().
        # То имелся ввиду полузакрытый диапазон типо [begin, end),
        # а Мос.биржа возвращает свечи включая края диапазона [from, till]
        # поэтому берем начало предыдущей свечи
        # ПС: с W тут тоже все ок. Если на НГ попала середина недели
        # то условие ложно, и еще одна неделя не будет вычтена.
        # А если начало недели 1 января то будет вычтено.
        if corrected == end:
            if market_data == MarketData.BAR_M:
                corrected = prev_month(corrected)
            else:
                corrected -= market_data.timedelta()

        # 3. Мос.биржа присылает и незавершенные свечи тоже...
        # Когда запрос get_bars идет с last_stored, до now().
        # Или когда в запросе время end больше настоящего времени,
        # например в 2025г скачать свечи за [2025-01-01, 2026-01-01].
        # Тогде еще надо отбросить текущую незавершенную свечу.
        msk_dt_now = cls.__to_msk(now())
        msk_current_bar = market_data.prev_dt(msk_dt_now)
        if corrected >= msk_current_bar:
            if market_data == MarketData.BAR_M:
                corrected = prev_month(msk_current_bar)
            else:
                corrected = msk_current_bar - market_data.timedelta()

        return corrected

    @classmethod
    def __get_bars(
        cls,
        iid: Iid,
        market_data: MarketData,
        begin: DateTime,
        end: DateTime,
    ) -> pl.DataFrame:
        # convert types to moex format
        moex_ticker = cls.__to_moex_ticker(iid)
        period = cls.__to_moex_period(market_data)
        begin = cls.__to_msk(begin)
        end = cls.__to_msk(end)

        # correct end datetime, see comment in that func
        end = cls.__correct_end_dt(end, market_data)

        # it is possible, for example, during an update timeframe M W D
        if begin == end:
            return pl.DataFrame()

        # request first part
        bars = cls.__try_request_bars(moex_ticker, period, begin, end)
        if bars.is_empty():
            return bars

        # request other if exist
        current = bars.item(-1, "begin")
        while current < end:
            current = market_data.next_dt(current)
            part = cls.__try_request_bars(moex_ticker, period, current, end)

            if part.is_empty():
                break

            bars.extend(part)
            current = bars.item(-1, "begin")

        # format df
        df = _format_bars_df(bars)

        return df

    @classmethod
    def __try_request_bars(
        cls,
        moex_ticker: moexalgo.AnyTickers,
        period: moexalgo.CandlePeriod,
        begin: DateTime,
        end: DateTime,
    ) -> pl.DataFrame:
        MAX_ATTEMPT = 5
        attempt = 0

        while attempt < MAX_ATTEMPT:
            try:
                df = moex_ticker.candles(
                    start=begin,
                    end=end,
                    period=period,
                    use_dataframe=True,
                )
                return pl.from_pandas(df)

            except httpx.ConnectError as e:
                log.warning(f"ConnectError: {e}. Try again after 3 sec")
                time.sleep(3)

            except httpx.ConnectTimeout as e:
                log.warning(f"ConnectTimeout: {e}. Try again after 3 sec")
                time.sleep(3)

            attempt += 1

        log.error("Request data failed")
        exit(1)

    @classmethod
    def __get_tics(
        cls,
        iid: Iid,
        market_data: MarketData,
        tradeno: int | None,
    ) -> pl.DataFrame:
        # convert types to moex format
        moex_ticker = cls.__to_moex_ticker(iid)

        # request first part
        part = cls.__try_request_tics(moex_ticker, tradeno)
        if part.is_empty():
            return part

        # Мос.Биржа отдает по 10.000 тиков за раз максимум.
        # соответственно если пришло 10.000 значит есть еще.
        # В последней партии будет например 2545 тиков...
        tics = pl.DataFrame(part, part.schema)
        while len(part) == 10_000:
            last = part.item(-1, "tradeno")
            part = cls.__try_request_tics(moex_ticker, last)

            if part.is_empty():
                break

            tics.extend(part)

        # format df
        df = _format_tics_df(tics)

        return df

    @classmethod
    def __try_request_tics(
        cls,
        moex_ticker: moexalgo.AnyTickers,
        tradeno: int | None,
    ) -> pl.DataFrame:
        MAX_ATTEMPT = 5
        attempt = 0

        while attempt < MAX_ATTEMPT:
            try:
                df = moex_ticker.trades(
                    tradeno=tradeno,
                    use_dataframe=True,
                )
                return pl.from_pandas(df)

            except httpx.ConnectError as e:
                log.warning(f"ConnectError: {e}. Try again after 3 sec")
                time.sleep(3)

            except httpx.ConnectTimeout as e:
                log.warning(f"ConnectTimeout: {e}. Try again after 3 sec")
                time.sleep(3)

            attempt += 1

        log.error("Request data failed")
        exit(1)


def _format_indexes_info(df: pl.DataFrame) -> pl.DataFrame:
    columns = ["decimals"]
    for name in columns:
        df = df.with_columns(pl.col(name).cast(pl.String).alias(name))

    return df


def _format_shares_info(df: pl.DataFrame) -> pl.DataFrame:
    columns = ["lotsize", "decimals", "minstep", "issuesize", "listlevel"]
    for name in columns:
        df = df.with_columns(pl.col(name).cast(pl.String).alias(name))

    return df


def _format_futures_info(df: pl.DataFrame) -> pl.DataFrame:
    columns = ["decimals", "minstep"]
    for name in columns:
        df = df.with_columns(pl.col(name).cast(pl.String).alias(name))

    return df


def _format_currencies_info(df: pl.DataFrame) -> pl.DataFrame:
    columns = ["lotsize", "decimals", "minstep"]
    for name in columns:
        df = df.with_columns(pl.col(name).cast(pl.String).alias(name))

    return df


def _format_bars_df(bars: pl.DataFrame) -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "ts_nanos": bars["begin"].cast(pl.Int64) - MSK_OFFSET_TS,
            "open": bars["open"],
            "high": bars["high"],
            "low": bars["low"],
            "close": bars["close"],
            "volume": bars["volume"].cast(pl.Int64),
            "value": bars["value"],
        }
    )

    return df


def _format_tics_df(tics: pl.DataFrame) -> pl.DateFrame:
    # format dataframe
    df = pl.DataFrame(
        {
            "ts_nanos": _get_safely(tics, "ts_nanos"),
            "direction": _get_safely(tics, "direction"),
            "lots": _get_safely(tics, "lots"),
            "price": tics["price"],
            "value": _get_safely(tics, "value"),
            "session": _get_safely(tics, "session"),
            "tradeno": _get_safely(tics, "tradeno"),
        }
    )

    return df


def _get_safely(df: pl.DataFrame, key: str) -> pl.Series | None:
    """Get value (pl.Series) or None if key not exists."""

    match key:
        case "ts_nanos":
            # convert date & time to timestamp
            day = Date.today()
            times = df["tradetime"]
            timestamps = list()
            for t in times:
                dt = DateTime.combine(day, t, tzinfo=UTC) - MSK_OFFSET
                ts = dt_to_ts(dt)
                timestamps.append(ts)
            return pl.Series("ts_nanos", timestamps)
        case "direction":
            if "buysell" in df.columns:
                return df["buysell"]
        case "lots":
            if "quantity" in df.columns:
                return df["quantity"]
        case "tradeno":
            if "tradeno" in df.columns:
                return df["tradeno"]
        case "session":
            if "tradingsession" in df.columns:
                return df["tradingsession"].cast(pl.Int8)
        case "value":
            if "value" in df.columns:
                return df["value"]
            else:
                # это фьючерс... вручную умножим lotsize=1 * lots * price
                return df["quantity"] * df["price"]

    return None


if __name__ == "__main__":
    # import moexalgo as ma

    # SourceMoex._SourceMoex__authorizate()

    # # Акции
    # eq = ma.Market("EQ")
    # r = eq.tickers()
    # print(r)

    # SBER
    # Свечи по акциям SBER за период
    # s = ma.Ticker("SBER")
    # r = s.candles(start="2023-10-10", end="2023-10-18", period="1d").head()
    # print(r)

    # s = ma.Ticker("SBER")
    # r = s.tradestats(start="2023-10-10", end="2023-10-18").head()
    # print(r)

    # s = ma.Ticker("SBER")
    # r = s.orderstats(start="2023-10-10", end="2023-10-18").head()
    # print(r)
    ...
