import asyncio

from temporalio.client import Client, WorkflowExecutionStatus
from temporalio.worker import Worker

from activities import print_number
from workflow import PrintNumbersWorkflow


async def main():
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create worker
    worker = Worker(
        client,
        task_queue="print-numbers-task-queue",
        workflows=[PrintNumbersWorkflow],
        activities=[print_number],
    )
    
    print("Starting worker on task queue: print-numbers-task-queue")
    
    # Run worker in background task
    worker_task = asyncio.create_task(worker.run())
    
    # Give the worker a moment to start up
    await asyncio.sleep(1)
    
    # Generate a unique workflow ID
    workflow_id = f"print-numbers-workflow"
    
    # Check if workflow is already running
    try:
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        
        if desc.status == WorkflowExecutionStatus.RUNNING:
            print(f"\nWorkflow {workflow_id} is already running")
            print(f"Workflow RunID: {desc.run_id}")
            print("\nUsing existing workflow...\n")
        else:
            # Workflow exists but not running, start a new one
            print(f"\nStarting workflow with ID: {workflow_id}")
            handle = await client.start_workflow(
                PrintNumbersWorkflow.run,
                id=workflow_id,
                task_queue="print-numbers-task-queue",
            )
            print(f"Workflow RunID: {handle.first_execution_run_id}")
            print("\nExecuting workflow...\n")
    except Exception:
        # Workflow doesn't exist, start it
        print(f"\nStarting workflow with ID: {workflow_id}")
        handle = await client.start_workflow(
            PrintNumbersWorkflow.run,
            id=workflow_id,
            task_queue="print-numbers-task-queue",
        )
        print(f"Workflow RunID: {handle.first_execution_run_id}")
        print("\nExecuting workflow...\n")
    
    # Wait for the workflow to complete and get the result
    result = await handle.result()
    print(f"\nWorkflow result: {result}")
    
    # Shutdown the worker
    print("\nShutting down worker...")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    
    print("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
