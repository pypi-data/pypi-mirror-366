"""Transactions module for the 1Shot API."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.transaction import TransactionListParams, Transaction
if TYPE_CHECKING:
    from uxly_1shot_client.async_client import AsyncClient
    from uxly_1shot_client.sync_client import Client


class BaseTransactions:
    """Base class for transactions module."""

    def _get_list_url(self, business_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Get the URL for listing transactions.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            The URL for listing transactions
        """
        url = f"/business/{business_id}/transactions/transactions"
        if params:
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        return url

    def _get_get_url(self, transaction_id: str) -> str:
        """Get the URL for getting an transaction.

        Args:
            transaction_id: The transaction ID

        Returns:
            The URL for getting an transaction
        """
        return f"/transactions/{transaction_id}"


class SyncTransactions(BaseTransactions):
    """Synchronous transactions module for the 1Shot API."""

    def __init__(self, client: "Client") -> None:
        """Initialize the transactions module.

        Args:
            client: The synchronous client instance
        """
        self._client = client

    def list(
        self, business_id: str, params: Optional[Union[TransactionListParams, Dict[str, Any]]] = None
    ) -> PagedResponse[Transaction]:
        """List transactions for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters, either as a dict or TransactionListParams instance

        Returns:
            A paged response of transactions
        """
        if params is not None and not isinstance(params, TransactionListParams):
            params = TransactionListParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_list_url(business_id, params.model_dump(by_alias=True) if params else None)
        response = self._client._request("GET", url)
        return PagedResponse[Transaction].model_validate(response)

    def get(self, transaction_id: str) -> Transaction:
        """Get an transaction by ID.

        Args:
            transaction_id: The transaction ID

        Returns:
            The transaction
        """
        url = self._get_get_url(transaction_id)
        response = self._client._request("GET", url)
        return Transaction.model_validate(response)


class AsyncTransactions(BaseTransactions):
    """Asynchronous transactions module for the 1Shot API."""

    def __init__(self, client: "AsyncClient") -> None:
        """Initialize the transactions module.

        Args:
            client: The asynchronous client instance
        """
        self._client = client

    async def list(
        self, business_id: str, params: Optional[Union[TransactionListParams, Dict[str, Any]]] = None
    ) -> PagedResponse[Transaction]:
        """List transactions for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters, either as a dict or TransactionListParams instance

        Returns:
            A paged response of transactions
        """
        if params is not None and not isinstance(params, TransactionListParams):
            params = TransactionListParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_list_url(business_id, params.model_dump(by_alias=True) if params else None)
        response = await self._client._request("GET", url)
        return PagedResponse[Transaction].model_validate(response)

    async def get(self, transaction_id: str) -> Transaction:
        """Get an transaction by ID.

        Args:
            transaction_id: The transaction ID

        Returns:
            The transaction
        """
        url = self._get_get_url(transaction_id)
        response = await self._client._request("GET", url)
        return Transaction.model_validate(response)