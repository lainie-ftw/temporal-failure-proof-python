// State management
let autoRefreshEnabled = true;
let autoRefreshInterval = null;
const REFRESH_INTERVAL = 3000; // 3 seconds

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadInitialData();
    startAutoRefresh();
});

// Initialize event listeners
function initializeEventListeners() {
    document.getElementById('transferForm').addEventListener('submit', handleTransferSubmit);
    document.getElementById('realWorldMode').addEventListener('change', handleRealWorldModeToggle);
    document.getElementById('refreshBtn').addEventListener('click', refreshData);
    document.getElementById('resetDbBtn').addEventListener('click', handleResetDatabase);
    document.getElementById('autoRefresh').addEventListener('change', handleAutoRefreshToggle);
    document.getElementById('clearHistoryBtn').addEventListener('click', clearHistory);
}

// Load initial data
async function loadInitialData() {
    await loadAccounts();
    await loadRealWorldModeStatus();
    await loadWorkflows();
}

// Refresh all data
async function refreshData() {
    await loadAccounts();
    await loadWorkflows();
}

// Load accounts from API
async function loadAccounts() {
    try {
        const response = await fetch('/api/accounts');
        if (!response.ok) throw new Error('Failed to load accounts');
        
        const accounts = await response.json();
        displayAccounts(accounts);
        populateAccountSelects(accounts);
    } catch (error) {
        console.error('Error loading accounts:', error);
        document.getElementById('accountsList').innerHTML = 
            '<div class="error">Failed to load accounts. Is the Account API running?</div>';
    }
}

// Display accounts in the UI
function displayAccounts(accounts) {
    const accountsList = document.getElementById('accountsList');
    
    if (Object.keys(accounts).length === 0) {
        accountsList.innerHTML = '<div class="empty-state">No accounts found</div>';
        return;
    }
    
    accountsList.innerHTML = Object.entries(accounts).map(([accountId, accountData]) => `
        <div class="account-item">
            <span class="account-name">${accountId}</span>
            <span class="account-balance">$${accountData.balance.toFixed(2)}</span>
        </div>
    `).join('');
}

// Populate account select dropdowns
function populateAccountSelects(accounts) {
    const fromSelect = document.getElementById('fromAccount');
    const toSelect = document.getElementById('toAccount');
    
    // Save current selections
    const currentFromValue = fromSelect.value;
    const currentToValue = toSelect.value;
    
    const options = Object.keys(accounts).map(accountId => 
        `<option value="${accountId}">${accountId}</option>`
    ).join('');
    
    fromSelect.innerHTML = '<option value="">Select account...</option>' + options;
    toSelect.innerHTML = '<option value="">Select account...</option>' + options;
    
    // Restore previous selections if they still exist
    if (currentFromValue && accounts[currentFromValue]) {
        fromSelect.value = currentFromValue;
    }
    if (currentToValue && accounts[currentToValue]) {
        toSelect.value = currentToValue;
    }
}

// Handle transfer form submission
async function handleTransferSubmit(event) {
    event.preventDefault();
    
    const fromAccount = document.getElementById('fromAccount').value;
    const toAccount = document.getElementById('toAccount').value;
    const amount = parseFloat(document.getElementById('amount').value);
    
    if (fromAccount === toAccount) {
        showMessage('error', 'Cannot transfer to the same account');
        return;
    }
    
    try {
        const response = await fetch('/api/transfer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                from_account: fromAccount,
                to_account: toAccount,
                amount: amount
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Transfer failed');
        }
        
        const result = await response.json();
        showMessage('success', `Transfer started! Workflow ID: ${result.workflow_id}`);
        
        // Reset form
        document.getElementById('transferForm').reset();
        
        // Refresh workflows immediately
        await loadWorkflows();
    } catch (error) {
        console.error('Error starting transfer:', error);
        showMessage('error', error.message);
    }
}

// Show message to user
function showMessage(type, text) {
    const messageDiv = document.getElementById('transferMessage');
    messageDiv.className = `message ${type} show`;
    messageDiv.textContent = text;
    
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 5000);
}

// Load Real World Mode status
async function loadRealWorldModeStatus() {
    try {
        const response = await fetch('/api/real-world-mode');
        if (!response.ok) throw new Error('Failed to load Real World Mode status');
        
        const data = await response.json();
        document.getElementById('realWorldMode').checked = data.enabled;
    } catch (error) {
        console.error('Error loading Real World Mode status:', error);
    }
}

// Handle Real World Mode toggle
async function handleRealWorldModeToggle(event) {
    const enabled = event.target.checked;
    
    try {
        const response = await fetch('/api/real-world-mode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ enabled })
        });
        
        if (!response.ok) throw new Error('Failed to toggle Real World Mode');
        
        console.log(`Real World Mode ${enabled ? 'enabled' : 'disabled'}`);
    } catch (error) {
        console.error('Error toggling Real World Mode:', error);
        event.target.checked = !enabled; // Revert toggle
    }
}

