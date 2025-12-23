import requests
import sys
import time

# Account API base URL
API_BASE_URL = "http://workshop-host:5000"

# Retry configuration
MAX_RETRIES = 3
BASE_RETRY_DELAY = 1  # seconds
REQUEST_TIMEOUT = 5  # seconds per request


def retry_api_call(operation, operation_description, max_retries=MAX_RETRIES, base_delay=BASE_RETRY_DELAY):
    """
    Retry an API call with exponential backoff.
    
    Args:
        operation: A callable that performs the API request
        operation_description: Description of the operation for logging
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
    
    Returns:
        The result of the successful operation
    
    Raises:
        The last exception if all retries are exhausted
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return operation()
        except requests.exceptions.RequestException as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                print(f"    ⟳ Retry attempt {attempt + 1}/{max_retries} for {operation_description} after {delay}s...")
                time.sleep(delay)
            else:
                # All retries exhausted
                print(f"    ✗ All retry attempts exhausted for {operation_description}")
    
    # Raise the last exception if all retries failed
    raise last_exception


def move_money(from_account, to_account, amount):
    """
    Move money from one account to another.
    
    This is a naive implementation that demonstrates the fragility of
    distributed transactions without proper orchestration.
    """
    print(f"\n{'='*60}")
    print(f"Starting money transfer: ${amount:.2f} from {from_account} to {to_account}")
    print(f"{'='*60}\n")
    
    # Step 1: Check balance of source account
    print(f"Step 1: Checking balance of {from_account}...")
    try:
        def check_from_balance():
            response = requests.get(f"{API_BASE_URL}/accounts/{from_account}", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        
        response = retry_api_call(check_from_balance, f"checking {from_account} balance")
        from_balance = response.json()['balance']
        print(f"  ✓ {from_account} balance: ${from_balance:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error checking {from_account} balance: {e}")
        return False
    
    # Step 2: Check balance of destination account
    print(f"\nStep 2: Checking balance of {to_account}...")
    try:
        def check_to_balance():
            response = requests.get(f"{API_BASE_URL}/accounts/{to_account}", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        
        response = retry_api_call(check_to_balance, f"checking {to_account} balance")
        to_balance = response.json()['balance']
        print(f"  ✓ {to_account} balance: ${to_balance:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error checking {to_account} balance: {e}")
        return False
    
    # Step 3: Withdraw from source account
    print(f"\nStep 3: Withdrawing ${amount:.2f} from {from_account}...")
    try:
        def withdraw_operation():
            response = requests.post(
                f"{API_BASE_URL}/accounts/{from_account}/withdraw",
                json={"amount": amount},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response
        
        response = retry_api_call(withdraw_operation, f"withdrawing from {from_account}")
        result = response.json()
        print(f"  ✓ Withdrawal successful")
        print(f"    Previous balance: ${result['previous_balance']:.2f}")
        print(f"    New balance: ${result['new_balance']:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error withdrawing from {from_account}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"    Response: {e.response.json()}")
        return False
    
    # Step 4: Deposit to destination account
    print(f"\nStep 4: Depositing ${amount:.2f} to {to_account}...")
    try:
        def deposit_operation():
            response = requests.post(
                f"{API_BASE_URL}/accounts/{to_account}/deposit",
                json={"amount": amount},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response
        
        response = retry_api_call(deposit_operation, f"depositing to {to_account}")
        result = response.json()
        print(f"  ✓ Deposit successful")
        print(f"    Previous balance: ${result['previous_balance']:.2f}")
        print(f"    New balance: ${result['new_balance']:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error depositing to {to_account}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"    Response: {e.response.json()}")
        print(f"\n  ⚠️  WARNING: Money was withdrawn from {from_account} but not deposited!")
        print(f"  ⚠️  This is a partial failure - money may be lost!")
        return False
    
    # Success!
    print(f"\n{'='*60}")
    print(f"✓ Transfer complete!")
    print(f"{'='*60}\n")
    
    # Show final balances
    print("Final balances:")
    try:
        def get_from_final_balance():
            response = requests.get(f"{API_BASE_URL}/accounts/{from_account}", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        
        response = retry_api_call(get_from_final_balance, f"retrieving {from_account} final balance")
        print(f"  {from_account}: ${response.json()['balance']:.2f}")
        
        def get_to_final_balance():
            response = requests.get(f"{API_BASE_URL}/accounts/{to_account}", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        
        response = retry_api_call(get_to_final_balance, f"retrieving {to_account} final balance")
        print(f"  {to_account}: ${response.json()['balance']:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  Error retrieving final balances: {e}")
    
    return True


def main():
    # Check if API is running
    print("Checking if Account API is running...")
    try:
        def health_check():
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            response.raise_for_status()
            return response
        
        retry_api_call(health_check, "health check")
        print("✓ Account API is running\n")
    except requests.exceptions.RequestException as e:
        print(f"✗ Account API is not running!")
        print(f"  Please start the API first: python account_api.py")
        sys.exit(1)
    
    # Transfer $100 from account_A to account_B
    success = move_money("account_A", "account_B", 100.00)
    
    if success:
        print("\n✓ Money transfer completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Money transfer failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
