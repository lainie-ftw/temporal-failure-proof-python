# Module 3: Money Transfer System with Web UI

This module provides a complete web-based interface for the Temporal money transfer workflow system.

## Features

- 🌐 **Web-based UI** - Interactive interface for managing money transfers
- 💸 **Multiple Concurrent Transfers** - Start multiple workflows simultaneously
- ⚡ **Real-time Monitoring** - Track active workflows and view completion status
- 🔄 **Auto-refresh** - Automatically updates account balances and workflow statuses
- ⚠️ **Real World Mode** - Toggle API failures to test Temporal's retry capabilities
- 📊 **Workflow History** - View completed and failed workflow executions
- 🗄️ **Database Reset** - Reset account balances to initial state

## Architecture

The system consists of four components:

1. **Temporal Server** - Workflow orchestration (port 7233)
2. **Account API** - Flask service managing account data (port 5000)
3. **Money Transfer API** - Web UI and workflow management (port 5001)
4. **Worker** - Processes Temporal workflows

## Setup and Running

### Prerequisites

1. Start Temporal server (see main README for Temporal setup)
2. Install dependencies:
   ```bash
   cd exercises
   uv pip install -e .
   ```

### Starting the Services

You need to run these in **separate terminal windows**:

#### Terminal 1: Account API
```bash
cd exercises/module03
uv run python account_api.py
```
This starts the Account API on `http://localhost:5000`

#### Terminal 2: Worker
```bash
cd exercises/module03
uv run python worker.py
```
This starts the Temporal worker that processes workflows

#### Terminal 3: Money Transfer API (Web UI)
```bash
cd exercises/module03
uv run python money_transfer_api.py
```
This starts the Web UI on `http://localhost:5001`

### Access the Web UI

Open your browser and navigate to:
```
http://localhost:5001/
```

## Using the Web UI

### Account Balances
- View real-time account balances for all accounts
- Automatically refreshes every 3 seconds (when auto-refresh is enabled)

### Starting a Transfer
1. Select the **From Account** (source)
2. Select the **To Account** (destination)
3. Enter the **Amount** to transfer
4. Click **Start Transfer**
5. A unique workflow ID will be generated and displayed
6. The workflow appears in the "Active Workflows" section

### Multiple Concurrent Transfers
- You can start multiple transfers without waiting for previous ones to complete
- Each transfer gets a unique workflow ID
- All active workflows are tracked simultaneously

### Real World Mode
- Toggle the **Real World Mode** switch to simulate API failures
- When enabled, the Account API will randomly:
  - Return errors (40% chance)
  - Timeout (10% chance)
  - Succeed (50% chance)
- This demonstrates Temporal's automatic retry capabilities

### Workflow Monitoring
- **Active Workflows**: Shows workflows currently executing
- **Workflow History**: Shows completed and failed workflows with results
- Color-coded status indicators:
  - 🟡 Yellow border = Running
  - 🟢 Green border = Completed successfully
  - 🔴 Red border = Failed

### Database Reset
- Click **Reset Database** to restore accounts to initial balances:
  - account_A: $1000.00
  - account_B: $500.00
- Useful for running multiple demonstrations

### Auto-refresh Control
- Toggle **Auto-refresh** to enable/disable automatic updates
- Manual refresh available via the **🔄 Refresh** button

## API Endpoints

The Money Transfer API provides the following endpoints:

### UI
- `GET /` - Serve the web interface

### Accounts
- `GET /api/accounts` - Get all account balances

### Workflows
- `POST /api/transfer` - Start a new money transfer workflow
  ```json
  {
    "from_account": "account_A",
    "to_account": "account_B",
    "amount": 100.00
  }
  ```
- `GET /api/workflows` - List all workflows
- `GET /api/workflows/<workflow_id>` - Get specific workflow details

### Configuration
- `GET /api/real-world-mode` - Get Real World Mode status
- `POST /api/real-world-mode` - Toggle Real World Mode
  ```json
  {
    "enabled": true
  }
  ```

### Database
- `POST /api/reset` - Reset database to initial state

## Files

- `money_transfer_api.py` - Main Flask application with UI and workflow management
- `account_api.py` - Account management service (unchanged from original)
- `worker.py` - Temporal worker
- `workflow.py` - Workflow definition
- `activities.py` - Activity implementations
- `reset_db.py` - Database reset utility
- `templates/index.html` - Web UI HTML
- `static/css/styles.css` - UI styling
- `static/js/app.js` - Frontend JavaScript

## Troubleshooting

### UI shows "Failed to load accounts"
- Ensure the Account API is running on port 5000
- Check terminal for error messages

### Workflows don't execute
- Ensure the Temporal worker is running (`python worker.py`)
- Check that Temporal server is running on localhost:7233

### Real World Mode toggle doesn't work
- The toggle modifies `account_api.py` directly
- You may need to restart the Account API after toggling

### Port conflicts
- Money Transfer API: port 5001
- Account API: port 5000
- Ensure these ports are available

## Learning Objectives

This module demonstrates:

1. **Temporal Workflow Orchestration** - How workflows coordinate multiple activities
2. **Failure Handling** - Automatic retries when downstream services fail
3. **Durability** - Workflows can be monitored and resumed
4. **Concurrent Execution** - Multiple workflows running simultaneously
5. **Observability** - Real-time visibility into workflow execution
