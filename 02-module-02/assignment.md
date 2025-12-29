---
slug: module-02
id: iciq2lchxv3m
type: challenge
title: 'Module 2: Exploring Simpler Retries'
tabs:
- id: 6ybo85ssqi2e
  title: Terminal 1
  type: terminal
  hostname: workshop-host
  workdir: /workspace/temporal-failure-proof-python/exercises/module02
- id: 4corw3hnqojz
  title: Terminal 2
  type: terminal
  hostname: workshop-host
  workdir: /workspace/temporal-failure-proof-python/exercises/module02
- id: pbk03fwqgoyi
  title: VS Code
  type: service
  hostname: workshop-host
  path: /
  port: 8443
- id: yx9sls10q4nb
  title: Temporal UI
  type: service
  hostname: workshop-host
  path: /
  port: 8080
difficulty: basic
timelimit: 0
lab_config:
  default_layout_sidebar_size: 0
enhanced_loading: null
---
# Overview
This assigment gives you hands-on experience with a major part of the _Durable_ in Durable Execution.

We're going to work with an application that is slightly more complex. Our module 2 application will:
- execute a business-related process
- connect to an [API](https://www.geeksforgeeks.org/software-testing/what-is-an-api/) that is _somewhat_ unreliable

We'll explore Temporal Activities, and how they automatically retry errors as you configure them. We'll compare them with how you might handle errors without Durable Execution, and why that might be a bit complex or even painful.

## Learning Objectives
1. Hands on experience with code that calls an unreliable API
2. How to solve unreliability with code - and pros and cons
3. How to solve unreliability with Durable Execution and _durable error handling_

Exercise Steps
===

## Step 1: Money movement + external API: Happy path!

1. In Terminal 1 [button label="Terminal 1" background="#444CE7"](tab-0), start the API server that interacts with bank accounts. For now, it's very reliable and won't generate errors.
```bash,run
uv run account_api.py
```

2. In Terminal 2 [button label="Terminal 2" background="#444CE7"](tab-1), start the money movement process.
This will execute a simplified money movement from one account to another, and write to a simple file-based database.
```bash,run
uv run move_money.py
```
This version has only the basics of error handling, with simple try/catch:
```python
    print(f"\nStep 2: Checking balance of {to_account}...")
    try:
        response = requests.get(f"{API_BASE_URL}/accounts/{to_account}")
        response.raise_for_status()
        to_balance = response.json()['balance']
        print(f"  ✓ {to_account} balance: ${to_balance:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error checking {to_account} balance: {e}")
        return False
```

Once it's complete, you can reset the "database" if you'd like by running this script:
```bash,run
uv run reset_db.py
```

3. Run money movement + retries
Let's move money again, but with python code that has more error handling.
```bash,run
uv run move_money_retries.py
```
Still good! Sweet!<br/>

You can see that it has quite a lot of error handling code in retry_api_call() - a nice reusable bit of code:
```python
def retry_api_call(operation, operation_description, max_retries=MAX_RETRIES, base_delay=BASE_RETRY_DELAY):
    """
    Retry an API call with exponential backoff.

    Args:
        operation: A callable that performs the API request
        operation_description: Description of the operation for logging
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff

    Returns:
        The result of the successful operation

    Raises:
        The last exception if all retries are exhausted
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return operation()
        except requests.exceptions.RequestException as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                print(f"    ⟳ Retry attempt {attempt + 1}/{max_retries} for {operation_description} after {delay}s...")
                time.sleep(delay)
            else:
                # All retries exhausted
                print(f"    ✗ All retry attempts exhausted for {operation_description}")

    # Raise the last exception if all retries failed
    raise last_exception
```

<br/>
You can again reset the "database" if you'd like:
```bash,run
uv run reset_db.py
```

## Step 2: Money movement with external API: REAL WORLD MODE

<img src="./anchorman_60_percent_API.jpg" alt="60 percent of the time it works every time" style="display: block; margin: 0 auto;" />
Now we're going to make our API behave a bit more like a real-world API, with timeouts, errors, and general "it works most of the time" vibes.

1. In the code editor [button label="Code Editor" background="#444CE7"](tab-2), in account_api.py, change REAL_WORLD_MODE = True, then restart the API.

2. Run money movement again -
```bash,run
uv run move_money.py
```
Feel free to run this multiple times as REAL_WORLD_MODE only *sometimes* fails...

3. Run money movement with retries to see how it handles our API -
```bash,run
uv run move_money_retries.py
```
Feel free to run this multiple times as REAL_WORLD_MODE only *sometimes* fails...
<br />
For extra chaos, kill and restart a money movement while it's retrying, and note that even if it didn't partially move money (withdraw but no deposit), it restarts its retries from the beginning.
<br />
We can see our error handling code is handling most of the errors, but we have to remember to use it for every external call, and if we need to add new features like errors we don't want to retry, we have to add that in and test things again.

<br/>
You can again reset the "database" if you'd like:
```bash,run
uv run reset_db.py
```

## Step 3: Now, let's see how it works with Temporal!
Execute a Workflow to do the same process with the failure-prone "real world" API:
```bash,run
uv run run_workflow.py
```

You can see in the Workflow code in the editor [button label="Code Editor" background="#444CE7"](tab-2) we didn't add any error handling code, just called _Activities_ with the [default retry policy](https://docs.temporal.io/encyclopedia/retry-policies#default-values-for-retry-policy):
```python
    # Step 1: Check balance of source account
    from_balance_result = await workflow.execute_activity(
        check_balance,
        CheckBalanceInput(account_id=input.from_account),
        start_to_close_timeout=timedelta(seconds=10),
    )
```

From the logs you can see that it durably executes the money movement, handling failure with aplomb.

If you kill the workflow worker while it's error handling, it remembers what retry it was on and what timeouts were set, and when it is restarted it picks up where it left off.

## Step 4: Check out the workflow in the Temporal UI
Now let's examine the Workflow's state as it progressed.

1. Click the **[button label="Temporal UI" background="#444CE7"](tab-3) Service tab** in your Instruqt envrionment.
2. The **Workflows** pane will display all recent executions
3. Locate your workflow (`money-transfer-workflow`) in the list

Take time to examine:
- **Event History:** A timeline view of all workflow events
- **Input/Results:** The data passed to and returned from your workflow
- **Workflow Timeline:** Visual representation of the execution flow

4. Check out the Activity calls, notice the different color and time taken for the ones that failed in attempts before succeeding. Did any fail completely?
5. Check out an Activity that failed at least once. Can you tell any details about the failure? (Hint: look for Last Failure Details!)

The durability in handling retries and timeouts combined with the visibility into state and failures is what we mean by _durable error handling_.
