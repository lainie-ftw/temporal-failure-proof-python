# Module 02: Money Transfer with Temporal

This module demonstrates converting a fragile distributed transaction (money transfer between accounts) into a robust Temporal workflow.

## Files

### Original Implementation
- **`move_money.py`** - Original naive implementation showing fragility of distributed transactions
- **`move_money_retries.py`** - Version with manual retry logic
- **`account_api.py`** - Mock banking API that the workflows interact with
- **`accounts.json`** - Database file for account balances
- **`reset_db.py`** - Utility to reset account balances

### Temporal Workflow Implementation
- **`activities.py`** - Temporal activities for account operations (check_balance, withdraw, deposit) with data classes
- **`workflow.py`** - MoneyTransferWorkflow that orchestrates the money transfer process
- **`worker.py`** - Standalone worker that processes workflows
- **`run_workflow.py`** - Script to run the workflow (includes embedded worker)

## How to Run

### Prerequisites
1. **Start Temporal Server** (if not already running):
   ```bash
   temporal server start-dev
   ```

2. **Start the Account API** (in a separate terminal):
   ```bash
   cd exercises/module02
   python account_api.py
   ```

### Option 1: Run with Embedded Worker
This starts a worker and executes the workflow in one command:
```bash
cd exercises/module02
python run_workflow.py
```

### Option 2: Run Worker Separately
Start the worker in one terminal:
```bash
cd exercises/module02
python worker.py
```

Then trigger workflows from another terminal or through the Temporal UI.

## Workflow Details

### Input Data Class
```python
MoneyTransferInput(
    from_account: str,
    to_account: str,
    amount: float
)
```

### Output Data Class
```python
MoneyTransferResult(
    success: bool,
    from_account: str,
    to_account: str,
    amount: float,
    from_account_final_balance: float,
    to_account_final_balance: float,
    error_message: str = ""
)
```

### Activities
All activities use data classes for inputs:
- **`check_balance(CheckBalanceInput)`** - Returns `BalanceResult`
- **`withdraw(WithdrawInput)`** - Returns `TransactionResult`
- **`deposit(DepositInput)`** - Returns `TransactionResult`

## Benefits of Temporal Implementation

Compared to the original `move_money.py`:

1. **Automatic Retries**: Activities automatically retry on transient failures without manual retry logic
2. **Durability**: Workflow state is persisted - survives process crashes
3. **Visibility**: Full execution history viewable in Temporal UI at http://localhost:8233
4. **No Lost Money**: Temporal tracks workflow state, preventing partial failures
5. **Timeouts**: Built-in timeout handling for each activity (10 seconds)
6. **Type Safety**: Data classes provide clear contracts between workflow and activities

## Testing

### Reset Account Balances
```bash
cd exercises/module02
python reset_db.py
```

### View in Temporal UI
Navigate to http://localhost:8233 to see:
- Workflow execution history
- Activity attempts and results
- Timing information
- Full audit trail
