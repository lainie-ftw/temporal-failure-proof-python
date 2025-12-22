# Module 01: Print Numbers Workflow

This directory contains a Temporal workflow implementation that replicates the behavior of `python_print.py`.

## Files

- **python_print.py** - Original Python script that prints numbers 1-4 with 3-second delays
- **activities.py** - Temporal activity definitions for printing each number
- **workflow.py** - Temporal workflow that orchestrates the activities with sleep delays
- **worker.py** - Worker process that executes workflows and activities
- **starter.py** - Client script to start the workflow execution

## How to Run

### Prerequisites

1. Ensure Temporal Server is running (default: localhost:7233)
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 1: Start the Worker

In Terminal 1, run the worker to listen for workflow tasks:

```bash
python worker.py
```

You should see: `Worker started, listening on task queue: print-numbers-task-queue`

### Step 2: Start the Workflow

In Terminal 2, execute the starter script:

```bash
python starter.py
```

This will:
- Connect to the Temporal server
- Start a new workflow execution
- Print the workflow ID and RunID
- Wait for the workflow to complete and display the result

### Expected Output

The workflow will print:
```
1
(3 second delay)
2
(3 second delay)
3
(3 second delay)
4
```

This matches the behavior of the original `python_print.py` script.

## Key Differences from Original Script

- **Fault Tolerance**: The Temporal workflow can recover from failures
- **Observability**: Complete execution history available in Temporal UI
- **Scalability**: Activities can be distributed across multiple workers
- **Durability**: Workflow state is persisted and can survive crashes
