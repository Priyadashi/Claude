// API Configuration
const API_BASE = window.location.origin;
const API_URL = `${API_BASE}/api`;

// State Management
const state = {
    currentView: 'optimize',
    currentJob: null,
    currentConfig: null,
    sapData: null
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeEventListeners();
    checkAPIConnection();
    setDefaultDate();
});

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            switchView(view);
        });
    });
}

function switchView(viewName) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.view === viewName) {
            item.classList.add('active');
        }
    });

    // Update views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    document.getElementById(`${viewName}-view`).classList.add('active');
    state.currentView = viewName;
}

// Event Listeners
function initializeEventListeners() {
    // Scenario buttons
    document.querySelectorAll('.btn-scenario').forEach(btn => {
        btn.addEventListener('click', () => {
            const scenario = btn.dataset.scenario;
            loadScenario(scenario);
        });
    });

    // SAP Data buttons
    document.getElementById('load-sap-data').addEventListener('click', loadSAPSampleData);
    document.getElementById('upload-sap-file').addEventListener('click', () => {
        document.getElementById('sap-file-input').click();
    });
    document.getElementById('sap-file-input').addEventListener('change', handleSAPFileUpload);

    // Config panel
    document.getElementById('close-config')?.addEventListener('click', () => {
        document.getElementById('config-panel').style.display = 'none';
    });

    // Run optimization
    document.getElementById('run-optimization').addEventListener('click', runOptimization);

    // SAP View
    document.getElementById('view-sample-sap').addEventListener('click', viewSampleSAPData);
    document.getElementById('download-template').addEventListener('click', downloadSAPTemplate);
    document.getElementById('close-sap-data')?.addEventListener('click', () => {
        document.getElementById('sap-data-display').style.display = 'none';
    });
}

// Set default date to today
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start-date').value = today;
}

