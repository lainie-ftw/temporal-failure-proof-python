# Custom Search Attributes - Module 3

This document describes the custom search attributes added to the MoneyTransferWorkflow.

## Search Attributes Added

Two custom search attributes have been added to enable filtering and searching workflows by account:

1. **`from_account`** (Keyword) - The source account for the money transfer
2. **`to_account`** (Keyword) - The destination account for the money transfer

## Implementation

### 1. Creating Search Attributes in Temporal

The search attributes were created using the Temporal CLI:

```bash
temporal operator search-attribute create --name from_account --type Keyword --namespace default
temporal operator search-attribute create --name to_account --type Keyword --namespace default
```

### 2. Setting Search Attributes in Workflow

The workflow code (workflow.py) was updated to set these search attributes when the workflow starts:

```python
@workflow.run
async def run(self, input: MoneyTransferInput) -> MoneyTransferResult:
    # Set custom search attributes for from_account and to_account
    workflow.upsert_search_attributes({
        "from_account": [input.from_account],
        "to_account": [input.to_account]
    })
    
    # ... rest of workflow logic
```

## Usage Examples

Once you have workflows running with these search attributes, you can query them using the Temporal CLI or Web UI:

### CLI Examples

**Find all transfers FROM a specific account:**
```bash
temporal workflow list --query 'from_account = "account_A"'
```

**Find all transfers TO a specific account:**
```bash
temporal workflow list --query 'to_account = "account_B"'
```

**Find transfers between two specific accounts:**
```bash
temporal workflow list --query 'from_account = "account_A" AND to_account = "account_B"'
```

**Find all transfers involving a specific account (as source OR destination):**
```bash
temporal workflow list --query 'from_account = "account_A" OR to_account = "account_A"'
```

**Combine with other filters (e.g., only running workflows):**
```bash
temporal workflow list --query 'from_account = "account_A" AND ExecutionStatus = "Running"'
```

**Recent completed transfers from an account:**
```bash
temporal workflow list --query 'from_account = "account_A" AND ExecutionStatus = "Completed"' --limit 10
```

### Temporal Web UI

You can also use these search attributes in the Temporal Web UI (typically at http://localhost:8233):

1. Navigate to the Workflows page
2. Click on "Advanced Search" or use the query box
3. Enter queries like:
   - `from_account = "account_A"`
   - `to_account = "account_B"`
   - `from_account = "account_A" AND to_account = "account_B"`

## Testing the Implementation

To test that the search attributes are working:

1. **Start the services** (if not already running):
   ```bash
   # Terminal 1: Account API
   cd exercises/module03
   uv run python account_api.py
   
   # Terminal 2: Worker
   cd exercises/module03
   uv run python worker.py
   
   # Terminal 3: Web UI
   cd exercises/module03
   uv run python money_transfer_api.py
   ```

2. **Create some test workflows**:
   - Open http://localhost:5001
   - Create a few transfers from different accounts
   - For example:
     - Transfer $50 from account_A to account_B
     - Transfer $75 from account_A to account_C
     - Transfer $100 from account_B to account_C

3. **Query using search attributes**:
   ```bash
   # List all transfers from account_A
   temporal workflow list --query 'from_account = "account_A"'
   
   # List all transfers to account_B
   temporal workflow list --query 'to_account = "account_B"'
   
   # List transfers between account_A and account_B
   temporal workflow list --query 'from_account = "account_A" AND to_account = "account_B"'
   ```

## Benefits

Custom search attributes provide several benefits:

1. **Improved Visibility** - Easily find workflows related to specific accounts
2. **Better Monitoring** - Track all transfers involving a particular account
3. **Troubleshooting** - Quickly identify problematic transfers for specific accounts
4. **Auditing** - Generate reports of all transfers for compliance or analysis
5. **Operational Queries** - Answer questions like:
   - "Show me all pending transfers from this account"
   - "What were the last 10 transfers to this account?"
   - "Are there any failed transfers involving this account?"

## Important Notes

- Search attributes are indexed and searchable, but **not encrypted**
- Do not use PII (Personally Identifiable Information) as search attribute values
- Search attributes are carried over in Continue-As-New operations
- The values are stored as keyword lists (arrays), which is why we use `[input.from_account]` syntax
- You need **advanced Visibility** (Elasticsearch, PostgreSQL, MySQL, or SQLite with Temporal Server v1.20+) to use custom search attributes

### ⚠️ Nondeterminism Warning

**Important**: Adding `upsert_search_attributes` to an existing workflow creates a workflow code change. Workflows that were created *before* this code change will fail with nondeterminism errors when queried by the Web UI because:

1. Old workflows were created WITHOUT the search attributes code
2. The new worker has the search attributes code
3. Temporal detects this mismatch when replaying workflow history

**Solution**: If you have existing workflows from before adding search attributes, you should:

1. **Terminate old workflows**:
   ```bash
   temporal workflow terminate --query 'WorkflowType="MoneyTransferWorkflow" AND StartTime < "2025-12-30T16:40:00Z"' --reason "Cleaning up workflows before search attributes"
   ```

2. **Or use workflow versioning** (advanced): Use Temporal's `workflow.patched()` API to make the change deterministic

After terminating/cleaning old workflows, new workflow executions will work correctly with search attributes and display properly in the UI.

## Reference

For more information about Search Attributes, see:
- Temporal Documentation: https://docs.temporal.io/search-attribute#custom-search-attribute
- Python SDK Visibility Guide: https://docs.temporal.io/develop/python/observability#visibility
