from datetime import timedelta
from dataclasses import dataclass

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import (
        check_balance,
        withdraw,
        deposit,
        CheckBalanceInput,
        WithdrawInput,
        DepositInput,
    )


@dataclass
class MoneyTransferInput:
    """Input for MoneyTransferWorkflow."""
    from_account: str
    to_account: str
    amount: float


@dataclass
class MoneyTransferResult:
    """Result from MoneyTransferWorkflow."""
    success: bool
    from_account: str
    to_account: str
    amount: float
    from_account_starting_balance: float
    to_account_starting_balance: float
    from_account_final_balance: float
    to_account_final_balance: float
    error_message: str = ""


@workflow.defn
class MoneyTransferWorkflow:
    """
    Workflow for transferring money between accounts.
    
    This workflow orchestrates the money transfer process using Temporal,
    which provides automatic retries, durability, and visibility into the
    transfer process.
    """
    
    @workflow.run
    async def run(self, input: MoneyTransferInput) -> MoneyTransferResult:
        """
        Execute the money transfer workflow.
        
        Args:
            input: MoneyTransferInput containing from_account, to_account, and amount
            
        Returns:
            MoneyTransferResult with success status and final balances
        """
        workflow.logger.info(
            f"Starting money transfer: ${input.amount:.2f} from "
            f"{input.from_account} to {input.to_account}"
        )
        
        # Step 1: Check balance of source account
        workflow.logger.info(f"Step 1: Checking balance of {input.from_account}...")
        from_balance_result = await workflow.execute_activity(
            check_balance,
            CheckBalanceInput(account_id=input.from_account),
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(
            f"Source account balance: ${from_balance_result.balance:.2f}"
        )
        
        # Step 2: Check balance of destination account
        workflow.logger.info(f"Step 2: Checking balance of {input.to_account}...")
        to_balance_result = await workflow.execute_activity(
            check_balance,
            CheckBalanceInput(account_id=input.to_account),
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(
            f"Destination account balance: ${to_balance_result.balance:.2f}"
        )
        
        # Step 3: Withdraw from source account
        workflow.logger.info(
            f"Step 3: Withdrawing ${input.amount:.2f} from {input.from_account}..."
        )
        withdraw_result = await workflow.execute_activity(
            withdraw,
            WithdrawInput(account_id=input.from_account, amount=input.amount),
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(
            f"Withdrawal successful. New balance: ${withdraw_result.new_balance:.2f}"
        )
        
        # Step 4: Deposit to destination account
        workflow.logger.info(
            f"Step 4: Depositing ${input.amount:.2f} to {input.to_account}..."
        )
        deposit_result = await workflow.execute_activity(
            deposit,
            DepositInput(account_id=input.to_account, amount=input.amount),
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(
            f"Deposit successful. New balance: ${deposit_result.new_balance:.2f}"
        )
        
        # Step 5: Get final balances
        workflow.logger.info("Step 5: Retrieving final balances...")
        final_from_balance = await workflow.execute_activity(
            check_balance,
            CheckBalanceInput(account_id=input.from_account),
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        final_to_balance = await workflow.execute_activity(
            check_balance,
            CheckBalanceInput(account_id=input.to_account),
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        workflow.logger.info("✓ Transfer complete!")
        
        return MoneyTransferResult(
            success=True,
            from_account=input.from_account,
            to_account=input.to_account,
            amount=input.amount,
            from_account_starting_balance=from_balance_result.balance,
            to_account_starting_balance=to_balance_result.balance,
            from_account_final_balance=final_from_balance.balance,
            to_account_final_balance=final_to_balance.balance,
        )
