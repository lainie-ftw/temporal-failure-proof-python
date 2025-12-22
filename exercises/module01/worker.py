import asyncio

from temporalio.client import Client
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
    
    print("Worker started, listening on task queue: print-numbers-task-queue")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
