"""Wallet models for the 1Shot API."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class AccountBalanceDetails(BaseModel):
    """Account balance details model."""

    type: int = Field(..., description="The chain technology type")
    ticker: str = Field(..., description="The token ticker")
    chain_id: int = Field(..., alias="chainId", description="The chain ID")
    token_address: str = Field(..., alias="tokenAddress", description="The token address")
    account_address: str = Field(..., alias="accountAddress", description="The account address")
    balance: str = Field(..., description="The balance of the token as a Big Number String")
    decimals: int = Field(..., description="The number of decimals in the balance. Determined by the token type.")


class Wallet(BaseModel):
    """Wallet stored by chain service"""

    id: str = Field(..., description="internal ID of the wallet object")
    account_address: str = Field(..., alias="accountAddress", description="string address of a wallet insight platform holds keys for")
    business_id: Optional[str] = Field(None, alias="businessId", description="The business ID that owns this wallet. Admin wallets will not have this value. An wallet will have either a user ID or a business ID.")
    user_id: Optional[str] = Field(None, alias="userId", description="The User ID of the person that owns this wallet. Admin wallets will not have this value. An wallet will have either a user ID or a business ID.")
    chain_id: int = Field(..., alias="chainId", description="The chain ID")
    name: str = Field(..., description="The name of the wallet.")
    description: Optional[str] = Field(None, description="Optional description of the wallet, can be used to describe it's purpose.")
    is_admin: bool = Field(..., alias="isAdmin", description="Whether or not the wallet is an admin wallet, used for internal purposes.")
    account_balance_details: Optional[AccountBalanceDetails] = Field(
        None, 
        alias="accountBalanceDetails", 
        description="The account balance details"
    )
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp")


class WalletListParams(BaseModel):
    """Parameters for listing wallets."""

    chain_id: Optional[int] = Field(None, alias="chainId", description="The specific chain to get the wallets for")
    page_size: Optional[int] = Field(None, alias="pageSize", description="The size of the page to return. Defaults to 25")
    page: Optional[int] = Field(None, description="Which page to return. This is 1 indexed, and default to the first page, 1")
    name: Optional[str] = Field(None, description="Filters on the name of the wallet.")

    @validator('page')
    def validate_page(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page number must be greater than or equal to 1')
        return v

    @validator('page_size')
    def validate_page_size(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page size must be greater than or equal to 1')
        return v


class WalletCreateParams(BaseModel):
    """Parameters for creating a wallet."""

    chain_id: int = Field(..., alias="chainId", description="The chain ID to create the wallet on")
    name: str = Field(..., description="The name of the wallet")
    description: Optional[str] = Field(None, description="A description of the wallet, such as it's intended use. This is for reference only.")


class WalletUpdateParams(BaseModel):
    """Parameters for updating a wallet."""

    name: Optional[str] = Field(None, description="The name of the wallet")
    description: Optional[str] = Field(None, description="Optional description of the wallet, can be used to describe it's purpose")


class Delegation(BaseModel):
    """Delegation model."""

    id: str = Field(..., description="Internal ID of the delegation")
    business_id: str = Field(..., alias="businessId", description="ID of the business that owns this delegation")
    escrow_wallet_id: str = Field(..., alias="escrowWalletId", description="ID of the escrow wallet that can execute transactions")
    delegator_address: str = Field(..., alias="delegatorAddress", description="The address of the delegator account")
    start_time: Optional[int] = Field(None, alias="startTime", description="The start time for the delegation. If null, the delegation starts immediately")
    end_time: Optional[int] = Field(None, alias="endTime", description="The end time for the delegation. If null, the delegation has no expiration")
    contract_addresses: List[str] = Field(..., alias="contractAddresses", description="Array of contract addresses that the wallet can execute transactions for")
    methods: List[str] = Field(..., description="Array of method names that the wallet can execute. If empty, all methods are allowed")
    delegation_data: str = Field(..., alias="delegationData", description="The actual Delegation object serialized as a JSON string. BigInts must be encoded as strings")
    updated: int = Field(..., description="The last update timestamp")
    created: int = Field(..., description="The creation timestamp")


class DelegationListParams(BaseModel):
    """Parameters for listing delegations."""

    page_size: Optional[int] = Field(None, alias="pageSize", description="The size of the page to return. Defaults to 25")
    page: Optional[int] = Field(None, description="Which page to return. This is 1 indexed, and default to the first page, 1")

    @validator('page')
    def validate_page(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page number must be greater than or equal to 1')
        return v

    @validator('page_size')
    def validate_page_size(cls, v):
        if v is not None and v < 1:
            raise ValueError('Page size must be greater than or equal to 1')
        return v


class DelegationCreateParams(BaseModel):
    """Parameters for creating a delegation."""

    start_time: Optional[int] = Field(None, alias="startTime", description="The start time for the delegation. If not provided, the delegation starts immediately")
    end_time: Optional[int] = Field(None, alias="endTime", description="The end time for the delegation. If not provided, the delegation has no expiration")
    contract_addresses: Optional[List[str]] = Field(None, alias="contractAddresses", description="Array of contract addresses that the wallet can execute transactions for")
    methods: Optional[List[str]] = Field(None, description="Array of method names that the wallet can execute. If empty, all methods are allowed")
    delegation_data: str = Field(..., alias="delegationData", description="The actual Delegation object serialized as a JSON string. BigInts must be encoded as strings")


class WalletTransferParams(BaseModel):
    """Parameters for transferring native tokens from a wallet."""

    destination_account_address: str = Field(..., alias="destinationAccountAddress", description="The destination account address")
    transfer_amount: Optional[str] = Field(None, alias="transferAmount", description="The amount of native token to transfer. This is the 'value' parameter in the actual transaction. If you omit this parameter, 1Shot API will calculate the maximum amount of token that you can transfer, getting as close to zeroing out the Wallet as possible")
    memo: Optional[str] = Field(None, description="An optional memo for the transfer")