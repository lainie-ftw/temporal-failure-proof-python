import requests
import sys

# Account API base URL
API_BASE_URL = "http://127.0.0.1:5000"


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
        response = requests.get(f"{API_BASE_URL}/accounts/{from_account}")
        response.raise_for_status()
        from_balance = response.json()['balance']
        print(f"  ✓ {from_account} balance: ${from_balance:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error checking {from_account} balance: {e}")
        return False
    
    # Step 2: Check balance of destination account
    print(f"\nStep 2: Checking balance of {to_account}...")
    try:
        response = requests.get(f"{API_BASE_URL}/accounts/{to_account}")
        response.raise_for_status()
        to_balance = response.json()['balance']
        print(f"  ✓ {to_account} balance: ${to_balance:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error checking {to_account} balance: {e}")
        return False
    
    # Step 3: Withdraw from source account
    print(f"\nStep 3: Withdrawing ${amount:.2f} from {from_account}...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/accounts/{from_account}/withdraw",
            json={"amount": amount}
        )
        response.raise_for_status()
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
        response = requests.post(
            f"{API_BASE_URL}/accounts/{to_account}/deposit",
            json={"amount": amount}
        )
        response.raise_for_status()
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
        response = requests.get(f"{API_BASE_URL}/accounts/{from_account}")
        response.raise_for_status()
        print(f"  {from_account}: ${response.json()['balance']:.2f}")
        
        response = requests.get(f"{API_BASE_URL}/accounts/{to_account}")
        response.raise_for_status()
        print(f"  {to_account}: ${response.json()['balance']:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  Error retrieving final balances: {e}")
    
    return True


def main():
    # Check if API is running
    print("Checking if Account API is running...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        response.raise_for_status()
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
