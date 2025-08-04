"""
Async instrument search, selection, and historical bar data for ProjectX clients.

Author: @TexasCoding
Date: 2025-08-02

Overview:
    Provides async methods for instrument discovery, smart contract selection, and retrieval
    of historical OHLCV bar data, with Polars DataFrame output for high-performance analysis.
    Integrates in-memory caching for both instrument and bar queries, minimizing redundant
    API calls and ensuring data consistency. Designed to support trading and analytics flows
    requiring timely and accurate market data.

Key Features:
    - Symbol/name instrument search with live/active filtering
    - Sophisticated contract selection logic (front month, micro, etc.)
    - Historical bar data retrieval (OHLCV) with timezone handling
    - Transparent, per-query caching for both instrument and bars
    - Data returned as Polars DataFrame (timestamp, open, high, low, close, volume)
    - Utilities for cache management and periodic cleanup

Example Usage:
    ```python
    import asyncio
    from project_x_py import ProjectX


    async def main():
        async with ProjectX.from_env() as client:
            instrument = await client.get_instrument("ES")
            bars = await client.get_bars("ES", days=3, interval=15)
            print(bars.head())


    asyncio.run(main())
    ```

See Also:
    - `project_x_py.client.cache.CacheMixin`
    - `project_x_py.client.base.ProjectXBase`
    - `project_x_py.client.trading.TradingMixin`
"""

import datetime
import re
import time
from typing import TYPE_CHECKING, Any

import polars as pl
import pytz

from project_x_py.exceptions import ProjectXInstrumentError
from project_x_py.models import Instrument
from project_x_py.utils import (
    ErrorMessages,
    LogContext,
    LogMessages,
    ProjectXLogger,
    format_error_message,
    handle_errors,
    validate_response,
)

if TYPE_CHECKING:
    from project_x_py.types import ProjectXClientProtocol

logger = ProjectXLogger.get_logger(__name__)


