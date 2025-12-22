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
- id: 3j6zghuaoxs5
  title: Terminal 2
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
  path: /
  port: 8443
difficulty: ""
timelimit: 0
lab_config:
  default_layout_sidebar_size: 0
enhanced_loading: null
---
# Overview


## Learning Objectives

Exercise Steps
===

## Step 1: Let's see what failures look like without Temporal.
1. This module uses `uv` as the Python package manager, so to execute the code, run the following command:
```bash,run
uv run python_print.py
```

2. **Go to Terminal 1 [button label="Terminal 1" background="#444CE7"](tab-0):** and enter `ctrl + C` to stop the script.

3. Run the Script again
```bash,run
uv run python_print.py
```

Note that the script starts from the beginning - it has no concept of any run that came before or that it was mid-run and then failed.

## Step 2: Now, let's see it in temporal!
1. Start the worker
```bash,run
uv run worker.py
```

2. Run the workflow starter
**Switch to [button label="Terminal 2" background="#444CE7"](tab-1)** and run:
```bash,run
uv run starter.py
```

3. **Go back to [button label="Terminal 1" background="#444CE7"](tab-0):** and enter `ctrl + C` to stop the worker. Note where it left off.

4. Now, restart the worker.
```bash,run
uv run worker.py
```

TADAAAAA!

## Step 3: Check out the workflow in the Temporal UI
1. Click the **[button label="Temporal UI" background="#444CE7"](tab-2) Service tab** in your Instruqt envrionment.
2. The **Workflows** pane will display all recent executions
3. Locate your workflow (`print-numbers-workflow`) in the list

Take time to examine:
- **Event History:** A timeline view of all workflow events
- **Input/Results:** The data passed to and returned from your workflow
- **Workflow Timeline:** Visual representation of the execution flow
