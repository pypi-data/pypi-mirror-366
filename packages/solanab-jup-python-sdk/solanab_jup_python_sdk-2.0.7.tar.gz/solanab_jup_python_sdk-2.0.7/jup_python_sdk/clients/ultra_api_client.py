from typing import Any, Optional

from jup_python_sdk.clients.base_ultra_client import BaseUltraClient
from jup_python_sdk.clients.jupiter_client import AsyncJupiterClient, JupiterClient
from jup_python_sdk.models.ultra_api.ultra_execute_request_model import (
    UltraExecuteRequest,
)
from jup_python_sdk.models.ultra_api.ultra_order_request_model import (
    UltraOrderRequest,
)


class UltraApiClient(JupiterClient, BaseUltraClient):
    """
    A synchronous client for interacting with the Jupiter Ultra API.
    """

    def _make_get_request(
        self, url: str, params: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Make a synchronous GET request."""
        response = self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def _make_post_request(
        self, url: str, json: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Make a synchronous POST request."""
        response = self.client.post(url, json=json, headers=headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def _call_order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """Call the synchronous order method."""
        return self.order(request)

    def _call_execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """Call the synchronous execute method."""
        return self.execute(request)

    def order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get an order from the Jupiter Ultra API (synchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        params = self._prepare_order_params(request)
        url = self._build_order_url()
        return self._make_get_request(url, params=params, headers=self._get_headers())

    def execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """
        Execute the order with the Jupiter Ultra API (synchronous).

        Args:
            request (UltraExecuteRequest): The execute request parameters.

        Returns:
            dict: The dict api response.
        """
        payload = self._prepare_execute_payload(request)
        url = self._build_execute_url()
        return self._make_post_request(url, json=payload, headers=self._get_headers())

    def order_and_execute(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get and execute an order in a single call (synchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        order_response = self._call_order(request)
        execute_request = self._prepare_execute_request_from_order(order_response)
        return self._call_execute(execute_request)

    def balances(self, address: str) -> dict[str, Any]:
        """
        Get token balances of an account (synchronous).

        Args:
            address (str): The public key of the account to get balances for.

        Returns:
            dict: The dict api response.
        """
        url = self._build_balances_url(address)
        return self._make_get_request(url, headers=self._get_headers())

    def shield(self, mints: list[str]) -> dict[str, Any]:
        """
        Get token info and warnings for specific mints (synchronous).

        Args:
            mints (list[str]): List of token mint addresses
            to get information for.

        Returns:
            dict: The dict api response with warnings information.
        """
        params = self._prepare_shield_params(mints)
        url = self._build_shield_url()
        return self._make_get_request(url, params=params, headers=self._get_headers())


class AsyncUltraApiClient(AsyncJupiterClient, BaseUltraClient):
    """
    An asynchronous client for interacting with the Jupiter Ultra API.
    """

    async def _make_get_request(
        self, url: str, params: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Make an asynchronous GET request."""
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    async def _make_post_request(
        self, url: str, json: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Make an asynchronous POST request."""
        response = await self.client.post(url, json=json, headers=headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    async def _call_order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """Call the asynchronous order method."""
        return await self.order(request)

    async def _call_execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """Call the asynchronous execute method."""
        return await self.execute(request)

    async def order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get an order from the Jupiter Ultra API (asynchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        params = self._prepare_order_params(request)
        url = self._build_order_url()
        return await self._make_get_request(url, params=params, headers=self._get_headers())

    async def execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """
        Execute the order with the Jupiter Ultra API (asynchronous).

        Args:
            request (UltraExecuteRequest): The execute request parameters.

        Returns:
            dict: The dict api response.
        """
        payload = self._prepare_execute_payload(request)
        url = self._build_execute_url()
        return await self._make_post_request(url, json=payload, headers=self._get_headers())

    async def order_and_execute(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get and execute an order in a single call (asynchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        order_response = await self._call_order(request)
        execute_request = self._prepare_execute_request_from_order(order_response)
        return await self._call_execute(execute_request)

    async def balances(self, address: str) -> dict[str, Any]:
        """
        Get token balances of an account (asynchronous).

        Args:
            address (str): The public key of the account to get balances for.

        Returns:
            dict: The dict api response.
        """
        url = self._build_balances_url(address)
        return await self._make_get_request(url, headers=self._get_headers())

    async def shield(self, mints: list[str]) -> dict[str, Any]:
        """
        Get token info and warnings for specific mints (asynchronous).

        Args:
            mints (list[str]): List of token mint addresses
            to get information for.

        Returns:
            dict: The dict api response with warnings information.
        """
        params = self._prepare_shield_params(mints)
        url = self._build_shield_url()
        return await self._make_get_request(url, params=params, headers=self._get_headers())
