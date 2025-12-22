from temporalio import activity


@activity.defn
async def print_number(n: int) -> str:
    print(str(n))
    return str(n)
