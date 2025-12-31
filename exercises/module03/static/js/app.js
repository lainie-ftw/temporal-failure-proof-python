// State management
let autoRefreshEnabled = true;
let autoRefreshInterval = null;
const REFRESH_INTERVAL = 200; // 200ms for faster updates
let expandedAccounts = new Set(); // Track which accounts have expanded history
let accountsData = {}; // Store accounts data for dropdown population

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
    document.getElementById('startBatchBtn').addEventListener('click', handleStartDailyBatch);
    document.getElementById('refreshBtn').addEventListener('click', refreshData);
    document.getElementById('resetDbBtn').addEventListener('click', handleResetDatabase);
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
    
    // Refresh expanded account histories
    for (const accountId of expandedAccounts) {
        await refreshAccountHistory(accountId);
    }
}

// Load accounts from API
async function loadAccounts() {
    try {
        const response = await fetch('/api/accounts');
        if (!response.ok) throw new Error('Failed to load accounts');
        
        const accounts = await response.json();
        accountsData = accounts; // Store for dropdown population
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
    
    // Check if accounts list already exists
    const existingWrappers = accountsList.querySelectorAll('.account-wrapper');
    
    if (existingWrappers.length > 0) {
        // Update existing accounts instead of regenerating
        Object.entries(accounts).forEach(([accountId, accountData]) => {
            const balanceElement = document.querySelector(`#account-wrapper-${accountId} .account-balance`);
            if (balanceElement) {
                balanceElement.textContent = `$${accountData.balance.toFixed(2)}`;
            }
        });
    } else {
        // Initial render
        accountsList.innerHTML = Object.entries(accounts).map(([accountId, accountData]) => {
            const isExpanded = expandedAccounts.has(accountId);
            const icon = isExpanded ? '▼' : '▶';
            
            return `
                <div class="account-wrapper" id="account-wrapper-${accountId}">
                    <div class="account-item">
                        <div class="account-info">
                            <span class="account-name">${accountId}</span>
                            <span class="account-balance">$${accountData.balance.toFixed(2)}</span>
                        </div>
                        <button class="btn-toggle-history" onclick="toggleAccountHistory('${accountId}')">
                            <span id="icon-${accountId}">${icon}</span> History
                        </button>
                    </div>
                    <div class="account-history-inline" id="history-${accountId}" style="display: ${isExpanded ? 'block' : 'none'};">
                        <div class="loading-inline">Loading history...</div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

// Populate account select dropdowns
function populateAccountSelects(accounts) {
    const fromSelect = document.getElementById('fromAccount');
    const toSelect = document.getElementById('toAccount');
    
    // Skip update if either dropdown is currently focused (user is selecting)
    if (document.activeElement === fromSelect || document.activeElement === toSelect) {
        return;
    }
    
    // Save current selections
    const currentFromValue = fromSelect.value;
    const currentToValue = toSelect.value;
    
    // Include balance information in dropdown options
    const options = Object.entries(accounts).map(([accountId, accountData]) => 
        `<option value="${accountId}">${accountId} ($${accountData.balance.toFixed(2)})</option>`
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

// Get human-readable step label with account info
function getStepLabel(step, input) {
    const fromAccount = input?.from_account || '...';
    const toAccount = input?.to_account || '...';
    
    switch (step) {
        case 'check_balance_from':
            return `Check Balance (${fromAccount})`;
        case 'check_balance_to':
            return `Check Balance (${toAccount})`;
        case 'withdraw':
            return 'Withdraw';
        case 'deposit':
            return 'Deposit';
        default:
            return step;
    }
}

// Render step progress visual for a workflow
function renderStepProgress(workflow, allCompleted = false) {
    const steps = workflow.steps || ['check_balance_from', 'check_balance_to', 'withdraw', 'deposit'];
    const completedSteps = allCompleted ? steps : (workflow.completed_steps || []);
    const currentStep = workflow.current_step;
    const input = workflow.input || {};
    
    return `
        <div class="step-progress">
            ${steps.map((step, index) => {
                const isCompleted = completedSteps.includes(step);
                const isCurrent = step === currentStep && !isCompleted;
                const stepClass = isCompleted ? 'completed' : (isCurrent ? 'current' : 'pending');
                const icon = isCompleted ? '✓' : (isCurrent ? '●' : '○');
                const label = getStepLabel(step, input);
                
                return `
                    <div class="step ${stepClass}">
                        <span class="step-icon">${icon}</span>
                        <span class="step-label">${label}</span>
                    </div>
                    ${index < steps.length - 1 ? '<span class="step-arrow">→</span>' : ''}
                `;
            }).join('')}
        </div>
    `;
}

// Display active workflows
function displayActiveWorkflows(workflows) {
    const activeList = document.getElementById('activeWorkflowsList');
    
    if (workflows.length === 0) {
        activeList.innerHTML = '<div class="empty-state">No active workflows</div>';
        return;
    }
    
    activeList.innerHTML = workflows.map(workflow => {
        const input = workflow.input || {};
        const fromAccount = input.from_account || 'Unknown';
        const toAccount = input.to_account || 'Unknown';
        const amount = input.amount || 0;
        
        return `
            <div class="workflow-item">
                <div class="workflow-header">
                    <span class="workflow-id">🔄 ${workflow.workflow_id}</span>
                    <span class="workflow-status running">RUNNING</span>
                </div>
                <div class="workflow-details">
                    <strong>From:</strong> ${fromAccount} →
                    <strong>To:</strong> ${toAccount} |
                    <strong>Amount:</strong> $${amount.toFixed(2)}
                </div>
                ${renderStepProgress(workflow)}
            </div>
        `;
    }).join('');
}

// Format timestamp to human-readable date/time
function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    
    // Handle both Unix timestamps (seconds) and ISO strings
    const date = typeof timestamp === 'number' 
        ? new Date(timestamp * 1000)  // Unix timestamp in seconds
        : new Date(timestamp);
    
    if (isNaN(date.getTime())) return 'N/A';
    
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
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
        
        // Format timestamps
        const startedAt = formatTimestamp(workflow.start_time);
        const completedAt = formatTimestamp(workflow.close_time);
        
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
                <div class="workflow-timestamps">
                    <span><strong>Started:</strong> ${startedAt}</span>
                    <span><strong>Completed:</strong> ${completedAt}</span>
                </div>
                ${renderStepProgress(workflow, workflow.status === 'COMPLETED')}
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

// Handle Start Daily Batch - starts 5 transfers of $100 each
async function handleStartDailyBatch() {
    const batchTransfers = [
        { from_account: 'account_A', to_account: 'account_F', amount: 100 },
        { from_account: 'account_B', to_account: 'account_G', amount: 100 },
        { from_account: 'account_C', to_account: 'account_H', amount: 100 },
        { from_account: 'account_D', to_account: 'account_I', amount: 100 },
        { from_account: 'account_E', to_account: 'account_J', amount: 100 }
    ];
    
    const btn = document.getElementById('startBatchBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Starting batch...';
    
    let successCount = 0;
    let failCount = 0;
    const workflowIds = [];
    
    try {
        for (const transfer of batchTransfers) {
            try {
                const response = await fetch('/api/transfer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(transfer)
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Transfer failed');
                }
                
                const result = await response.json();
                workflowIds.push(result.workflow_id);
                successCount++;
            } catch (error) {
                console.error(`Error starting transfer ${transfer.from_account} -> ${transfer.to_account}:`, error);
                failCount++;
            }
        }
        
        // Show results
        if (successCount === batchTransfers.length) {
            showMessage('success', `Daily batch started! ${successCount} workflows initiated.`);
        } else if (successCount > 0) {
            showMessage('error', `Batch partially started: ${successCount} succeeded, ${failCount} failed.`);
        } else {
            showMessage('error', 'Failed to start daily batch. Check if services are running.');
        }
        
        // Refresh workflows to show the new batch
        await loadWorkflows();
        
    } finally {
        btn.disabled = false;
        btn.textContent = '🚀 Start Daily Batch';
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

// ============================================================================
// Account History Functions (Inline)
// ============================================================================

// Toggle account history inline
async function toggleAccountHistory(accountId) {
    const historyDiv = document.getElementById(`history-${accountId}`);
    const icon = document.getElementById(`icon-${accountId}`);
    
    if (expandedAccounts.has(accountId)) {
        // Collapse
        expandedAccounts.delete(accountId);
        historyDiv.style.display = 'none';
        icon.textContent = '▶';
    } else {
        // Expand
        expandedAccounts.add(accountId);
        historyDiv.style.display = 'block';
        icon.textContent = '▼';
        
        // Load history
        await loadAccountHistoryInline(accountId);
    }
}

// Load account history inline
async function loadAccountHistoryInline(accountId) {
    const historyDiv = document.getElementById(`history-${accountId}`);
    
    try {
        const response = await fetch(`/api/accounts/${accountId}/workflows`);
        if (!response.ok) throw new Error('Failed to load account history');
        
        const data = await response.json();
        displayAccountHistoryInline(accountId, data);
    } catch (error) {
        console.error('Error loading account history:', error);
        historyDiv.innerHTML = '<div class="error-inline">Failed to load history</div>';
    }
}

// Refresh account history for an expanded account
async function refreshAccountHistory(accountId) {
    if (!expandedAccounts.has(accountId)) return;
    
    const historyDiv = document.getElementById(`history-${accountId}`);
    if (!historyDiv) return;
    
    try {
        const response = await fetch(`/api/accounts/${accountId}/workflows`);
        if (!response.ok) throw new Error('Failed to load account history');
        
        const data = await response.json();
        displayAccountHistoryInline(accountId, data);
    } catch (error) {
        console.error('Error refreshing account history:', error);
    }
}

// Display account history inline
function displayAccountHistoryInline(accountId, data) {
    const historyDiv = document.getElementById(`history-${accountId}`);
    const { summary, workflows } = data;
    
    let html = `
        <div class="inline-summary">
            <div class="inline-summary-item">
                <span class="inline-label">Sent:</span>
                <span class="inline-value negative">$${summary.total_sent.toFixed(2)}</span>
            </div>
            <div class="inline-summary-item">
                <span class="inline-label">Received:</span>
                <span class="inline-value positive">$${summary.total_received.toFixed(2)}</span>
            </div>
            <div class="inline-summary-item">
                <span class="inline-label">Net:</span>
                <span class="inline-value ${summary.net_change >= 0 ? 'positive' : 'negative'}">
                    ${summary.net_change >= 0 ? '+' : ''}$${summary.net_change.toFixed(2)}
                </span>
            </div>
            <div class="inline-summary-item">
                <span class="inline-label">Count:</span>
                <span class="inline-value">${summary.transaction_count}</span>
            </div>
        </div>
        <div class="inline-transactions">
    `;
    
    if (workflows.length === 0) {
        html += '<div class="empty-state-inline">No transactions</div>';
    } else {
        html += workflows.slice(0, 5).map(workflow => {
            const input = workflow.input || {};
            const direction = workflow.direction;
            const counterparty = workflow.counterparty || 'Unknown';
            const amount = input.amount || 0;
            const status = workflow.status;
            const statusIcon = status === 'COMPLETED' ? '✓' : (status === 'RUNNING' ? '🔄' : '✗');
            const directionIcon = direction === 'sent' ? '→' : '←';
            
            return `
                <div class="inline-transaction ${direction}">
                    <span class="transaction-icon">${directionIcon}</span>
                    <span class="transaction-counterparty">${counterparty}</span>
                    <span class="transaction-amount ${direction === 'sent' ? 'negative' : 'positive'}">
                        ${direction === 'sent' ? '-' : '+'}$${amount.toFixed(2)}
                    </span>
                    <span class="transaction-status">${statusIcon}</span>
                </div>
            `;
        }).join('');
        
        if (workflows.length > 5) {
            html += `<div class="show-more">Showing 5 of ${workflows.length} transactions</div>`;
        }
    }
    
    html += '</div>';
    historyDiv.innerHTML = html;
}
