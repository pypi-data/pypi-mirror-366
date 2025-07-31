"""Wallets module for the 1Shot API."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.wallet import (
    Wallet,
    WalletListParams,
    WalletCreateParams,
    WalletUpdateParams,
    Delegation,
    DelegationListParams,
    DelegationCreateParams,
    WalletTransferParams,
)
from uxly_1shot_client.models.transaction import Transaction
if TYPE_CHECKING:
    from uxly_1shot_client.async_client import AsyncClient
    from uxly_1shot_client.sync_client import Client

class BaseWallets:
    """Base class for wallets module."""

    def _get_list_url(self, business_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Get the URL for listing wallets.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            The URL for listing wallets
        """
        url = f"/business/{business_id}/wallets"
        if params:
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        return url

    def _get_create_url(self, business_id: str) -> str:
        """Get the URL for creating a wallet.

        Args:
            business_id: The business ID

        Returns:
            The URL for creating a wallet
        """
        return f"/business/{business_id}/wallets"

    def _get_get_url(self, wallet_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Get the URL for getting a wallet.

        Args:
            wallet_id: The wallet ID
            params: Optional query parameters

        Returns:
            The URL for getting a wallet
        """
        url = f"/wallets/{wallet_id}"
        if params:
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        return url

    def _get_update_url(self, wallet_id: str) -> str:
        """Get the URL for updating a wallet.

        Args:
            wallet_id: The wallet ID

        Returns:
            The URL for updating a wallet
        """
        return f"/wallets/{wallet_id}"

    def _get_delete_url(self, wallet_id: str) -> str:
        """Get the URL for deleting a wallet.

        Args:
            wallet_id: The wallet ID

        Returns:
            The URL for deleting a wallet
        """
        return f"/wallets/{wallet_id}"

    def _get_list_delegations_url(self, wallet_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Get the URL for listing delegations for a wallet.

        Args:
            wallet_id: The wallet ID
            params: Optional filter parameters

        Returns:
            The URL for listing delegations
        """
        url = f"/wallets/{wallet_id}/delegations"
        if params:
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        return url

    def _get_create_delegation_url(self, wallet_id: str) -> str:
        """Get the URL for creating a delegation for a wallet.

        Args:
            wallet_id: The wallet ID

        Returns:
            The URL for creating a delegation
        """
        return f"/wallets/{wallet_id}/delegations"

    def _get_transfer_url(self, wallet_id: str) -> str:
        """Get the URL for transferring native tokens from a wallet.

        Args:
            wallet_id: The wallet ID

        Returns:
            The URL for transferring native tokens
        """
        return f"/wallets/{wallet_id}/transfer"


class SyncWallets(BaseWallets):
    """Synchronous wallets module for the 1Shot API."""

    def __init__(self, client: "Client") -> None:
        """Initialize the wallets module.

        Args:
            client: The synchronous client instance
        """
        self._client = client

    def list(
        self, business_id: str, params: Optional[Union[WalletListParams, Dict[str, Any]]] = None
    ) -> PagedResponse[Wallet]:
        """List escrow wallets for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters, either as a dict or WalletListParams instance

        Returns:
            A paged response of wallets
        """
        if params is not None and not isinstance(params, WalletListParams):
            params = WalletListParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_list_url(business_id, params.model_dump(by_alias=True) if params else None)
        response = self._client._request("GET", url)
        return PagedResponse[Wallet].model_validate(response)

    def create(
        self, business_id: str, params: Union[WalletCreateParams, Dict[str, Any]]
    ) -> Wallet:
        """Create a new escrow wallet for a business.

        Args:
            business_id: The business ID
            params: Parameters for creating the wallet, either as a dict or WalletCreateParams instance

        Returns:
            The created wallet
        """
        if not isinstance(params, WalletCreateParams):
            params = WalletCreateParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_create_url(business_id)
        response = self._client._request("POST", url, data=params.model_dump(exclude_none=True, by_alias=True))
        return Wallet.model_validate(response)

    def get(
        self, wallet_id: str, include_balances: Optional[bool] = None
    ) -> Wallet:
        """Get an escrow wallet by ID.

        Args:
            wallet_id: The wallet ID
            include_balances: Whether to include balance information

        Returns:
            The wallet
        """
        params = {"includeBalances": str(include_balances).lower()} if include_balances is not None else None
        url = self._get_get_url(wallet_id, params)
        response = self._client._request("GET", url)
        return Wallet.model_validate(response)

    def update(
        self, wallet_id: str, params: Union[WalletUpdateParams, Dict[str, Any]]
    ) -> Wallet:
        """Update an escrow wallet.

        Args:
            wallet_id: The wallet ID
            params: Update parameters, either as a dict or WalletUpdateParams instance

        Returns:
            The updated wallet
        """
        if not isinstance(params, WalletUpdateParams):
            params = WalletUpdateParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_update_url(wallet_id)
        response = self._client._request("PUT", url, data=params.model_dump(exclude_none=True, by_alias=True))
        return Wallet.model_validate(response)

    def delete(self, wallet_id: str) -> None:
        """Delete a wallet. The API Credential must have Admin level permissions on the Business that owns this Wallet, and the Wallet must be near empty.

        Args:
            wallet_id: The wallet ID

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        self._client._request("DELETE", self._get_delete_url(wallet_id))

    def list_delegations(
        self, wallet_id: str, params: Optional[Union[DelegationListParams, Dict[str, Any]]] = None
    ) -> PagedResponse[Delegation]:
        """List delegations for a wallet.

        Args:
            wallet_id: The wallet ID
            params: Optional filter parameters, either as a dict or DelegationListParams instance

        Returns:
            A paged response of delegations
        """
        if params is not None and not isinstance(params, DelegationListParams):
            params = DelegationListParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_list_delegations_url(wallet_id, params.model_dump(by_alias=True) if params else None)
        response = self._client._request("GET", url)
        return PagedResponse[Delegation].model_validate(response)

    def create_delegation(
        self, wallet_id: str, params: Union[DelegationCreateParams, Dict[str, Any]]
    ) -> Delegation:
        """Create a new delegation for a wallet.

        Args:
            wallet_id: The wallet ID
            params: Parameters for creating the delegation, either as a dict or DelegationCreateParams instance

        Returns:
            The created delegation
        """
        if not isinstance(params, DelegationCreateParams):
            params = DelegationCreateParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_create_delegation_url(wallet_id)
        response = self._client._request("POST", url, data=params.model_dump(exclude_none=True, by_alias=True))
        return Delegation.model_validate(response)

    def transfer(
        self, wallet_id: str, params: Union[WalletTransferParams, Dict[str, Any]]
    ) -> Transaction:
        """Transfer native tokens from a wallet.

        Args:
            wallet_id: The wallet ID
            params: Parameters for the transfer, either as a dict or WalletTransferParams instance

        Returns:
            The transaction object
        """
        if not isinstance(params, WalletTransferParams):
            params = WalletTransferParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_transfer_url(wallet_id)
        response = self._client._request("POST", url, data=params.model_dump(exclude_none=True, by_alias=True))
        return Transaction.model_validate(response)


class AsyncWallets(BaseWallets):
    """Asynchronous wallets module for the 1Shot API."""

    def __init__(self, client: "AsyncClient") -> None:
        """Initialize the wallets module.

        Args:
            client: The asynchronous client instance
        """
        self._client = client

    async def list(
        self, business_id: str, params: Optional[Union[WalletListParams, Dict[str, Any]]] = None
    ) -> PagedResponse[Wallet]:
        """List escrow wallets for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters, either as a dict or WalletListParams instance

        Returns:
            A paged response of wallets
        """
        if params is not None and not isinstance(params, WalletListParams):
            params = WalletListParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_list_url(business_id, params.model_dump(by_alias=True) if params else None)
        response = await self._client._request("GET", url)
        return PagedResponse[Wallet].model_validate(response)

    async def create(
        self, business_id: str, params: Union[WalletCreateParams, Dict[str, Any]]
    ) -> Wallet:
        """Create a new escrow wallet for a business.

        Args:
            business_id: The business ID
            params: Parameters for creating the wallet, either as a dict or WalletCreateParams instance

        Returns:
            The created wallet
        """
        if not isinstance(params, WalletCreateParams):
            params = WalletCreateParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_create_url(business_id)
        response = await self._client._request("POST", url, data=params.model_dump(exclude_none=True, by_alias=True))
        return Wallet.model_validate(response)

    async def get(
        self, wallet_id: str, include_balances: Optional[bool] = None
    ) -> Wallet:
        """Get an escrow wallet by ID.

        Args:
            wallet_id: The wallet ID
            include_balances: Whether to include balance information

        Returns:
            The wallet
        """
        params = {"includeBalances": str(include_balances).lower()} if include_balances is not None else None
        url = self._get_get_url(wallet_id, params)
        response = await self._client._request("GET", url)
        return Wallet.model_validate(response)

    async def update(
        self, wallet_id: str, params: Union[WalletUpdateParams, Dict[str, Any]]
    ) -> Wallet:
        """Update an escrow wallet.

        Args:
            wallet_id: The wallet ID
            params: Update parameters, either as a dict or WalletUpdateParams instance

        Returns:
            The updated wallet
        """
        if not isinstance(params, WalletUpdateParams):
            params = WalletUpdateParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_update_url(wallet_id)
        response = await self._client._request("PUT", url, data=params.model_dump(exclude_none=True, by_alias=True))
        return Wallet.model_validate(response)

    async def delete(self, wallet_id: str) -> None:
        """Delete a wallet. The API Credential must have Admin level permissions on the Business that owns this Wallet, and the Wallet must be near empty.

        Args:
            wallet_id: The wallet ID

        Raises:
            aiohttp.ClientError: If the request fails
        """
        await self._client._request("DELETE", self._get_delete_url(wallet_id))

    async def list_delegations(
        self, wallet_id: str, params: Optional[Union[DelegationListParams, Dict[str, Any]]] = None
    ) -> PagedResponse[Delegation]:
        """List delegations for a wallet.

        Args:
            wallet_id: The wallet ID
            params: Optional filter parameters, either as a dict or DelegationListParams instance

        Returns:
            A paged response of delegations
        """
        if params is not None and not isinstance(params, DelegationListParams):
            params = DelegationListParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_list_delegations_url(wallet_id, params.model_dump(by_alias=True) if params else None)
        response = await self._client._request("GET", url)
        return PagedResponse[Delegation].model_validate(response)

    async def create_delegation(
        self, wallet_id: str, params: Union[DelegationCreateParams, Dict[str, Any]]
    ) -> Delegation:
        """Create a new delegation for a wallet.

        Args:
            wallet_id: The wallet ID
            params: Parameters for creating the delegation, either as a dict or DelegationCreateParams instance

        Returns:
            The created delegation
        """
        if not isinstance(params, DelegationCreateParams):
            params = DelegationCreateParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_create_delegation_url(wallet_id)
        response = await self._client._request("POST", url, data=params.model_dump(exclude_none=True, by_alias=True))
        return Delegation.model_validate(response)

    async def transfer(
        self, wallet_id: str, params: Union[WalletTransferParams, Dict[str, Any]]
    ) -> Transaction:
        """Transfer native tokens from a wallet.

        Args:
            wallet_id: The wallet ID
            params: Parameters for the transfer, either as a dict or WalletTransferParams instance

        Returns:
            The transaction object
        """
        if not isinstance(params, WalletTransferParams):
            params = WalletTransferParams.model_validate(params, by_alias=True, by_name=True)
        url = self._get_transfer_url(wallet_id)
        response = await self._client._request("POST", url, data=params.model_dump(exclude_none=True, by_alias=True))
        return Transaction.model_validate(response)