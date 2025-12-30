# Module 04: Bug handling with Temporal

This module demonstrates how dealing with bugs with Temporal is easier.

In this scenario, we're going to pretend that a less experienced programmer, Jerry, has made some changes to our code. Let's run it and see how Jerry's code does.

(This module inspired by real-world scenarios where code gets pushed to production and...well just run it and see what happens and how we can fix it.)

## Files

### Temporal Workflow Implementation
- **`activities.py`** - Temporal activities for account operations (check_balance, withdraw, deposit) with data classes
- **`workflow.py`** - MoneyTransferWorkflow that orchestrates the money transfer process
- **`worker.py`** - Standalone worker that processes workflows
- **`run_workflow.py`** - Script to run the workflow (includes embedded worker)

## How to Run

### Prerequisites
1. **Start Temporal Server** (if not already running):
```bash
temporal server start-dev
```

2. **Start the Account API** (in a separate terminal):
```bash
cd exercises/module04
python account_api.py
```

### Option 1: Run with Embedded Worker
This starts a worker and executes the workflow in one command:
```bash
cd exercises/module04
python run_workflow.py
```

### Option 2: Run Worker Separately
Start the worker in one terminal:
```bash
cd exercises/module04
python worker.py
```

Then trigger workflows from another terminal or through the Temporal UI.

### Notice the Workflow failed:
Go to the Temporal UI and see that the workflow has failed. Explore the exception.
Look at the Workflow code, can you find the problem?
Fix Jerry's code, then restart the worker process. 

As we saw when we crashed things in Module 1, Temporal will pick back up where it left off. 
Now that it can proceed, it will finish the Workflow task and continue.

### Notice an Activity Failed:
Now you may notice that the Withdraw Activity is continually failing. Check out [activities.py](./activities.py) - let's see what is happening. Perhaps Jerry has made some changes here too?

Fix the Activity, restart the worker process, and see that Temporal picks up the latest Activity code and succeeds.

Nice work! 

## Details of Temporal Implementation
### Bugs in Workflow Code
Temporal keeps process state automatically, and always retries Workflow Task Failures. 
If all Workflows are stuck on a bug step, fixing these Workflow failure can be as simple as fixing the code and redeploying it.

(If some Workflows are past the bug step -- if it breaks some Workflows but not all -- take care to [version](https://docs.temporal.io/develop/python/versioning) the change so that Workflows past this step will not have a breaking change.)

### Bugs in Activity Code
Temporal by default retries Activities indefinitely. If you have an Activity that is broken and keeps retrying, you can see the failure info in the UI, including the line of code, fix the code, add tests and pass tests, and then deploy the fixed code. Temporal will then execute the Activities. It might be a while - usually retry backoff settings are relevant here. 

This auto-bug-fixing behavior is one reason to keep unlimited retries defaults for your Activities.
If your business process requires succeeding or failing in a limited time, or you don't want to call an expensive API many many times, or you want to fail your processes for other reasons after a number of calls, it's fine to limit retries - but you lose this neat behavior.

It might be useful to mention Workflow Reset as well - you can "time travel" your workflows back to a certain step using [Workflow Reset](https://patford12.medium.com/batch-reset-with-temporal-f895a8b8408b) - so if they've failed out their Activity Retry policy and failed the Workflow

