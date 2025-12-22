import asyncio
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import print_number


@workflow.defn
class PrintNumbersWorkflow:
    @workflow.run
    async def run(self) -> str:
        for counter in range(1, 11):
            # Execute print_number activity
            await workflow.execute_activity(
                print_number,
                counter,
                start_to_close_timeout=timedelta(seconds=10),
            )
            
            # Sleep for 3 seconds between calls (except after the last one)
            if counter < 10:
                await asyncio.sleep(3)
        
        return "Workflow completed"
