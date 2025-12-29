#!/usr/bin/env python3
"""
Money Transfer API - Web UI and Workflow Management

This Flask application provides:
- Web UI for interacting with the money transfer system
- API endpoints for managing transfers and workflows
- Integration with Temporal for workflow orchestration
- Real World Mode toggle functionality
"""

import asyncio
import time
import uuid
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import requests

# Temporal imports
from temporalio.client import Client, WorkflowExecutionStatus
from workflow import MoneyTransferWorkflow, MoneyTransferInput

app = Flask(__name__)

# Configuration
TEMPORAL_SERVER = "localhost:7233"
TASK_QUEUE = "money-transfer-task-queue"
ACCOUNT_API_URL = "http://127.0.0.1:5000"
ACCOUNT_API_FILE = Path(__file__).parent / "account_api.py"

# State management
temporal_client = None


# ============================================================================
# Temporal Client Management
# ============================================================================

async def get_temporal_client():
    """Get or create Temporal client connection."""
    global temporal_client
    if temporal_client is None:
        try:
            temporal_client = await Client.connect(TEMPORAL_SERVER)
        except Exception as e:
            print(f"Error connecting to Temporal: {e}")
            raise
    return temporal_client


def run_async(coro):
    """Helper to run async code in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================================================
# Workflow Management
# ============================================================================

async def start_workflow_async(from_account, to_account, amount):
    """Start a money transfer workflow."""
    client = await get_temporal_client()
    
    # Generate unique workflow ID
    workflow_id = f"transfer-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    
    # Prepare workflow input
    workflow_input = MoneyTransferInput(
        from_account=from_account,
        to_account=to_account,
        amount=amount
    )
    
    # Start workflow
    handle = await client.start_workflow(
        MoneyTransferWorkflow.run,
        workflow_input,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )
    
    return workflow_id, handle


async def get_workflow_state_async(workflow_id):
    """Get workflow state from Temporal using query."""
    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)
        
        # Get workflow description for metadata
        desc = await handle.describe()
        status = desc.status.name
        
        # Initialize workflow data
        workflow_data = {
            'workflow_id': workflow_id,
            'run_id': desc.run_id,
            'status': status,
            'start_time': desc.start_time.timestamp() if desc.start_time else None,
            'close_time': desc.close_time.timestamp() if desc.close_time else None,
            'input': None,
            'result': None
        }
        
        # Query workflow state if it's still running or just completed
        if status in ['RUNNING', 'COMPLETED']:
            try:
                state = await handle.query(MoneyTransferWorkflow.get_state)
                workflow_data['input'] = state.get('input', {})
                workflow_data['result'] = state.get('result')
            except Exception as e:
                print(f"Error querying workflow {workflow_id}: {e}")
                # Fallback: try to get result if completed
                if status == 'COMPLETED':
                    try:
                        result = await handle.result()
                        workflow_data['input'] = {
                            'from_account': result.from_account,
                            'to_account': result.to_account,
                            'amount': result.amount
                        }
                        workflow_data['result'] = {
                            'success': result.success,
                            'from_account': result.from_account,
                            'to_account': result.to_account,
                            'amount': result.amount,
                            'from_account_starting_balance': result.from_account_starting_balance,
                            'to_account_starting_balance': result.to_account_starting_balance,
                            'from_account_final_balance': result.from_account_final_balance,
                            'to_account_final_balance': result.to_account_final_balance,
                            'error_message': result.error_message
                        }
                    except:
                        pass
        
        return workflow_data
        
    except Exception as e:
        print(f"Error getting workflow state for {workflow_id}: {e}")
        return None


async def get_all_workflows_async():
    """Get all workflows from Temporal using queries."""
    workflows = []
    try:
        client = await get_temporal_client()
        
        # Query recent workflows
        async for workflow_execution in client.list_workflows(
            f'WorkflowType="MoneyTransferWorkflow"'
        ):
            workflow_id = workflow_execution.id
            
            # Get workflow state using query
            workflow_data = await get_workflow_state_async(workflow_id)
            if workflow_data:
                workflows.append(workflow_data)
                
    except Exception as e:
        print(f"Error listing workflows: {e}")
    
    return workflows


# ============================================================================
# Web UI Routes
# ============================================================================

@app.route('/')
def index():
    """Serve the main UI page."""
    return render_template('index.html')


# ============================================================================
# API Routes - Accounts
# ============================================================================

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts from the Account API."""
    try:
        response = requests.get(f"{ACCOUNT_API_URL}/accounts/account_A")
        if response.status_code != 200:
            return jsonify({"error": "Failed to connect to Account API"}), 503
        
        # Get both accounts
        accounts = {}
        for account_id in ['account_A', 'account_B']:
            try:
                resp = requests.get(f"{ACCOUNT_API_URL}/accounts/{account_id}")
                if resp.status_code == 200:
                    data = resp.json()
                    accounts[account_id] = {"balance": data['balance']}
            except:
                pass
        
        return jsonify(accounts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API Routes - Workflows
# ============================================================================

@app.route('/api/transfer', methods=['POST'])
def start_transfer():
    """Start a new money transfer workflow."""
    try:
        data = request.get_json()
        
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        amount = data.get('amount')
        
        if not all([from_account, to_account, amount]):
            return jsonify({"error": "Missing required fields"}), 400
        
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
        
        # Start workflow
        workflow_id, handle = run_async(start_workflow_async(from_account, to_account, amount))
        
        return jsonify({
            "workflow_id": workflow_id,
            "status": "started"
        }), 200
        
    except Exception as e:
        print(f"Error starting transfer: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """Get all workflows."""
    try:
        # Get workflows from Temporal using queries
        workflows = run_async(get_all_workflows_async())
        return jsonify(workflows), 200
    except Exception as e:
        print(f"Error getting workflows: {e}")
        return jsonify([]), 200


@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """Get a specific workflow."""
    try:
        # Get workflow state using Temporal query
        workflow = run_async(get_workflow_state_async(workflow_id))
        
        if workflow is None:
            return jsonify({"error": "Workflow not found"}), 404
        
        return jsonify(workflow), 200
    except Exception as e:
        print(f"Error getting workflow: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API Routes - Real World Mode
# ============================================================================

@app.route('/api/real-world-mode', methods=['GET'])
def get_real_world_mode():
    """Get the current Real World Mode status."""
    try:
        # Read the status from account_api.py file
        with open(ACCOUNT_API_FILE, 'r') as f:
            content = f.read()
        
        # Check if REAL_WORLD_MODE is True or False
        enabled = 'REAL_WORLD_MODE = True' in content
        
        return jsonify({"enabled": enabled}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/real-world-mode', methods=['POST'])
def set_real_world_mode():
    """Toggle Real World Mode."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        # Read the account_api.py file
        with open(ACCOUNT_API_FILE, 'r') as f:
            content = f.read()
        
        # Replace the REAL_WORLD_MODE value
        if enabled:
            content = content.replace(
                'REAL_WORLD_MODE = False',
                'REAL_WORLD_MODE = True'
            )
        else:
            content = content.replace(
                'REAL_WORLD_MODE = True',
                'REAL_WORLD_MODE = False'
            )
        
        # Write back to file
        with open(ACCOUNT_API_FILE, 'w') as f:
            f.write(content)
        
        return jsonify({
            "enabled": enabled,
            "message": f"Real World Mode {'enabled' if enabled else 'disabled'}"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API Routes - Database Management
# ============================================================================

@app.route('/api/reset', methods=['POST'])
def reset_database():
    """Reset the accounts database."""
    try:
        from reset_db import reset_database as do_reset
        success = do_reset()
        
        if success:
            return jsonify({"message": "Database reset successfully"}), 200
        else:
            return jsonify({"error": "Failed to reset database"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Money Transfer API - Web UI")
    print("=" * 70)
    print("\n📋 Prerequisites:")
    print("  1. Temporal server running on localhost:7233")
    print("  2. Account API running on http://127.0.0.1:5000")
    print("  3. Worker running (python worker.py)")
    print("\n🌐 Access the UI at: http://localhost:5001/")
    print("\n⚠️  Note: The worker must be running for workflows to execute!")
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
