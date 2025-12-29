import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from activities import check_balance, withdraw, deposit
from workflow import MoneyTransferWorkflow


async def main():
    """Start a Temporal worker for the money transfer workflow."""
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create worker
    worker = Worker(
        client,
        task_queue="money-transfer-task-queue",
        workflows=[MoneyTransferWorkflow],
        activities=[check_balance, withdraw, deposit],
    )
    
    print("Worker started, listening on task queue: money-transfer-task-queue")
    print("Waiting for workflows to execute...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