class MarketDataMixin:
    """Mixin class providing market data functionality."""

    @handle_errors("get instrument")
    @validate_response(required_fields=["success", "contracts"])
    async def get_instrument(
        self: "ProjectXClientProtocol", symbol: str, live: bool = False
    ) -> Instrument:
        """
        Get detailed instrument information with caching.

        Args:
            symbol: Trading symbol (e.g., 'NQ', 'ES', 'MGC')
            live: If True, only return live/active contracts (default: False)

        Returns:
            Instrument object with complete contract details

        Example:
            >>> instrument = await client.get_instrument("NQ")
            >>> print(f"Trading {instrument.symbol} - {instrument.name}")
            >>> print(f"Tick size: {instrument.tick_size}")
        """
        with LogContext(
            logger,
            operation="get_instrument",
            symbol=symbol,
            live=live,
        ):
            await self._ensure_authenticated()

            # Check cache first
            cached_instrument = self.get_cached_instrument(symbol)
            if cached_instrument:
                logger.info(LogMessages.CACHE_HIT, extra={"symbol": symbol})
                return cached_instrument

            logger.info(LogMessages.CACHE_MISS, extra={"symbol": symbol})

            # Search for instrument
            payload = {"searchText": symbol, "live": live}
            response = await self._make_request(
                "POST", "/Contract/search", data=payload
            )

            if not response or not response.get("success", False):
                raise ProjectXInstrumentError(
                    format_error_message(
                        ErrorMessages.INSTRUMENT_NOT_FOUND, symbol=symbol
                    )
                )

            contracts_data = response.get("contracts", [])
            if not contracts_data:
                raise ProjectXInstrumentError(
                    format_error_message(
                        ErrorMessages.INSTRUMENT_NOT_FOUND, symbol=symbol
                    )
                )

            # Select best match
            best_match = self._select_best_contract(contracts_data, symbol)
            instrument = Instrument(**best_match)

            # Cache the result
            self.cache_instrument(symbol, instrument)
            logger.info(LogMessages.CACHE_UPDATE, extra={"symbol": symbol})

            # Periodic cache cleanup
            if time.time() - self.last_cache_cleanup > 3600:  # Every hour
                await self._cleanup_cache()

            return instrument

    def _select_best_contract(
        self: "ProjectXClientProtocol",
        instruments: list[dict[str, Any]],
        search_symbol: str,
    ) -> dict[str, Any]:
        """
        Select the best matching contract from search results.

        This method implements smart contract selection logic for futures and other
        instruments, ensuring the most appropriate contract is selected based on
        the search criteria. The selection algorithm follows these priorities:

        1. Exact symbol match (case-insensitive)
        2. For futures contracts:
           - Identifies the base symbol (e.g., "ES" from "ESM23")
           - Groups contracts by base symbol
           - Selects the front month contract (chronologically closest expiration)
        3. For micro contracts, ensures proper matching (e.g., "MNQ" for micro Nasdaq)
        4. Falls back to the first result if no better match is found

        The futures month codes follow CME convention: F(Jan), G(Feb), H(Mar), J(Apr),
        K(May), M(Jun), N(Jul), Q(Aug), U(Sep), V(Oct), X(Nov), Z(Dec)

        Args:
            instruments: List of instrument dictionaries from search results
            search_symbol: Original search symbol provided by the user

        Returns:
            dict[str, Any]: Best matching instrument dictionary with complete contract details

        Raises:
            ProjectXInstrumentError: If no instruments are found for the given symbol
        """
        if not instruments:
            raise ProjectXInstrumentError(f"No instruments found for: {search_symbol}")

        search_upper = search_symbol.upper()

        # First try exact match
        for inst in instruments:
            if inst.get("symbol", "").upper() == search_upper:
                return inst

        # For futures, try to find the front month
        # Extract base symbol and find all contracts
        futures_pattern = re.compile(r"^(.+?)([FGHJKMNQUVXZ]\d{1,2})$")
        base_symbols: dict[str, list[dict[str, Any]]] = {}

        for inst in instruments:
            symbol = inst.get("symbol", "").upper()
            match = futures_pattern.match(symbol)
            if match:
                base = match.group(1)
                if base not in base_symbols:
                    base_symbols[base] = []
                base_symbols[base].append(inst)

        # Find contracts matching our search
        matching_base = None
        for base in base_symbols:
            if base == search_upper or search_upper.startswith(base):
                matching_base = base
                break

        if matching_base and base_symbols[matching_base]:
            # Sort by symbol to get front month (alphabetical = chronological for futures)
            sorted_contracts = sorted(
                base_symbols[matching_base], key=lambda x: x.get("symbol", "")
            )
            return sorted_contracts[0]

        # Default to first result
        return instruments[0]

    @handle_errors("search instruments")
    @validate_response(required_fields=["success", "contracts"])
    async def search_instruments(
        self: "ProjectXClientProtocol", query: str, live: bool = False
    ) -> list[Instrument]:
        """
        Search for instruments by symbol or name.

        Args:
            query: Search query (symbol or partial name)
            live: If True, search only live/active instruments

        Returns:
            List of Instrument objects matching the query

        Example:
            >>> instruments = await client.search_instruments("gold")
            >>> for inst in instruments:
            >>>     print(f"{inst.name}: {inst.description}")
        """
        with LogContext(
            logger,
            operation="search_instruments",
            query=query,
            live=live,
        ):
            await self._ensure_authenticated()

            logger.info(LogMessages.DATA_FETCH, extra={"query": query})

            payload = {"searchText": query, "live": live}
            response = await self._make_request(
                "POST", "/Contract/search", data=payload
            )

            if not response or not response.get("success", False):
                return []

            contracts_data = response.get("contracts", [])
            instruments = [Instrument(**contract) for contract in contracts_data]

            logger.info(
                LogMessages.DATA_RECEIVED,
                extra={"count": len(instruments), "query": query},
            )

            return instruments

    @handle_errors("get bars")
    async def get_bars(
        self: "ProjectXClientProtocol",
        symbol: str,
        days: int = 8,
        interval: int = 5,
        unit: int = 2,
        limit: int | None = None,
        partial: bool = True,
    ) -> pl.DataFrame:
        """
        Retrieve historical OHLCV bar data for an instrument.

        This method fetches historical market data with intelligent caching and
        timezone handling. The data is returned as a Polars DataFrame optimized
        for financial analysis and technical indicator calculations.

        Args:
            symbol: Symbol of the instrument (e.g., "MGC", "MNQ", "ES")
            days: Number of days of historical data (default: 8)
            interval: Interval between bars in the specified unit (default: 5)
            unit: Time unit for the interval (default: 2 for minutes)
                  1=Second, 2=Minute, 3=Hour, 4=Day, 5=Week, 6=Month
            limit: Maximum number of bars to retrieve (auto-calculated if None)
            partial: Include incomplete/partial bars (default: True)

        Returns:
            pl.DataFrame: DataFrame with OHLCV data and timezone-aware timestamps
                Columns: timestamp, open, high, low, close, volume
                Timezone: Converted to your configured timezone (default: US/Central)

        Raises:
            ProjectXInstrumentError: If instrument not found or invalid
            ProjectXDataError: If data retrieval fails or invalid response

        Example:
            >>> # Get 5 days of 15-minute gold data
            >>> data = await client.get_bars("MGC", days=5, interval=15)
            >>> print(f"Retrieved {len(data)} bars")
            >>> print(
            ...     f"Date range: {data['timestamp'].min()} to {data['timestamp'].max()}"
            ... )
        """
        with LogContext(
            logger,
            operation="get_bars",
            symbol=symbol,
            days=days,
            interval=interval,
            unit=unit,
            partial=partial,
        ):
            await self._ensure_authenticated()

            # Check market data cache
            cache_key = f"{symbol}_{days}_{interval}_{unit}_{partial}"
            cached_data = self.get_cached_market_data(cache_key)
            if cached_data is not None:
                logger.info(LogMessages.CACHE_HIT, extra={"cache_key": cache_key})
                return cached_data

            logger.info(
                LogMessages.DATA_FETCH,
                extra={"symbol": symbol, "days": days, "interval": interval},
            )

            # Lookup instrument
            instrument = await self.get_instrument(symbol)

            # Calculate date range
            from datetime import timedelta

            start_date = datetime.datetime.now(pytz.UTC) - timedelta(days=days)
            end_date = datetime.datetime.now(pytz.UTC)

        # Calculate limit based on unit type
        if limit is None:
            if unit == 1:  # Seconds
                total_seconds = int((end_date - start_date).total_seconds())
                limit = int(total_seconds / interval)
            elif unit == 2:  # Minutes
                total_minutes = int((end_date - start_date).total_seconds() / 60)
                limit = int(total_minutes / interval)
            elif unit == 3:  # Hours
                total_hours = int((end_date - start_date).total_seconds() / 3600)
                limit = int(total_hours / interval)
            else:  # Days or other units
                total_minutes = int((end_date - start_date).total_seconds() / 60)
                limit = int(total_minutes / interval)

        # Prepare payload
        payload = {
            "contractId": instrument.id,
            "live": False,
            "startTime": start_date.isoformat(),
            "endTime": end_date.isoformat(),
            "unit": unit,
            "unitNumber": interval,
            "limit": limit,
            "includePartialBar": partial,
        }

        # Fetch data using correct endpoint
        response = await self._make_request(
            "POST", "/History/retrieveBars", data=payload
        )

        if not response:
            return pl.DataFrame()

        # Handle the response format
        if not response.get("success", False):
            error_msg = response.get("errorMessage", "Unknown error")
            self.logger.error(
                LogMessages.DATA_ERROR,
                extra={"operation": "get_history", "error": error_msg},
            )
            return pl.DataFrame()

        bars_data = response.get("bars", [])
        if not bars_data:
            return pl.DataFrame()

        # Convert to DataFrame and process
        data = (
            pl.DataFrame(bars_data)
            .sort("t")
            .rename(
                {
                    "t": "timestamp",
                    "o": "open",
                    "h": "high",
                    "l": "low",
                    "c": "close",
                    "v": "volume",
                }
            )
            .with_columns(
                # Optimized datetime conversion with cached timezone
                pl.col("timestamp")
                .str.to_datetime()
                .dt.replace_time_zone("UTC")
                .dt.convert_time_zone(self.config.timezone)
            )
        )

        if data.is_empty():
            return data

        # Sort by timestamp
        data = data.sort("timestamp")

        # Cache the result
        self.cache_market_data(cache_key, data)

        # Cleanup cache periodically
        if time.time() - self.last_cache_cleanup > 3600:
            await self._cleanup_cache()

        return data
