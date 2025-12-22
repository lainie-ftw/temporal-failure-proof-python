import asyncio

from temporalio.client import Client

from workflow import PrintNumbersWorkflow


async def main():
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Generate a unique workflow ID
    workflow_id = f"print-numbers-workflow"
    
    # Start the workflow
    handle = await client.start_workflow(
        PrintNumbersWorkflow.run,
        id=workflow_id,
        task_queue="print-numbers-task-queue",
    )
    
    print(f"Started workflow with ID: {workflow_id}")
    print(f"Workflow RunID: {handle.first_execution_run_id}")
    
    # Wait for the workflow to complete and get the result
    result = await handle.result()
    print(f"\nWorkflow result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
