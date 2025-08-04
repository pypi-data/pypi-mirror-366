"""
Async trading queries: positions and trade history for ProjectX accounts.

Author: @TexasCoding
Date: 2025-08-02

Overview:
    Supplies async methods for querying open positions and executed trades for the currently
    authenticated account. Integrates tightly with the authentication/session lifecycle and
    other mixins, enabling streamlined access to P&L, trade analysis, and reporting data.
    All queries require a valid session and leverage ProjectX's unified API request logic.

Key Features:
    - Query current open positions for the selected account
    - Search historical trades with flexible date range and contract filters
    - Async error handling and robust integration with authentication
    - Typed results as Position and Trade model objects for analysis/reporting
    - Designed for use in trading bots, dashboards, and research scripts

Example Usage:
    ```python
    import asyncio
    from project_x_py import ProjectX


    async def main():
        async with ProjectX.from_env() as client:
            await client.authenticate()
            positions = await client.get_positions()
            trades = await client.search_trades(limit=10)
            print([p.symbol for p in positions])
            print([t.contractId for t in trades])


    asyncio.run(main())
    ```

See Also:
    - `project_x_py.client.auth.AuthenticationMixin`
    - `project_x_py.client.base.ProjectXBase`
    - `project_x_py.client.market_data.MarketDataMixin`
"""

import datetime
import logging
from datetime import timedelta
from typing import TYPE_CHECKING

import pytz

from project_x_py.exceptions import ProjectXError
from project_x_py.models import Position, Trade

if TYPE_CHECKING:
    from project_x_py.types import ProjectXClientProtocol

logger = logging.getLogger(__name__)


class TradingMixin:
    """Mixin class providing trading functionality."""

    async def get_positions(self: "ProjectXClientProtocol") -> list[Position]:
        """
        Get all open positions for the authenticated account.

        This method retrieves all current open positions for the currently selected
        trading account. It provides a snapshot of the portfolio including position
        size, entry price, unrealized P&L, and other position details.

        The method automatically ensures authentication before making the API call
        and handles the conversion of raw position data into strongly-typed Position
        objects for easier analysis and manipulation.

        Returns:
            list[Position]: List of Position objects representing current holdings,
                each containing:
                - symbol: Instrument symbol
                - quantity: Position size (positive for long, negative for short)
                - price: Average entry price
                - unrealized_pnl: Current unrealized profit/loss
                - contract_id: Unique contract identifier
                - position_id: Unique position identifier
                - timestamp: Position open time

        Raises:
            ProjectXError: If no account is selected or API call fails
            ProjectXAuthenticationError: If authentication is required

        Example:
            >>> positions = await client.get_positions()
            >>> for pos in positions:
            >>>     print(f"{pos.symbol}: {pos.quantity} @ {pos.price}")
            >>>     print(f"Unrealized P&L: ${pos.unrealized_pnl:,.2f}")
        """
        await self._ensure_authenticated()

        if not self.account_info:
            raise ProjectXError("No account selected")

        response = await self._make_request(
            "GET", f"/accounts/{self.account_info.id}/positions"
        )

        if not response or not isinstance(response, list):
            return []

        return [Position(**pos) for pos in response]

    async def search_open_positions(
        self: "ProjectXClientProtocol", account_id: int | None = None
    ) -> list[Position]:
        """
        Search for open positions across accounts.

        Args:
            account_id: Optional account ID to filter positions

        Returns:
            List of Position objects

        Example:
            >>> positions = await client.search_open_positions()
            >>> total_pnl = sum(pos.unrealized_pnl for pos in positions)
            >>> print(f"Total P&L: ${total_pnl:,.2f}")
        """
        await self._ensure_authenticated()

        # Use the account_id from the authenticated account if not provided
        if account_id is None and self.account_info:
            account_id = self.account_info.id

        if account_id is None:
            raise ProjectXError("No account ID available for position search")

        payload = {"accountId": account_id}
        response = await self._make_request(
            "POST", "/Position/searchOpen", data=payload
        )

        if not response or not response.get("success", False):
            return []

        positions_data = response.get("positions", [])
        return [Position(**pos) for pos in positions_data]

    async def search_trades(
        self: "ProjectXClientProtocol",
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
        contract_id: str | None = None,
        account_id: int | None = None,
        limit: int = 100,
    ) -> list[Trade]:
        """
        Search trade execution history for analysis and reporting.

        Retrieves executed trades within the specified date range, useful for
        performance analysis, tax reporting, and strategy evaluation.

        Args:
            start_date: Start date for trade search (default: 30 days ago)
            end_date: End date for trade search (default: now)
            contract_id: Optional contract ID filter for specific instrument
            account_id: Account ID to search (uses default account if None)
            limit: Maximum number of trades to return (default: 100)

        Returns:
            List[Trade]: List of executed trades with detailed information including:
                - contractId: Instrument that was traded
                - size: Trade size (positive=buy, negative=sell)
                - price: Execution price
                - timestamp: Execution time
                - commission: Trading fees

        Raises:
            ProjectXError: If trade search fails or no account information available

        Example:
            >>> from datetime import datetime, timedelta
            >>> # Get last 7 days of trades
            >>> start = datetime.now() - timedelta(days=7)
            >>> trades = await client.search_trades(start_date=start)
            >>> for trade in trades:
            >>>     print(
            >>>         f"Trade: {trade.contractId} - {trade.size} @ ${trade.price:.2f}"
            >>>     )
        """
        await self._ensure_authenticated()

        if account_id is None:
            if not self.account_info:
                raise ProjectXError("No account information available")
            account_id = self.account_info.id

        # Default date range
        if end_date is None:
            end_date = datetime.datetime.now(pytz.UTC)
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Prepare parameters
        params = {
            "accountId": account_id,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "limit": limit,
        }

        if contract_id:
            params["contractId"] = contract_id

        response = await self._make_request("GET", "/trades/search", params=params)

        if not response or not isinstance(response, list):
            return []

        return [Trade(**trade) for trade in response]