// Load workflows
async function loadWorkflows() {
    try {
        const response = await fetch('/api/workflows');
        if (!response.ok) throw new Error('Failed to load workflows');
        
        const workflows = await response.json();
        displayWorkflows(workflows);
    } catch (error) {
        console.error('Error loading workflows:', error);
    }
}

// Display workflows in active and history sections
function displayWorkflows(workflows) {
    const activeWorkflows = workflows.filter(w => w.status === 'RUNNING');
    const completedWorkflows = workflows.filter(w => w.status !== 'RUNNING');
    
    displayActiveWorkflows(activeWorkflows);
    displayWorkflowHistory(completedWorkflows);
}

// Display active workflows
function displayActiveWorkflows(workflows) {
    const activeList = document.getElementById('activeWorkflowsList');
    
    if (workflows.length === 0) {
        activeList.innerHTML = '<div class="empty-state">No active workflows</div>';
        return;
    }
    
    activeList.innerHTML = workflows.map(workflow => `
        <div class="workflow-item">
            <div class="workflow-header">
                <span class="workflow-id">🔄 ${workflow.workflow_id}</span>
                <span class="workflow-status running">RUNNING</span>
            </div>
            <div class="workflow-details">
                <strong>From:</strong> ${workflow.input.from_account} →
                <strong>To:</strong> ${workflow.input.to_account} |
                <strong>Amount:</strong> $${workflow.input.amount.toFixed(2)}
            </div>
        </div>
    `).join('');
}

// Display workflow history
function displayWorkflowHistory(workflows) {
    const historyList = document.getElementById('workflowHistory');
    
    if (workflows.length === 0) {
        historyList.innerHTML = '<div class="empty-state">No completed workflows</div>';
        return;
    }
    
    // Sort by completion time (most recent first)
    workflows.sort((a, b) => new Date(b.close_time || 0) - new Date(a.close_time || 0));
    
    historyList.innerHTML = workflows.map(workflow => {
        const statusClass = workflow.status === 'COMPLETED' ? 'completed' : 'failed';
        const statusText = workflow.status === 'COMPLETED' ? 'COMPLETED' : 'FAILED';
        const icon = workflow.status === 'COMPLETED' ? '✓' : '✗';
        
        return `
            <div class="workflow-item ${statusClass}">
                <div class="workflow-header">
                    <span class="workflow-id">${icon} ${workflow.workflow_id}</span>
                    <span class="workflow-status ${statusClass}">${statusText}</span>
                </div>
                <div class="workflow-details">
                    <strong>From:</strong> ${workflow.input.from_account} →
                    <strong>To:</strong> ${workflow.input.to_account} |
                    <strong>Amount:</strong> $${workflow.input.amount.toFixed(2)}
                </div>
                ${workflow.result ? formatWorkflowResult(workflow.result, workflow.status) : ''}
            </div>
        `;
    }).join('');
}

// Format workflow result
function formatWorkflowResult(result, status) {
    if (status === 'COMPLETED' && result.success) {
        return `
            <div class="workflow-result">
                <div><strong>Starting Balances:</strong></div>
                <div>${result.from_account}: $${result.from_account_starting_balance.toFixed(2)} | 
                     ${result.to_account}: $${result.to_account_starting_balance.toFixed(2)}</div>
                <div><strong>Final Balances:</strong></div>
                <div>${result.from_account}: $${result.from_account_final_balance.toFixed(2)} | 
                     ${result.to_account}: $${result.to_account_final_balance.toFixed(2)}</div>
            </div>
        `;
    } else if (status === 'FAILED') {
        return `
            <div class="workflow-result">
                <div><strong>Error:</strong> ${result.error_message || 'Workflow execution failed'}</div>
            </div>
        `;
    }
    return '';
}

// Handle database reset
async function handleResetDatabase() {
    if (!confirm('Are you sure you want to reset the database? This will restore all accounts to their initial balances.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/reset', {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Failed to reset database');
        
        alert('Database reset successfully!');
        await refreshData();
    } catch (error) {
        console.error('Error resetting database:', error);
        alert('Failed to reset database: ' + error.message);
    }
}

// Handle auto-refresh toggle
function handleAutoRefreshToggle(event) {
    autoRefreshEnabled = event.target.checked;
    
    if (autoRefreshEnabled) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
}

// Start auto-refresh
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    if (autoRefreshEnabled) {
        autoRefreshInterval = setInterval(() => {
            refreshData();
        }, REFRESH_INTERVAL);
    }
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Clear workflow history
function clearHistory() {
    if (!confirm('Are you sure you want to clear the workflow history?')) {
        return;
    }
    
    // This will be implemented on the server side
    // For now, just refresh to show the empty state
    document.getElementById('workflowHistory').innerHTML = '<div class="empty-state">No completed workflows</div>';
}
