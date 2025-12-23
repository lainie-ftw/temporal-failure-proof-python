import requests
from dataclasses import dataclass
from temporalio import activity

# Account API base URL
API_BASE_URL = "http://workshop-host:5000"


@dataclass
class CheckBalanceInput:
    """Input for check_balance activity."""
    account_id: str


@dataclass
class WithdrawInput:
    """Input for withdraw activity."""
    account_id: str
    amount: float


@dataclass
class DepositInput:
    """Input for deposit activity."""
    account_id: str
    amount: float


@dataclass
class BalanceResult:
    """Result from check_balance activity."""
    account_id: str
    balance: float


@dataclass
class TransactionResult:
    """Result from withdraw or deposit activities."""
    account_id: str
    previous_balance: float
    new_balance: float
    amount: float


@activity.defn
async def check_balance(input: CheckBalanceInput) -> BalanceResult:
    """
    Check the balance of an account.
    
    Args:
        input: CheckBalanceInput containing account_id
        
    Returns:
        BalanceResult with account_id and current balance
        
    Raises:
        Exception: If the API request fails
    """
    activity.logger.info(f"Checking balance of {input.account_id}...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/accounts/{input.account_id}"
        )
        response.raise_for_status()
        balance = response.json()['balance']
        
        activity.logger.info(f"✓ {input.account_id} balance: ${balance:.2f}")
        
        return BalanceResult(
            account_id=input.account_id,
            balance=balance
        )
    except requests.exceptions.RequestException as e:
        activity.logger.error(f"✗ Error checking {input.account_id} balance: {e}")
        raise


@activity.defn
async def withdraw(input: WithdrawInput) -> TransactionResult:
    """
    Withdraw money from an account.
    
    Args:
        input: WithdrawInput containing account_id and amount
        
    Returns:
        TransactionResult with transaction details
        
    Raises:
        Exception: If the API request fails or insufficient funds
    """
    activity.logger.info(f"Withdrawing ${input.amount:.2f} from {input.account_id}...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/accounts/{input.account_id}/withdraw",
            json={"amount": input.amount},
        )
        response.raise_for_status()
        result = response.json()
        
        activity.logger.info(f"✓ Withdrawal successful")
        activity.logger.info(f"  Previous balance: ${result['previous_balance']:.2f}")
        activity.logger.info(f"  New balance: ${result['new_balance']:.2f}")
        
        return TransactionResult(
            account_id=input.account_id,
            previous_balance=result['previous_balance'],
            new_balance=result['new_balance'],
            amount=input.amount
        )
    except requests.exceptions.RequestException as e:
        activity.logger.error(f"✗ Error withdrawing from {input.account_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            activity.logger.error(f"  Response: {e.response.text}")
        raise


@activity.defn
async def deposit(input: DepositInput) -> TransactionResult:
    """
    Deposit money to an account.
    
    Args:
        input: DepositInput containing account_id and amount
        
    Returns:
        TransactionResult with transaction details
        
    Raises:
        Exception: If the API request fails
    """
    activity.logger.info(f"Depositing ${input.amount:.2f} to {input.account_id}...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/accounts/{input.account_id}/deposit",
            json={"amount": input.amount},
        )
        response.raise_for_status()
        result = response.json()
        
        activity.logger.info(f"✓ Deposit successful")
        activity.logger.info(f"  Previous balance: ${result['previous_balance']:.2f}")
        activity.logger.info(f"  New balance: ${result['new_balance']:.2f}")
        
        return TransactionResult(
            account_id=input.account_id,
            previous_balance=result['previous_balance'],
            new_balance=result['new_balance'],
            amount=input.amount
        )
    except requests.exceptions.RequestException as e:
        activity.logger.error(f"✗ Error depositing to {input.account_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            activity.logger.error(f"  Response: {e.response.text}")
        raise
