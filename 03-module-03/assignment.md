---
slug: module-03
id: uuxemlx82xa0
type: challenge
title: 'Module 3: Exploring Failure-Proof Downstream Systems'
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
**TODO: Update this re: words about: now we have a UI, yay visibility (queries), larger scale business problem solving, and what's the end user experience if a system built on Temporal has to deal with Real World Mode**

_Words from Module 2's opener:_
This assigment gives you hands-on experience with a major part of the _Durable_ in Durable Execution.

We're going to work with an application that is slightly more complex. Our module 2 application will:
- execute a business-related process
- connect to an [API](https://www.geeksforgeeks.org/software-testing/what-is-an-api/) that is _somewhat_ unreliable

We'll explore Temporal Activities, and how they automatically retry errors as you configure them. We'll compare them with how you might handle errors without Durable Execution, and why that might be a bit complex or even painful.

## Learning Objectives
**TODO: update this**
1. Hands on experience with code that calls an unreliable API
2. How to solve unreliability with code - and pros and cons
3. How to solve unreliability with Durable Execution and _durable error handling_

Exercise Steps
===

## Step 1: Setup

1. In [button label="Terminal 1" background="#444CE7"](tab-0), run the included script that will start three things: 1) the `account_api` we used before, 2) the Temporal worker we used before, and 3) a new API called `money_transfer_api` that helps to facilitate communication between a new UI and money transfer actions - which are in this case Temporal Workflow actions.
```bash,run
./start_services.sh
```

The output of this script will show the Workflow and Activity logger statements as you start money transfer Workflows.

Feel free to take a look at the new API in the [button label="Code Editor" background="#444CE7"](tab-2) in the exercises/module03 folder!

## Step 2: REAL WORLD MODE!
Check out the [button label="Money Transfer UI" background="#444CE7"](tab-1), and move some money around! You can reset the database at any time by hitting the Reset Database button on the top of the UI.

1. Move some money between accounts with Real World Mode turned off (this is how it will load by default).
2. Turn on Real World Mode, and move some money between accounts. What do you notice as the end user?

Take a look at the workflows in the [button label="Temporal UI" background="#444CE7"](tab-3) - note that failures are still occurring while Real World Mode is turned on.

## Step 3: Now, let's see how it works with Temporal!
**TODO: add some words re: look at the cool workflows on the bottom! (screenshot of UI, talk about queries)**
You can see in the Workflow code in the editor [button label="Code Editor" background="#444CE7"](tab-2)  **TODO: add words re: how the query is implemented**

## Step 4: Check out the workflow in the Temporal UI
Now let's examine the Workflow's state as it progressed.

1. Click the **[button label="Temporal UI" background="#444CE7"](tab-3) Service tab** in your Instruqt envrionment.
2. The **Workflows** pane will display all recent executions
3. Compare the workflows in the Temporal UI with what's shown in the Money Transfer UI

Take time to examine:
- **Event History:** A timeline view of all workflow events
- **Input/Results:** The data passed to and returned from your workflow
- **Workflow Timeline:** Visual representation of the execution flow

4. Check out the Activity calls, notice the different color and time taken for the ones that failed in attempts before succeeding. Did any fail completely?
5. Check out an Activity that failed at least once. Can you tell any details about the failure? (Hint: look for Last Failure Details!)

The durability in handling retries and timeouts combined with the visibility into state and failures is what we mean by _durable error handling_.