// API Functions
async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            updateConnectionStatus(true);
        } else {
            updateConnectionStatus(false);
        }
    } catch (error) {
        console.error('API connection error:', error);
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(isConnected) {
    const statusEl = document.getElementById('connection-status');
    const statusDot = document.querySelector('.status-dot');

    if (isConnected) {
        statusEl.textContent = 'Connected';
        statusDot.style.background = 'var(--success)';
    } else {
        statusEl.textContent = 'Disconnected';
        statusDot.style.background = 'var(--error)';
    }
}

// Load Scenario
async function loadScenario(scenario) {
    try {
        showToast(`Loading ${scenario} scenario...`, 'info');

        // Create request with scenario
        const config = {
            scenario: scenario,
            planning_horizon: 14,
            shifts_per_day: 2,
            hours_per_shift: 8
        };

        state.currentConfig = config;
        showConfigPanel(config, scenario);
    } catch (error) {
        console.error('Error loading scenario:', error);
        showToast('Failed to load scenario', 'error');
    }
}

// Load SAP Sample Data
async function loadSAPSampleData() {
    try {
        showToast('Loading SAP sample data...', 'info');

        const response = await fetch(`${API_URL}/sap/sample-data`);
        if (!response.ok) throw new Error('Failed to load SAP data');

        const sapData = await response.json();
        state.sapData = sapData;

        // Create config from SAP data
        const config = {
            sap_data: {
                ...sapData,
                demands: [
                    { product_id: 'FG001', quantity: 100, day: 5 },
                    { product_id: 'FG002', quantity: 150, day: 7 },
                    { product_id: 'FG003', quantity: 200, day: 10 }
                ],
                planning_horizon: 14,
                shifts_per_day: 2,
                hours_per_shift: 8
            }
        };

        state.currentConfig = config;
        showConfigPanel(config, 'SAP Data');
        showToast('SAP data loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading SAP data:', error);
        showToast('Failed to load SAP data', 'error');
    }
}

// Handle SAP File Upload
async function handleSAPFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
        const text = await file.text();
        const sapData = JSON.parse(text);

        // Validate SAP data
        const response = await fetch(`${API_URL}/sap/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...sapData })
        });

        const validation = await response.json();

        if (validation.valid) {
            state.sapData = sapData;
            state.currentConfig = { sap_data: sapData };
            showConfigPanel(state.currentConfig, 'Uploaded SAP Data');
            showToast('SAP file uploaded successfully', 'success');
        } else {
            showToast(`Invalid SAP data: ${validation.message}`, 'error');
        }
    } catch (error) {
        console.error('Error uploading SAP file:', error);
        showToast('Failed to parse SAP file', 'error');
    }
}

// Show Config Panel
function showConfigPanel(config, title) {
    const panel = document.getElementById('config-panel');
    const summary = document.getElementById('config-summary');

    let summaryHTML = `<h4>${title}</h4>`;

    if (config.scenario) {
        summaryHTML += `
            <div class="config-summary-grid">
                <div class="config-stat">
                    <div class="config-stat-value">Ready</div>
                    <div class="config-stat-label">Status</div>
                </div>
            </div>
        `;
    } else if (config.sap_data) {
        const sapData = config.sap_data;
        summaryHTML += `
            <div class="config-summary-grid">
                <div class="config-stat">
                    <div class="config-stat-value">${sapData.materials?.length || 0}</div>
                    <div class="config-stat-label">Materials</div>
                </div>
                <div class="config-stat">
                    <div class="config-stat-value">${sapData.work_centers?.length || 0}</div>
                    <div class="config-stat-label">Work Centers</div>
                </div>
                <div class="config-stat">
                    <div class="config-stat-value">${sapData.routing_operations?.length || 0}</div>
                    <div class="config-stat-label">Operations</div>
                </div>
                <div class="config-stat">
                    <div class="config-stat-value">${sapData.demands?.length || 0}</div>
                    <div class="config-stat-label">Demands</div>
                </div>
            </div>
        `;
    }

    summary.innerHTML = summaryHTML;
    panel.style.display = 'block';
}

// Run Optimization
async function runOptimization() {
    try {
        if (!state.currentConfig) {
            showToast('Please load a configuration first', 'error');
            return;
        }

        // Get parameters from form
        const planningHorizon = parseInt(document.getElementById('planning-horizon').value);
        const shiftsPerDay = parseInt(document.getElementById('shifts-per-day').value);
        const hoursPerShift = parseFloat(document.getElementById('hours-per-shift').value);
        const startDate = document.getElementById('start-date').value;

        // Build request
        const request = {
            ...state.currentConfig,
            time_limit: 300,
            start_date: startDate
        };

        // Update planning parameters if SAP data
        if (request.sap_data) {
            request.sap_data.planning_horizon = planningHorizon;
            request.sap_data.shifts_per_day = shiftsPerDay;
            request.sap_data.hours_per_shift = hoursPerShift;
        }

        // Hide config panel, show progress
        document.getElementById('config-panel').style.display = 'none';
        showProgress();

        // Submit optimization
        const response = await fetch(`${API_URL}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        if (!response.ok) throw new Error('Optimization request failed');

        const result = await response.json();
        state.currentJob = result.job_id;

        showToast('Optimization started', 'success');
        pollJobStatus(result.job_id);
    } catch (error) {
        console.error('Error running optimization:', error);
        showToast('Failed to start optimization', 'error');
        hideProgress();
    }
}

// Poll Job Status
async function pollJobStatus(jobId) {
    try {
        const response = await fetch(`${API_URL}/jobs/${jobId}`);
        if (!response.ok) throw new Error('Failed to get job status');

        const job = await response.json();

        // Update progress
        updateProgress(job.progress, job.status);

        if (job.status === 'completed') {
            hideProgress();
            showResults(job.result);
            showToast('Optimization completed successfully!', 'success');
        } else if (job.status === 'failed') {
            hideProgress();
            showToast(`Optimization failed: ${job.error}`, 'error');
        } else {
            // Continue polling
            setTimeout(() => pollJobStatus(jobId), 1000);
        }
    } catch (error) {
        console.error('Error polling job status:', error);
        hideProgress();
        showToast('Failed to check optimization status', 'error');
    }
}

// Progress Functions
function showProgress() {
    document.getElementById('progress-card').style.display = 'block';
    updateProgress(0, 'running');
}

function hideProgress() {
    document.getElementById('progress-card').style.display = 'none';
}

function updateProgress(progress, status) {
    const fillEl = document.getElementById('progress-fill');
    const textEl = document.getElementById('progress-text');

    fillEl.style.width = `${progress * 100}%`;

    const statusMessages = {
        'pending': 'Queued...',
        'running': progress < 0.3 ? 'Initializing...' : progress < 0.5 ? 'Building model...' : progress < 0.9 ? 'Solving...' : 'Finalizing...',
        'completed': 'Completed!',
        'failed': 'Failed'
    };

    textEl.textContent = statusMessages[status] || 'Processing...';
}

