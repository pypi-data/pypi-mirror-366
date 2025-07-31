"""ContractMethods module for the 1Shot API."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union


from uxly_1shot_client.models.common import PagedResponse
from uxly_1shot_client.models.transaction import Transaction
if TYPE_CHECKING:
    from uxly_1shot_client.async_client import AsyncClient
    from uxly_1shot_client.sync_client import Client
from uxly_1shot_client.models.contract_method import (
    ContractMethodEstimate,
    ContractMethodTestResult,
    ContractMethodEncodeResult,
    ContractMethodExecuteAsDelegatorParams,
    ContractMethod,
    ListContractMethodsParams,
    ContractMethodCreateParams,
    ContractMethodUpdateParams,
    Prompt,
    FullPrompt,
    ContractSearchParams,
    ContractContractMethodsParams,
    ERC7702Authorization,
)

class BaseContractMethods:
    """Base class for ContractMethods module."""

    def _get_test_url(self, contract_method_id: str) -> str:
        """Get the URL for testing a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for testing a contract method
        """
        return f"/methods/{contract_method_id}/test"

    def _get_estimate_url(self, contract_method_id: str) -> str:
        """Get the URL for estimating a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for estimating a contract method
        """
        return f"/methods/{contract_method_id}/estimate"

    def _get_execute_url(self, contract_method_id: str) -> str:
        """Get the URL for executing a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for executing a contract method
        """
        return f"/methods/{contract_method_id}/execute"

    def _get_encode_url(self, contract_method_id: str) -> str:
        """Get the URL for encoding a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for encoding a contract method
        """
        return f"/methods/{contract_method_id}/encode"

    def _get_execute_as_delegator_url(self, contract_method_id: str) -> str:
        """Get the URL for executing a contract method as a delegator.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for executing a contract method as a delegator
        """
        return f"/methods/{contract_method_id}/executeAsDelegator"

    def _get_read_url(self, contract_method_id: str) -> str:
        """Get the URL for reading a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for reading a contract method
        """
        return f"/methods/{contract_method_id}/read"

    def _get_get_url(self, contract_method_id: str) -> str:
        """Get the URL for getting a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for getting a contract method
        """
        return f"/methods/{contract_method_id}"

    def _get_list_url(self, business_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Get the URL for listing contract methods.

        Args:
            business_id: The business ID
            params: Optional filter parameters

        Returns:
            The URL for listing contract methods
        """
        url = f"/business/{business_id}/methods"
        if params:
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        return url

    def _get_create_url(self, business_id: str) -> str:
        """Get the URL for creating a contract method.

        Args:
            business_id: The business ID

        Returns:
            The URL for creating a contract method
        """
        return f"/business/{business_id}/methods"

    def _get_import_from_abi_url(self, business_id: str) -> str:
        """Get the URL for importing contract methods from an ABI.

        Args:
            business_id: The business ID

        Returns:
            The URL for importing contract methods from an ABI
        """
        return f"/business/{business_id}/methods/abi"

    def _get_contract_search_url(self) -> str:
        """Get the URL for searching prompts.

        Returns:
            The URL for searching prompts
        """
        return "/prompts/search"

    def _get_create_contract_methods_from_prompt_url(self, business_id: str) -> str:
        """Get the URL for creating contract methods from a prompt.

        Args:
            business_id: The business ID

        Returns:
            The URL for creating contract methods from a prompt
        """
        return f"/business/{business_id}/methods/prompt"

    def _get_update_url(self, contract_method_id: str) -> str:
        """Get the URL for updating a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for updating a contract method
        """
        return f"/methods/{contract_method_id}"

    def _get_delete_url(self, contract_method_id: str) -> str:
        """Get the URL for deleting a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for deleting a contract method
        """
        return f"/methods/{contract_method_id}"

    def _get_restore_url(self, contract_method_id: str) -> str:
        """Get the URL for restoring a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The URL for restoring a contract method
        """
        return f"/methods/{contract_method_id}/restore"


