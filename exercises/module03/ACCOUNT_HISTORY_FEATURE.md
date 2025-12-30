# Account History Feature

## Overview

This feature leverages the custom search attributes (`from_account` and `to_account`) to provide per-account transaction history views in the Money Transfer UI.

## Implementation Details

### Backend Changes (money_transfer_api.py)

**New API Endpoint:**
```
GET /api/accounts/<account_id>/workflows
```

Returns:
```json
{
  "account_id": "account_A",
  "summary": {
    "total_sent": 500.00,
    "total_received": 300.00,
    "net_change": -200.00,
    "transaction_count": 8,
    "completed_count": 7,
    "failed_count": 0,
    "running_count": 1
  },
  "workflows": [...]
}
```

**New Helper Functions:**
1. `get_account_workflows_async(account_id)` - Queries Temporal using search attributes:
   - Query: `from_account = "{account_id}" OR to_account = "{account_id}"`
   - Adds `direction` field ("sent" or "received")
   - Adds `counterparty` field (the other account in the transaction)

2. `calculate_account_summary(account_id, workflows)` - Calculates summary statistics:
   - Total sent/received amounts
   - Net change
   - Transaction counts by status

### Frontend Changes

**UI Components (index.html):**
- Added "View History →" button to each account in the accounts list
- Added hidden account history section that displays when viewing an account

**JavaScript Functions (app.js):**
1. `viewAccountHistory(accountId)` - Fetches and displays account history
2. `displayAccountHistory(data)` - Renders the account history view with:
   - Summary statistics cards
   - Transaction list with direction indicators
   - Workflow details and status
3. `closeAccountHistory()` - Closes the account history view

**Styling (styles.css):**
- Selected account highlighting
- Summary cards with color-coded values
- Transaction items with sent/received indicators
- Responsive design for mobile devices

## Features

### Summary Statistics
- **Total Sent**: Sum of all completed outgoing transfers
- **Total Received**: Sum of all completed incoming transfers
- **Net Change**: Received - Sent
- **Total Transactions**: Count of all workflows involving the account

### Transaction Display
Each transaction shows:
- Direction (↗️ SENT or ↙️ RECEIVED)
- Counterparty account
- Amount (color-coded: red for sent, green for received)
- Workflow ID
- Status (COMPLETED, RUNNING, FAILED)
- Timestamps
- Step progress for running workflows

## Usage

1. **Start the services:**
   ```bash
   # Terminal 1: Account API
   cd exercises/module03
   uv run python account_api.py
   
   # Terminal 2: Worker
   uv run python worker.py
   
   # Terminal 3: Web UI
   uv run python money_transfer_api.py
   ```

2. **Create some test transactions:**
   - Open http://localhost:5001
   - Use "Start Daily Batch" or create individual transfers
   
3. **View account history:**
   - Click "View History →" button next to any account
   - Review summary statistics and transaction list
   - Click "← Back to All Accounts" to return

## Technical Notes

### Search Attribute Query
The feature uses Temporal's search attribute query capability:
```python
query = f'from_account = "{account_id}" OR to_account = "{account_id}"'
async for workflow_execution in client.list_workflows(query):
    # Process workflows...
```

### Performance Considerations
- Workflows are queried on-demand (not cached)
- Summary statistics are calculated server-side
- Only completed workflows count toward sent/received totals
- Results are sorted by start time (most recent first)

### UX Enhancements
- Selected account is highlighted in the accounts list
- Smooth scroll to account history section
- Color-coded transaction directions
- Hover effects on transaction items
- Responsive layout for mobile devices

## Future Enhancements

Potential improvements:
- Date range filtering
- Export to CSV
- Link to Temporal Web UI for workflow details
- Real-time updates for active workflows
- Transaction search/filtering
- Pagination for large transaction histories