// Show Results
function showResults(result) {
    const container = document.getElementById('results-container');

    const html = `
        <div class="results-summary">
            <div class="result-stat">
                <div class="result-stat-value">$${result.objective_value.toLocaleString(undefined, {maximumFractionDigits: 0})}</div>
                <div class="result-stat-label">Total Gross Margin</div>
                <div class="result-stat-change">✓ Optimized</div>
            </div>
            <div class="result-stat">
                <div class="result-stat-value">${result.summary.planning_horizon}</div>
                <div class="result-stat-label">Planning Days</div>
            </div>
            <div class="result-stat">
                <div class="result-stat-value">${result.production_schedule.length}</div>
                <div class="result-stat-label">Production Orders</div>
            </div>
            <div class="result-stat">
                <div class="result-stat-value">${result.summary.total_products}</div>
                <div class="result-stat-label">Products</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3>Download Results</h3>
            </div>
            <div class="card-body">
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="downloadExcel()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                        Download Excel
                    </button>
                    <button class="btn btn-secondary" onclick="downloadJSON()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                        Download JSON
                    </button>
                    <button class="btn btn-secondary" onclick="viewSchedule()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                        View Schedule
                    </button>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;

    // Also show schedule
    displaySchedule(result.daily_schedule);

    // Switch to results view
    switchView('results');
}

// Display Schedule
function displaySchedule(dailySchedule) {
    const container = document.getElementById('schedule-container');

    if (!dailySchedule || dailySchedule.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No schedule data available</p></div>';
        return;
    }

    let html = '<div class="schedule-timeline">';

    dailySchedule.forEach(day => {
        html += `
            <div class="day-card">
                <div class="day-header">
                    <div class="day-title">Day ${day.day}</div>
                    <div class="day-date">${day.date}</div>
                </div>
                <div class="shifts">
        `;

        Object.keys(day.shifts).forEach(shiftNum => {
            const shiftItems = day.shifts[shiftNum];
            html += `
                <div class="shift">
                    <div class="shift-header">Shift ${parseInt(shiftNum) + 1}</div>
            `;

            if (shiftItems.length > 0) {
                shiftItems.forEach(item => {
                    html += `
                        <div class="production-item">
                            ${item.product} on ${item.machine}: <strong>${item.quantity} units</strong>
                        </div>
                    `;
                });
            } else {
                html += '<div class="production-item" style="color: var(--text-muted);">No production scheduled</div>';
            }

            html += '</div>';
        });

        html += `
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

// Download Functions
function downloadExcel() {
    if (!state.currentJob) return;
    window.open(`${API_URL}/results/${state.currentJob}/excel`, '_blank');
}

function downloadJSON() {
    if (!state.currentJob) return;
    window.open(`${API_URL}/results/${state.currentJob}/json`, '_blank');
}

function viewSchedule() {
    switchView('schedule');
}

// SAP Data View Functions
async function viewSampleSAPData() {
    try {
        const response = await fetch(`${API_URL}/sap/sample-data`);
        if (!response.ok) throw new Error('Failed to load SAP data');

        const sapData = await response.json();
        displaySAPData(sapData);
    } catch (error) {
        console.error('Error loading SAP data:', error);
        showToast('Failed to load SAP data', 'error');
    }
}

function displaySAPData(sapData) {
    const display = document.getElementById('sap-data-display');
    const content = document.getElementById('sap-data-content');

    content.textContent = JSON.stringify(sapData, null, 2);
    display.style.display = 'block';
}

async function downloadSAPTemplate() {
    try {
        const response = await fetch(`${API_URL}/sap/sample-data`);
        if (!response.ok) throw new Error('Failed to load template');

        const data = await response.json();

        // Add demands to template
        const template = {
            ...data,
            demands: [
                { product_id: 'FG001', quantity: 100, day: 5 },
                { product_id: 'FG002', quantity: 150, day: 7 }
            ]
        };

        // Create download
        const blob = new Blob([JSON.stringify(template, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sap_data_template.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('Template downloaded', 'success');
    } catch (error) {
        console.error('Error downloading template:', error);
        showToast('Failed to download template', 'error');
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
