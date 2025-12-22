import json
import os
from pathlib import Path
from flask import Flask, jsonify, request
from threading import Lock

app = Flask(__name__)

# Path to our fake database
DB_FILE = Path(__file__).parent / "accounts.json"

# Lock for thread-safe file operations
db_lock = Lock()


def read_accounts():
    """Read accounts from JSON file."""
    with db_lock:
        with open(DB_FILE, 'r') as f:
            return json.load(f)


def write_accounts(accounts):
    """Write accounts to JSON file."""
    with db_lock:
        with open(DB_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)


@app.route('/accounts/<account_number>', methods=['GET'])
def get_account(account_number):
    """Get account balance."""
    accounts = read_accounts()
    
    if account_number not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    return jsonify({
        "account_number": account_number,
        "balance": accounts[account_number]["balance"]
    }), 200


@app.route('/accounts/<account_number>/withdraw', methods=['POST'])
def withdraw(account_number):
    """Withdraw money from account."""
    data = request.get_json()
    
    if not data or 'amount' not in data:
        return jsonify({"error": "Amount is required"}), 400
    
    amount = data['amount']
    
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    
    accounts = read_accounts()
    
    if account_number not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    current_balance = accounts[account_number]["balance"]
    
    if current_balance < amount:
        return jsonify({
            "error": "Insufficient funds",
            "current_balance": current_balance,
            "requested_amount": amount
        }), 400
    
    # Perform withdrawal
    accounts[account_number]["balance"] = current_balance - amount
    write_accounts(accounts)
    
    return jsonify({
        "account_number": account_number,
        "previous_balance": current_balance,
        "amount_withdrawn": amount,
        "new_balance": accounts[account_number]["balance"]
    }), 200


@app.route('/accounts/<account_number>/deposit', methods=['POST'])
def deposit(account_number):
    """Deposit money to account."""
    data = request.get_json()
    
    if not data or 'amount' not in data:
        return jsonify({"error": "Amount is required"}), 400
    
    amount = data['amount']
    
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    
    accounts = read_accounts()
    
    if account_number not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    current_balance = accounts[account_number]["balance"]
    
    # Perform deposit
    accounts[account_number]["balance"] = current_balance + amount
    write_accounts(accounts)
    
    return jsonify({
        "account_number": account_number,
        "previous_balance": current_balance,
        "amount_deposited": amount,
        "new_balance": accounts[account_number]["balance"]
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    print("Starting Account API service on http://localhost:5000")
    print("Endpoints:")
    print("  GET  /accounts/<account_number>")
    print("  POST /accounts/<account_number>/withdraw")
    print("  POST /accounts/<account_number>/deposit")
    print("  GET  /health")
    app.run(host='0.0.0.0', port=5000, debug=True)