class SyncContractMethods(BaseContractMethods):
    """Synchronous ContractMethods module for the 1Shot API."""

    def __init__(self, client: "Client") -> None:
        """Initialize the ContractMethods module.

        Args:
            client: The synchronous client instance
        """
        self._client = client

    def test(self, contract_method_id: str, params: Dict[str, Any]) -> ContractMethodTestResult:
        """Test a contract method execution. This method simulates the execution of a contract method. No gas will be spent and nothing on chain will change, but it will let you know whether or not an execution would succeed.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method

        Returns:
            The test result, including success status and potential error information

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "POST",
            self._get_test_url(contract_method_id),
            data={"params": params},
        )
        return ContractMethodTestResult.model_validate(response)

    def estimate(self, contract_method_id: str, params: Dict[str, Any], wallet_id: Optional[str] = None) -> ContractMethodEstimate:
        """Estimate the cost of executing a contract method. Returns data about the fees and amount of gas.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method
            wallet_id: Optional ID of the wallet to use for the estimate

        Returns:
            The cost estimate, including gas amount and fees

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        data: Dict[str, Any] = {"params": params}
        if wallet_id is not None:
            data["walletId"] = wallet_id

        response = self._client._request(
            "POST",
            self._get_estimate_url(contract_method_id),
            data=data,
        )
        return ContractMethodEstimate.model_validate(response)

    def execute(
        self,
        contract_method_id: str,
        params: Dict[str, Any],
        wallet_id: Optional[str] = None,
        memo: Optional[str] = None,
        authorization_list: Optional[List[ERC7702Authorization]] = None,
    ) -> Transaction:
        """Execute a contract method. You can only execute contract methods that are payable or nonpayable. Use /read for view and pure contract methods.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method
            wallet_id: Optional ID of the wallet to use
            memo: Optional memo for the execution. You may include any text you like when you execute a contract method, as a note to yourself about why it was done. This text can be JSON or similar if you want to store formatted data.
            authorization_list: Optional list of ERC-7702 authorizations. If you are using ERC-7702, you must provide at least one authorization.

        Returns:
            The transaction object

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        data: Dict[str, Any] = {"params": params}
        if wallet_id is not None:
            data["walletId"] = wallet_id
        if memo is not None:
            data["memo"] = memo
        if authorization_list is not None:
            data["authorizationList"] = [auth.model_dump(by_alias=True) for auth in authorization_list]

        response = self._client._request(
            "POST",
            self._get_execute_url(contract_method_id),
            data=data,
        )
        return Transaction.model_validate(response)

    def encode(
        self,
        contract_method_id: str,
        params: Dict[str, Any],
        authorization_list: Optional[List[ERC7702Authorization]] = None,
        value: Optional[str] = None,
    ) -> ContractMethodEncodeResult:
        """Encode a contract method to get the transaction data. This method encodes the transaction data for a Contract Method. It returns a hex string of the bytes of the encoded data. This can be used to call the Contract Method directly on the blockchain.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method
            authorization_list: Optional list of ERC-7702 authorizations. If you are using ERC-7702, you must provide at least one authorization.
            value: Optional amount of native token to send along with the contract method

        Returns:
            The encoded transaction data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        data: Dict[str, Any] = {"params": params}
        if authorization_list is not None:
            data["authorizationList"] = [auth.model_dump(by_alias=True) for auth in authorization_list]
        if value is not None:
            data["value"] = value

        response = self._client._request(
            "POST",
            self._get_encode_url(contract_method_id),
            data=data,
        )
        return ContractMethodEncodeResult.model_validate(response)

    def execute_as_delegator(
        self,
        contract_method_id: str,
        params: Dict[str, Any],
        delegator_address: str,
        wallet_id: Optional[str] = None,
        memo: Optional[str] = None,
        value: Optional[str] = None,
    ) -> Transaction:
        """Execute a contract method as a delegator. This method executes the transaction on behalf of the specified delegator address.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method
            delegator_address: The address of the delegator on whose behalf the transaction will be executed
            wallet_id: Optional ID of the wallet to use
            memo: Optional memo for the execution
            value: Optional amount of native token to send along with the contract method

        Returns:
            The transaction object

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        data: Dict[str, Any] = {"params": params, "delegatorAddress": delegator_address}
        if wallet_id is not None:
            data["walletId"] = wallet_id
        if memo is not None:
            data["memo"] = memo
        if value is not None:
            data["value"] = value

        response = self._client._request(
            "POST",
            self._get_execute_as_delegator_url(contract_method_id),
            data=data,
        )
        return Transaction.model_validate(response)

    def read(self, contract_method_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read the result of a view or pure function. This will error on payable and nonpayable contract methods.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method

        Returns:
            The function result

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "POST",
            self._get_read_url(contract_method_id),
            data={"params": params},
        )
        return response

    def get(self, contract_method_id: str) -> ContractMethod:
        """Get a single ContractMethod via its ContractMethodId.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The contract method

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "GET",
            self._get_get_url(contract_method_id),
        )
        return ContractMethod.model_validate(response)

    def list(
        self,
        business_id: str,
        params: Optional[Union[ListContractMethodsParams, Dict[str, Any]]] = None,
    ) -> PagedResponse[ContractMethod]:
        """List contract methods for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters, either as a dict or ListContractMethodsParams instance

        Returns:
            A paged response of contract methods

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if params is not None and not isinstance(params, ListContractMethodsParams):
            params = ListContractMethodsParams.model_validate(params, by_alias=True, by_name=True)
        dumped_params = params.model_dump(mode='json', by_alias=True) if params else None
        url = self._get_list_url(business_id, dumped_params)
        response = self._client._request("GET", url)
        return PagedResponse[ContractMethod].model_validate(response)

    def create(
        self,
        business_id: str,
        params: Union[ContractMethodCreateParams, Dict[str, Any]],
    ) -> ContractMethod:
        """Create a new ContractMethod. A ContractMethod is sometimes referred to as an Endpoint. A ContractMethod corresponds to a single method on a smart contract.

        Args:
            business_id: The business ID
            params: ContractMethod creation parameters, either as a dict or ContractMethodCreateParams instance

        Returns:
            The created contract method

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if not isinstance(params, ContractMethodCreateParams):
            params = ContractMethodCreateParams.model_validate(params, by_alias=True, by_name=True)
        response = self._client._request(
            "POST",
            self._get_create_url(business_id),
            data=params.model_dump(exclude_none=True, by_alias=True),
        )
        return ContractMethod.model_validate(response)

    def import_from_abi(
        self,
        business_id: str,
        params: Dict[str, Any],
    ) -> List[ContractMethod]:
        """Import a complete ethereum ABI and creates ContractMethods for each "function" type entry. Every contract method will be associated with the same Escrow Wallet.

        Args:
            business_id: The business ID
            params: ABI import parameters including:
                - chain_id: The chain ID
                - contractAddress: The contract address
                - escrowWalletId: The escrow wallet ID
                - abi: The Ethereum ABI
                - name: Optional name of the smart contract
                - description: Optional description of the smart contract
                - tags: Optional array of tags for the smart contract

        Returns:
            The imported contract methods

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "POST",
            self._get_import_from_abi_url(business_id),
            data=params,
        )
        return [ContractMethod.model_validate(tx) for tx in response]

    def create_from_contract(
        self,
        business_id: str,
        params: Union[ContractContractMethodsParams, Dict[str, Any]],
    ) -> List[ContractMethod]:
        """Assures that ContractMethods exist for a given contract. This is based on the verified contract ABI and the highest-ranked Contract Description. If ContractMethods already exist, they are not modified. If they do not exist, any methods that are in the Contract Description will be created with the details from the Contract Description.

        Args:
            business_id: The business ID
            params: Contract contract methods parameters, either as a dict or ContractContractMethodsParams instance

        Returns:
            The created contract methods

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if not isinstance(params, ContractContractMethodsParams):
            params = ContractContractMethodsParams.model_validate(params, by_alias=True, by_name=True)
        response = self._client._request(
            "POST",
            self._get_create_contract_methods_from_prompt_url(business_id),
            data=params.model_dump(exclude_none=True, by_alias=True),
        )
        return [ContractMethod.model_validate(tx) for tx in response]

    def search_contracts(
        self,
        params: Union[ContractSearchParams, Dict[str, Any]],
    ) -> List[FullPrompt]:
        """Search for prompts using semantic search.

        Args:
            params: The search parameters

        Returns:
            A list of prompts matching the search criteria

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if not isinstance(params, ContractSearchParams):
            params = ContractSearchParams.model_validate(params, by_alias=True, by_name=True)
        response = self._client._request(
            "POST",
            self._get_contract_search_url(),
            data=params.model_dump(exclude_none=True, by_alias=True),
        )
        return [FullPrompt.model_validate(prompt) for prompt in response]

    def update(
        self,
        contract_method_id: str,
        params: Union[ContractMethodUpdateParams, Dict[str, Any]],
    ) -> ContractMethod:
        """Update a ContractMethod. You can update most of the properties of a contract method via this method, but you can't change the inputs or outputs. Use the Struct API calls for that instead.

        Args:
            contract_method_id: The Contract Method ID
            params: Update parameters, either as a dict or ContractMethodUpdateParams instance

        Returns:
            The updated contract method

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if not isinstance(params, ContractMethodUpdateParams):
            params = ContractMethodUpdateParams.model_validate(params, by_alias=True, by_name=True)
        response = self._client._request(
            "PUT",
            self._get_update_url(contract_method_id),
            data=params.model_dump(exclude_none=True, by_alias=True),
        )
        return ContractMethod.model_validate(response)

    def delete(self, contract_method_id: str) -> None:
        """Delete a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        self._client._request(
            "DELETE",
            self._get_delete_url(contract_method_id),
        )

    def restore(self, contract_method_id: str) -> ContractMethod:
        """Restore a deleted contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The restored contract method

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self._client._request(
            "PUT",
            self._get_restore_url(contract_method_id),
        )
        return ContractMethod.model_validate(response)


