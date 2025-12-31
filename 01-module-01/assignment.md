---
slug: module-01
id: zzmodvjpso51
type: challenge
title: 'Module 1: Exploring Crash-Proof'
tabs:
- id: fakgc6mgjtsd
  title: Terminal 1
  type: terminal
  hostname: workshop-host
  workdir: /workspace/temporal-failure-proof-python/exercises/module01
- id: mqnjxgrejxh1
  title: Temporal UI
  type: service
  hostname: workshop-host
  path: /
  port: 8080
- id: shyvk81cf8b8
  title: VS Code
  type: service
  hostname: workshop-host
  path: ?folder=/workspace/temporal-failure-proof-python/exercises/module01
  port: 8443
difficulty: ""
timelimit: 0
lab_config:
  default_layout_sidebar_size: 0
enhanced_loading: null
---
# Overview
This assigment gives you hands-on experience with Temporal Durable Execution and its ability to resume processes in-flight. Even if your applications crash, with durable execution you can pick up right where you left off.

## Learning Objectives
1. Experience Temporal Workflow state tracking and process resumability

Exercise Steps
===

## Step 1: Let's see what failures look like without Temporal.
1. This module uses `uv` as the Python package manager, so to execute the code, run the following command:
```bash,run
uv run python_print.py
```
This code runs a process that executes steps in order, with sleeps in between each step.

2. **Go to Terminal 1 [button label="Terminal 1" background="#444CE7"](tab-0):** and enter `ctrl + C` to stop the script.

Now we've killed the process.

3. Run the Script again
```bash,run
uv run python_print.py
```

Note that the script starts from the beginning - it has no concept of any run that came before or that it was mid-run and then was interrupted.

## Step 2: Now, let's see it in temporal!
1. Start the Workflow and the Temporal worker combined.
```bash,run
uv run run_workflow.py
```

2. **Go back to [button label="Terminal 1" background="#444CE7"](tab-0):** and enter `ctrl + C` to stop the worker. Note where it left off.

3. Now, restart the worker.
```bash,run
uv run run_workflow.py
```

The Workflow picks up right where it left off. It keeps track of state and doesn't repeat any steps. Keeping state mid-process is a key part of Temporal's durable execution.

Note we didn't have to write any state management or code to checkpoint what state we were on to a database. Temporal automatically keeps track of what was done and what needs to be done next in your Workflows. You can think of it like a Workflow run _remembers_ where it was as it runs, even if interrupted.

## Step 3: Check out the workflow in the Temporal UI
Now let's examine the Workflow's state as it progressed.

1. Click the **[button label="Temporal UI" background="#444CE7"](tab-1) tab** in your Instruqt envrionment.
2. The **Workflows** pane will display all recent executions
3. Locate your workflow (`print-numbers-workflow`) in the list

Take time to examine:
- **Event History:** A timeline view of all workflow events
- **Input/Results:** The data passed to and returned from your workflow
- **Workflow Timeline:** Visual representation of the execution flow

Notice how there was a gap in execution when you killed the Workflow process, but that it picked up right where it left off as soon as the process was restarted.

In a production environment, it's rare to have all workers stopped for a long time, but it's useful for this exercise to see that when you stop and restart a Temporal worker process, nothing breaks, and they can pick up right where they left off.

In later modules, we'll be using the Workflow state (memory) capability to handle harder kinds of errors.
