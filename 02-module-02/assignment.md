---
slug: module-02
id: iciq2lchxv3m
type: challenge
title: 'Module 2: Exploring Simpler Retries'
tabs:
- id: bc8hdose4qbs
  title: Terminal 1
  type: terminal
  hostname: workshop-host
  workdir: /workspace/temporal-failure-proof-python/exercises/module02
- id: ii8vcve6x0kd
  title: Terminal 2
  type: terminal
  hostname: workshop-host
  workdir: /workspace/temporal-failure-proof-python/exercises/module02
- id: re7hjtexvx4z
  title: VS Code
  type: service
  hostname: workshop-host
  path: /
  port: 8443
- id: kzyh2wa3t2qn
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


## Learning Objectives

Exercise Steps
===

## Step 1: Money movement + external API: Happy path!
1. In Terminal 1 [button label="Terminal 1" background="#444CE7"](tab-0), start the API server that interacts with bank accounts.
```bash,run
uv run account_api.py
```

2. In Terminal 2 [button label="Terminal 2" background="#444CE7"](tab-1), start the money movement process.
```bash,run
uv run move_money.py
```
Once it's complete, you can reset the "database" if you'd like by running this script:
```bash,run
uv run reset_db.py
```

3. Run money movement + retries
```bash,run
uv run move_money_retries.py
```
Still good! Sweet!

## Step 2: Money movement with external API: REAL WORLD MODE
1. In the code editor [button label="Code Editor" background="#444CE7"](tab-2), in account_api.py, change REAL_WORLD_MODE = True

2. Run money movement with retries again - feel free to do this multiple times as REAL_WORLD_MODE only *sometimes* fails...


## Step 3: Now, let's see it in Temporal!
```bash,run
uv run run_workflow.py
```

## Step 4: Check out the workflow in the Temporal UI
Now let's examine the Workflow's state as it progressed.

1. Click the **[button label="Temporal UI" background="#444CE7"](tab-3) Service tab** in your Instruqt envrionment.
2. The **Workflows** pane will display all recent executions
3. Locate your workflow (`money-transfer-workflow`) in the list

Take time to examine:
- **Event History:** A timeline view of all workflow events
- **Input/Results:** The data passed to and returned from your workflow
- **Workflow Timeline:** Visual representation of the execution flow
