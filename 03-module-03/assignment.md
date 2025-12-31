---
slug: module-03
id: uuxemlx82xa0
type: challenge
title: 'Module 3: Exploring Failure-Proof User Experiences'
tabs:
- id: mxyzus22wk72
  title: Terminal 1
  type: terminal
  hostname: workshop-host
  workdir: /workspace/temporal-failure-proof-python/exercises/module03
- id: 6ybiuzwvxyft
  title: Money Transfer UI
  type: service
  hostname: workshop-host
  path: /
  port: 5001
- id: o6wapk8vtrfa
  title: VS Code
  type: service
  hostname: workshop-host
  path: /
  port: 8443
- id: mecu4v6zqf0b
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
This module gives you hands-on experience in how Temporal makes for durable user experiences.

We're going to explore how it feels to work with money movement transactions as a user would. We will:
- have a user interface you can interact with to start transactions and monitor them
- execute multiple business-related process
- connect again to an [API](https://www.geeksforgeeks.org/software-testing/what-is-an-api/) that is _somewhat_ unreliable
- pull information from Workflows as they execute
- examine how many transactions at a time can be challenging to debug using only logs

## Learning Objectives
1. Hands on experience with a user interface that works with Temporal Workflows
2. How to get information from running Workflows with Queries
3. How to explore multiple running processes using the Temporal UI, Queries, and Search Attributes
4. Consideration of visibility without Temporal

Exercise Steps
===

## Step 1: Setup

In [button label="Terminal 1" background="#444CE7"](tab-0), run the included script that will start three things:
1. the `account_api` we used before
2. the Temporal worker we used before
3. a new API called `money_transfer_api` that helps to facilitate communication between a new UI and money transfer actions - which are, in this case, Temporal Workflow actions.
```bash,run
./start_services.sh
```

The output of this script will show the Workflow and Activity logger statements as you start money transfer Workflows.

Feel free to take a look at the new API in the [button label="Code Editor" background="#444CE7"](tab-2) in the exercises/module03 folder!

## Step 2: Start Transfers using a UI
Check out the [button label="Money Transfer UI" background="#444CE7"](tab-1), and move some money around! You can reset the database at any time by hitting the Reset Database button on the top of the UI.

1. Move some money between accounts with Real World Mode turned off (this is how it will load by default).
2. Turn on Real World Mode, and move some money between accounts. What do you notice as the end user?
3. Start the daily processing by hitting the **Start Daily Batch 🚀** button. This will execute multiple transfers.

Take a look at the workflows in the [button label="Temporal UI" background="#444CE7"](tab-3) - note that failures are still occurring while Real World Mode is turned on.

Click into the Workflows. 
- How many had errors in their Activities? 
- What was the maximum number of retries needed in our real-world mode?
- Did any fail completely?

Consider if we had to debug these via logs only, without Temporal?
- How would we find failed transfers?
- How would we connect failures in logs to specific transactions?
- Without retries, we would have to find which transactions failed. Have you ever built this monitoring without Temporal? 
- Consider what would happen if we had multiple transfers in flight if our application crashed. Have you had something like this happen before?

## Step 3: Now, let's see how it works with Temporal!

You can see in the Workflow code in the editor [button label="Code Editor" background="#444CE7"](tab-2).
Check out the `@workflow.query` and 

**TODO: add some words re: the custom search attributes and how the account view works**

## Step 4: Check out the workflow in the Temporal UI
Now let's examine the Workflow's state as it progressed.

1. Click the [button label="Temporal UI" background="#444CE7"](tab-3).
2. The **Workflows** pane will display all recent executions
3. Compare the workflows in the Temporal UI with what's shown in the Money Transfer UI

Take time to examine:
- **Event History:** A timeline view of all workflow events
- **Input/Results:** The data passed to and returned from your workflow
- **Workflow Timeline:** Visual representation of the execution flow

4. Check out the Activity calls, notice the different color and time taken for the ones that failed in attempts before succeeding. Did any fail completely?
5. Check out an Activity that failed at least once. Can you tell any details about the failure? (Hint: look for Last Failure Details!)

The durability in handling retries and timeouts combined with the visibility into state and failures is what we mean by _durable error handling_.