class AsyncContractMethods(BaseContractMethods):
    """Asynchronous ContractMethods module for the 1Shot API."""

    def __init__(self, client: "AsyncClient") -> None:
        """Initialize the ContractMethods module.

        Args:
            client: The asynchronous client instance
        """
        self._client = client

    async def test(self, contract_method_id: str, params: Dict[str, Any]) -> ContractMethodTestResult:
        """Test a contract method execution. This method simulates the execution of a contract method. No gas will be spent and nothing on chain will change, but it will let you know whether or not an execution would succeed.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method

        Returns:
            The test result, including success status and potential error information

        Raises:
            aiohttp.ClientError: If the request fails
        """
        response = await self._client._request(
            "POST",
            self._get_test_url(contract_method_id),
            data={"params": params},
        )
        return ContractMethodTestResult.model_validate(response)

    async def estimate(self, contract_method_id: str, params: Dict[str, Any]) -> ContractMethodEstimate:
        """Estimate the cost of executing a contract method. Returns data about the fees and amount of gas.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method

        Returns:
            The cost estimate, including gas amount and fees

        Raises:
            aiohttp.ClientError: If the request fails
        """
        data: Dict[str, Any] = {"params": params}

        response = await self._client._request(
            "POST",
            self._get_estimate_url(contract_method_id),
            data=data,
        )
        return ContractMethodEstimate.model_validate(response)

    async def execute(
        self,
        contract_method_id: str,
        params: Dict[str, Any],
        wallet_id: Optional[str] = None,
        memo: Optional[str] = None,
        authorization_list: Optional[List[ERC7702Authorization]] = None,
    ) -> Transaction:
        """Execute a contract method. You can only execute contract methods that are payable or nonpayable. Use /read for view and pure contract methods.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method
            wallet_id: Optional ID of the wallet to use
            memo: Optional memo for the execution. You may include any text you like when you execute a contract method, as a note to yourself about why it was done. This text can be JSON or similar if you want to store formatted data.
            authorization_list: Optional list of ERC-7702 authorizations. If you are using ERC-7702, you must provide at least one authorization.

        Returns:
            The transaction object

        Raises:
            aiohttp.ClientError: If the request fails
        """
        data: Dict[str, Any] = {"params": params}
        if wallet_id is not None:
            data["walletId"] = wallet_id
        if memo is not None:
            data["memo"] = memo
        if authorization_list is not None:
            data["authorizationList"] = [auth.model_dump(by_alias=True) for auth in authorization_list]

        response = await self._client._request(
            "POST",
            self._get_execute_url(contract_method_id),
            data=data,
        )
        return Transaction.model_validate(response)

    async def encode(
        self,
        contract_method_id: str,
        params: Dict[str, Any],
        authorization_list: Optional[List[ERC7702Authorization]] = None,
        value: Optional[str] = None,
    ) -> ContractMethodEncodeResult:
        """Encode a contract method to get the transaction data. This method encodes the transaction data for a Contract Method. It returns a hex string of the bytes of the encoded data. This can be used to call the Contract Method directly on the blockchain.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method
            authorization_list: Optional list of ERC-7702 authorizations. If you are using ERC-7702, you must provide at least one authorization.
            value: Optional amount of native token to send along with the contract method

        Returns:
            The encoded transaction data

        Raises:
            aiohttp.ClientError: If the request fails
        """
        data: Dict[str, Any] = {"params": params}
        if authorization_list is not None:
            data["authorizationList"] = [auth.model_dump(by_alias=True) for auth in authorization_list]
        if value is not None:
            data["value"] = value

        response = await self._client._request(
            "POST",
            self._get_encode_url(contract_method_id),
            data=data,
        )
        return ContractMethodEncodeResult.model_validate(response)

    async def execute_as_delegator(
        self,
        contract_method_id: str,
        params: Dict[str, Any],
        delegator_address: str,
        wallet_id: Optional[str] = None,
        memo: Optional[str] = None,
        value: Optional[str] = None,
    ) -> Transaction:
        """Execute a contract method as a delegator. This method executes the transaction on behalf of the specified delegator address.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method
            delegator_address: The address of the delegator on whose behalf the transaction will be executed
            wallet_id: Optional ID of the wallet to use
            memo: Optional memo for the execution
            value: Optional amount of native token to send along with the contract method

        Returns:
            The transaction object

        Raises:
            aiohttp.ClientError: If the request fails
        """
        data: Dict[str, Any] = {"params": params, "delegatorAddress": delegator_address}
        if wallet_id is not None:
            data["walletId"] = wallet_id
        if memo is not None:
            data["memo"] = memo
        if value is not None:
            data["value"] = value

        response = await self._client._request(
            "POST",
            self._get_execute_as_delegator_url(contract_method_id),
            data=data,
        )
        return Transaction.model_validate(response)

    async def read(self, contract_method_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read the result of a view or pure function. This will error on payable and nonpayable contract methods.

        Args:
            contract_method_id: The Contract Method ID
            params: Parameters for the contract method

        Returns:
            The function result

        Raises:
            aiohttp.ClientError: If the request fails
        """
        response = await self._client._request(
            "POST",
            self._get_read_url(contract_method_id),
            data={"params": params},
        )
        return response

    async def get(self, contract_method_id: str) -> ContractMethod:
        """Get a single ContractMethod via its ContractMethodId.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The contract method

        Raises:
            aiohttp.ClientError: If the request fails
        """
        response = await self._client._request(
            "GET",
            self._get_get_url(contract_method_id),
        )
        return ContractMethod.model_validate(response)

    async def list(
        self,
        business_id: str,
        params: Optional[Union[ListContractMethodsParams, Dict[str, Any]]] = None,
    ) -> PagedResponse[ContractMethod]:
        """List contract methods for a business.

        Args:
            business_id: The business ID
            params: Optional filter parameters, either as a dict or ListContractMethodsParams instance

        Returns:
            A paged response of contract methods

        Raises:
            aiohttp.ClientError: If the request fails
        """
        if params is not None and not isinstance(params, ListContractMethodsParams):
            params = ListContractMethodsParams.model_validate(params, by_alias=True, by_name=True)
        dumped_params = params.model_dump(mode='json', by_alias=True) if params else None
        url = self._get_list_url(business_id, dumped_params)
        response = await self._client._request("GET", url)
        return PagedResponse[ContractMethod].model_validate(response)

    async def create(
        self,
        business_id: str,
        params: Union[ContractMethodCreateParams, Dict[str, Any]],
    ) -> ContractMethod:
        """Create a new ContractMethod. A ContractMethod is sometimes referred to as an Endpoint. A ContractMethod corresponds to a single method on a smart contract.

        Args:
            business_id: The business ID
            params: ContractMethod creation parameters, either as a dict or ContractMethodCreateParams instance

        Returns:
            The created contract method

        Raises:
            aiohttp.ClientError: If the request fails
        """
        if not isinstance(params, ContractMethodCreateParams):
            params = ContractMethodCreateParams.model_validate(params, by_alias=True, by_name=True)
        response = await self._client._request(
            "POST",
            self._get_create_url(business_id),
            data=params.model_dump(exclude_none=True, by_alias=True),
        )
        return ContractMethod.model_validate(response)

    async def import_from_abi(
        self,
        business_id: str,
        params: Dict[str, Any],
    ) -> List[ContractMethod]:
        """Import a complete ethereum ABI and creates ContractMethods for each "function" type entry. Every contract method will be associated with the same Escrow Wallet.

        Args:
            business_id: The business ID
            params: ABI import parameters including:
                - chain_id: The chain ID
                - contractAddress: The contract address
                - escrowWalletId: The escrow wallet ID
                - abi: The Ethereum ABI
                - name: Optional name of the smart contract
                - description: Optional description of the smart contract
                - tags: Optional array of tags for the smart contract

        Returns:
            The imported contract methods

        Raises:
            aiohttp.ClientError: If the request fails
        """
        response = await self._client._request(
            "POST",
            self._get_import_from_abi_url(business_id),
            data=params,
        )
        return [ContractMethod.model_validate(tx) for tx in response]

    async def create_from_contract(
        self,
        business_id: str,
        params: Union[ContractContractMethodsParams, Dict[str, Any]],
    ) -> List[ContractMethod]:
        """Assures that ContractMethods exist for a given contract. This is based on the verified contract ABI and the highest-ranked Contract Description. If ContractMethods already exist, they are not modified. If they do not exist, any methods that are in the Contract Description will be created with the details from the Contract Description.

        Args:
            business_id: The business ID
            params: Contract contract methods parameters, either as a dict or ContractContractMethodsParams instance

        Returns:
            The created contract methods

        Raises:
            aiohttp.ClientError: If the request fails
        """
        if not isinstance(params, ContractContractMethodsParams):
            params = ContractContractMethodsParams.model_validate(params, by_alias=True, by_name=True)
        response = await self._client._request(
            "POST",
            self._get_create_contract_methods_from_prompt_url(business_id),
            data=params.model_dump(exclude_none=True, by_alias=True),
        )
        return [ContractMethod.model_validate(tx) for tx in response]

    async def search_contracts(
        self,
        params: Union[ContractSearchParams, Dict[str, Any]],
    ) -> List[FullPrompt]:
        """Search for prompts using semantic search.

        Args:
            params: The search parameters

        Returns:
            A list of prompts matching the search criteria

        Raises:
            aiohttp.ClientError: If the request fails
        """
        if not isinstance(params, ContractSearchParams):
            params = ContractSearchParams.model_validate(params, by_alias=True, by_name=True)
        response = await self._client._request(
            "POST",
            self._get_contract_search_url(),
            data=params.model_dump(exclude_none=True, by_alias=True),
        )
        return [FullPrompt.model_validate(prompt) for prompt in response]

    async def update(
        self,
        contract_method_id: str,
        params: Union[ContractMethodUpdateParams, Dict[str, Any]],
    ) -> ContractMethod:
        """Update a ContractMethod. You can update most of the properties of a contract method via this method, but you can't change the inputs or outputs. Use the Struct API calls for that instead.

        Args:
            contract_method_id: The Contract Method ID
            params: Update parameters, either as a dict or ContractMethodUpdateParams instance

        Returns:
            The updated contract method

        Raises:
            aiohttp.ClientError: If the request fails
        """
        if not isinstance(params, ContractMethodUpdateParams):
            params = ContractMethodUpdateParams.model_validate(params, by_alias=True, by_name=True)
        response = await self._client._request(
            "PUT",
            self._get_update_url(contract_method_id),
            data=params.model_dump(exclude_none=True, by_alias=True),
        )
        return ContractMethod.model_validate(response)

    async def delete(self, contract_method_id: str) -> None:
        """Delete a contract method.

        Args:
            contract_method_id: The Contract Method ID

        Raises:
            aiohttp.ClientError: If the request fails
        """
        await self._client._request(
            "DELETE",
            self._get_delete_url(contract_method_id),
        )

    async def restore(self, contract_method_id: str) -> ContractMethod:
        """Restore a deleted contract method.

        Args:
            contract_method_id: The Contract Method ID

        Returns:
            The restored contract method

        Raises:
            aiohttp.ClientError: If the request fails
        """
        response = await self._client._request(
            "PUT",
            self._get_restore_url(contract_method_id),
        )
        return ContractMethod.model_validate(response) 