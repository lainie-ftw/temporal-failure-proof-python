import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import check_balance, withdraw, deposit
from workflow import MoneyTransferWorkflowMod03

# Configure logging to show workflow and activity execution details
logging.basicConfig(level=logging.INFO)


async def main():
    """Start a Temporal worker for the money transfer workflow."""
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create worker
    worker = Worker(
        client,
        task_queue="money-transfer-task-queue",
        workflows=[MoneyTransferWorkflowMod03],
        activities=[check_balance, withdraw, deposit],
    )
    
    print("Worker started, listening on task queue: money-transfer-task-queue")
    print("Waiting for workflows to execute...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
