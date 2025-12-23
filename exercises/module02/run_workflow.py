import asyncio
import sys
import requests

from temporalio.client import Client, WorkflowExecutionStatus
from temporalio.worker import Worker

from activities import check_balance, withdraw, deposit
from workflow import MoneyTransferWorkflow, MoneyTransferInput

# Account API base URL
API_BASE_URL = "http://localhost:5000"


async def main():
    """Run the money transfer workflow."""
    
    # Connect to Temporal server
    print("Connecting to Temporal server...")
    try:
        client = await Client.connect("localhost:7233")
        print("✓ Connected to Temporal server\n")
    except Exception as e:
        print(f"✗ Failed to connect to Temporal server: {e}")
        print(f"  Please ensure Temporal server is running")
        sys.exit(1)
    
    # Create worker
    worker = Worker(
        client,
        task_queue="money-transfer-task-queue",
        workflows=[MoneyTransferWorkflow],
        activities=[check_balance, withdraw, deposit],
    )
    
    print("Starting worker on task queue: money-transfer-task-queue")
    
    # Run worker in background task
    worker_task = asyncio.create_task(worker.run())
    
    # Give the worker a moment to start up
    await asyncio.sleep(1)
    
    # Generate a unique workflow ID
    workflow_id = f"money-transfer-workflow"
    
    # Prepare workflow input
    workflow_input = MoneyTransferInput(
        from_account="account_A",
        to_account="account_B",
        amount=100.00
    )
    
    #todo move this to when the workflow isn't started below
    print(f"\n{'='*60}")
    print(f"Starting (or resuming) money transfer workflow")
    print(f"  From: {workflow_input.from_account}")
    print(f"  To: {workflow_input.to_account}")
    print(f"  Amount: ${workflow_input.amount:.2f}")
    print(f"{'='*60}\n")
    
    # Check if workflow is already running
    try:
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        
        if desc.status == WorkflowExecutionStatus.RUNNING:
            print(f"Workflow {workflow_id} is already running")
            print(f"Workflow RunID: {desc.run_id}")
            print("\nUsing existing workflow...\n")
        else:
            # Workflow exists but not running, start a new one
            print(f"Starting workflow with ID: {workflow_id}")
            handle = await client.start_workflow(
                MoneyTransferWorkflow.run,
                workflow_input,
                id=workflow_id,
                task_queue="money-transfer-task-queue",
            )
            print(f"Workflow RunID: {handle.first_execution_run_id}")
            print("\nExecuting workflow...\n")
    except Exception:
        # Workflow doesn't exist, start it
        print(f"Starting workflow with ID: {workflow_id}")
        handle = await client.start_workflow(
            MoneyTransferWorkflow.run,
            workflow_input,
            id=workflow_id,
            task_queue="money-transfer-task-queue",
        )
        print(f"Workflow RunID: {handle.first_execution_run_id}")
        print("\nExecuting workflow...\n")
    
    # Wait for the workflow to complete and get the result
    try:
        result = await handle.result()
        
        print(f"\n{'='*60}")
        print(f"✓ Workflow completed successfully!")
        print(f"{'='*60}\n")
        
        print("Transfer Summary:")
        print(f"  From Account: {result.from_account}")
        print(f"  To Account: {result.to_account}")
        print(f"  Amount Transferred: ${result.amount:.2f}")
        print(f"\nFinal Balances:")
        print(f"  {result.from_account}: ${result.from_account_final_balance:.2f}")
        print(f"  {result.to_account}: ${result.to_account_final_balance:.2f}")
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Workflow failed!")
        print(f"{'='*60}\n")
        print(f"Error: {e}")
        sys.exit(1)
    
    # Shutdown the worker
    print("\n\nShutting down worker...")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    
    print("Worker stopped")
    print("\n✓ Money transfer completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
