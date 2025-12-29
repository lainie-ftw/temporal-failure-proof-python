#!/usr/bin/env python3
"""
Reset the accounts database to initial state.

This script resets the accounts.json file to its original values,
useful for running multiple demonstrations in a workshop setting.
"""

import json
from pathlib import Path

# Path to our fake database
DB_FILE = Path(__file__).parent / "accounts.json"

# Initial account state
INITIAL_STATE = {
    "account_A": {
        "balance": 1000.00
    },
    "account_B": {
        "balance": 500.00
    }
}


def reset_database():
    """Reset the accounts database to initial state."""
    print("Resetting accounts database...")
    
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(INITIAL_STATE, f, indent=2)
        
        print("✓ Database reset successfully!")
        print("\nCurrent account balances:")
        print(f"  account_A: ${INITIAL_STATE['account_A']['balance']:.2f}")
        print(f"  account_B: ${INITIAL_STATE['account_B']['balance']:.2f}")
        
    except Exception as e:
        print(f"✗ Error resetting database: {e}")
        return False
    
    return True


if __name__ == "__main__":
    reset_database()
