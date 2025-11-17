// GovContracts Pro - Frontend Application

const API_BASE = '';  // Same origin

// State management
let state = {
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    currentPage: 1,
    pageSize: 50,
    totalResults: 0,
    currentView: 'dashboard'
};

// DOM Elements
const elements = {
    // Auth
    loginBtn: document.getElementById('loginBtn'),
    registerBtn: document.getElementById('registerBtn'),
    logoutBtn: document.getElementById('logoutBtn'),
    authSection: document.getElementById('authSection'),
    userSection: document.getElementById('userSection'),
    userEmail: document.getElementById('userEmail'),

    // Modals
    loginModal: document.getElementById('loginModal'),
    registerModal: document.getElementById('registerModal'),
    contractModal: document.getElementById('contractModal'),

    // Forms
    loginForm: document.getElementById('loginForm'),
    registerForm: document.getElementById('registerForm'),

    // Views
    dashboardView: document.getElementById('dashboardView'),
    searchView: document.getElementById('searchView'),

    // Dashboard
    totalContracts: document.getElementById('totalContracts'),
    openContracts: document.getElementById('openContracts'),
    closedContracts: document.getElementById('closedContracts'),
    lastUpdated: document.getElementById('lastUpdated'),
    stateChart: document.getElementById('stateChart'),

    // Search
    keywordSearch: document.getElementById('keywordSearch'),
    stateFilter: document.getElementById('stateFilter'),
    statusFilter: document.getElementById('statusFilter'),
    minValue: document.getElementById('minValue'),
    maxValue: document.getElementById('maxValue'),
    dueAfter: document.getElementById('dueAfter'),
    dueBefore: document.getElementById('dueBefore'),
    searchBtn: document.getElementById('searchBtn'),
    clearFiltersBtn: document.getElementById('clearFiltersBtn'),
    contractsList: document.getElementById('contractsList'),
    resultCount: document.getElementById('resultCount'),
    pageInfo: document.getElementById('pageInfo'),
    prevPage: document.getElementById('prevPage'),
    nextPage: document.getElementById('nextPage'),

    // Contract Detail
    contractDetail: document.getElementById('contractDetail')
};

// API Helper
async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

// Auth Functions
function updateAuthUI() {
    if (state.token && state.user) {
        elements.authSection.style.display = 'none';
        elements.userSection.style.display = 'flex';
        elements.userEmail.textContent = state.user.email;
    } else {
        elements.authSection.style.display = 'flex';
        elements.userSection.style.display = 'none';
    }
}

async function login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
    });

    if (!response.ok) {
        throw new Error('Invalid credentials');
    }

    const data = await response.json();
    state.token = data.access_token;
    localStorage.setItem('token', state.token);

    // Get user info
    const user = await apiRequest('/users/me');
    state.user = user;
    localStorage.setItem('user', JSON.stringify(user));

    updateAuthUI();
    loadDashboard();
}

async function register(userData) {
    const user = await apiRequest('/register', {
        method: 'POST',
        body: JSON.stringify(userData)
    });

    // Auto-login after registration
    await login(userData.email, userData.password);
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    updateAuthUI();
    showView('dashboard');
}

// Dashboard Functions
async function loadDashboard() {
    if (!state.token) {
        elements.totalContracts.textContent = '-';
        elements.openContracts.textContent = '-';
        elements.closedContracts.textContent = '-';
        elements.lastUpdated.textContent = 'Login required';
        elements.stateChart.innerHTML = '<p>Login to view statistics</p>';
        return;
    }

    try {
        const stats = await apiRequest('/statistics');

        elements.totalContracts.textContent = stats.total_contracts.toLocaleString();
        elements.openContracts.textContent = stats.open_contracts.toLocaleString();
        elements.closedContracts.textContent = stats.closed_contracts.toLocaleString();

        const lastUpdate = new Date(stats.last_updated);
        elements.lastUpdated.textContent = lastUpdate.toLocaleString();

        // Render state chart
        renderStateChart(stats.by_state);
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        elements.stateChart.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

function renderStateChart(byState) {
    const sortedStates = Object.entries(byState)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    if (sortedStates.length === 0) {
        elements.stateChart.innerHTML = '<p>No data available</p>';
        return;
    }

    const maxValue = sortedStates[0][1];

    let chartHTML = '';
    for (const [state, count] of sortedStates) {
        const percentage = (count / maxValue) * 100;
        chartHTML += `
            <div class="chart-bar">
                <div class="chart-bar-label">${state}</div>
                <div class="chart-bar-fill" style="width: ${percentage}%">${count}</div>
            </div>
        `;
    }

    elements.stateChart.innerHTML = chartHTML;
}

// Search Functions
async function searchContracts() {
    if (!state.token) {
        alert('Please login to search contracts');
        elements.loginModal.style.display = 'block';
        return;
    }

    const params = new URLSearchParams();

    if (elements.keywordSearch.value) {
        params.append('keyword', elements.keywordSearch.value);
    }
    if (elements.stateFilter.value) {
        params.append('state', elements.stateFilter.value);
    }
    if (elements.statusFilter.value) {
        params.append('status', elements.statusFilter.value);
    }
    if (elements.minValue.value) {
        params.append('min_value', elements.minValue.value);
    }
    if (elements.maxValue.value) {
        params.append('max_value', elements.maxValue.value);
    }
    if (elements.dueAfter.value) {
        params.append('due_after', new Date(elements.dueAfter.value).toISOString());
    }
    if (elements.dueBefore.value) {
        params.append('due_before', new Date(elements.dueBefore.value).toISOString());
    }

    params.append('page', state.currentPage);
    params.append('page_size', state.pageSize);

    try {
        elements.contractsList.innerHTML = '<p>Loading...</p>';

        const results = await apiRequest(`/contracts?${params}`);
        state.totalResults = results.total;

        elements.resultCount.textContent = results.total.toLocaleString();
        elements.pageInfo.textContent = `Page ${state.currentPage} of ${Math.ceil(results.total / state.pageSize) || 1}`;

        // Update pagination buttons
        elements.prevPage.disabled = state.currentPage <= 1;
        elements.nextPage.disabled = state.currentPage * state.pageSize >= results.total;

        renderContracts(results.contracts);
    } catch (error) {
        console.error('Search failed:', error);
        elements.contractsList.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
}

function renderContracts(contracts) {
    if (contracts.length === 0) {
        elements.contractsList.innerHTML = '<p class="no-results">No contracts found matching your criteria.</p>';
        return;
    }

    let html = '';
    for (const contract of contracts) {
        const statusClass = contract.status ? `status-${contract.status}` : 'status-unknown';
        const dueDate = contract.due_date ? new Date(contract.due_date).toLocaleDateString() : 'Not specified';
        const value = contract.estimated_value
            ? `$${contract.estimated_value.toLocaleString()}`
            : (contract.budget_max ? `Up to $${contract.budget_max.toLocaleString()}` : 'Not specified');

        const description = contract.description
            ? (contract.description.length > 200
                ? contract.description.substring(0, 200) + '...'
                : contract.description)
            : 'No description available';

        html += `
            <div class="contract-card">
                <h4 onclick="showContractDetail(${contract.id})">${escapeHtml(contract.title)}</h4>
                <div class="contract-meta">
                    <span><span class="status-badge ${statusClass}">${contract.status || 'Unknown'}</span></span>
                    <span><strong>State:</strong> ${escapeHtml(contract.state || 'N/A')}</span>
                    <span><strong>Agency:</strong> ${escapeHtml(contract.agency || 'N/A')}</span>
                    <span><strong>Due:</strong> ${dueDate}</span>
                    <span><strong>Value:</strong> ${value}</span>
                </div>
                <p class="contract-description">${escapeHtml(description)}</p>
            </div>
        `;
    }

    elements.contractsList.innerHTML = html;
}

async function showContractDetail(contractId) {
    if (!state.token) {
        alert('Please login to view contract details');
        return;
    }

    try {
        const contract = await apiRequest(`/contracts/${contractId}`);

        const postedDate = contract.posted_date ? new Date(contract.posted_date).toLocaleDateString() : 'N/A';
        const dueDate = contract.due_date ? new Date(contract.due_date).toLocaleDateString() : 'N/A';
        const closeDate = contract.close_date ? new Date(contract.close_date).toLocaleDateString() : 'N/A';

        let detailHTML = `
            <h2>${escapeHtml(contract.title)}</h2>

            <div class="detail-section">
                <h3>Basic Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Status</span>
                        <span class="detail-value">
                            <span class="status-badge status-${contract.status || 'unknown'}">
                                ${contract.status || 'Unknown'}
                            </span>
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">External ID</span>
                        <span class="detail-value">${escapeHtml(contract.external_id)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">State</span>
                        <span class="detail-value">${escapeHtml(contract.state || 'N/A')}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Agency</span>
                        <span class="detail-value">${escapeHtml(contract.agency || 'N/A')}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Department</span>
                        <span class="detail-value">${escapeHtml(contract.department || 'N/A')}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Category</span>
                        <span class="detail-value">${escapeHtml(contract.category || 'N/A')}</span>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h3>Important Dates</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Posted Date</span>
                        <span class="detail-value">${postedDate}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Due Date</span>
                        <span class="detail-value">${dueDate}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Close Date</span>
                        <span class="detail-value">${closeDate}</span>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h3>Financial Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Estimated Value</span>
                        <span class="detail-value">${contract.estimated_value ? '$' + contract.estimated_value.toLocaleString() : 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Budget Range</span>
                        <span class="detail-value">
                            ${contract.budget_min || contract.budget_max
                                ? `$${(contract.budget_min || 0).toLocaleString()} - $${(contract.budget_max || 0).toLocaleString()}`
                                : 'N/A'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">NAICS Code</span>
                        <span class="detail-value">${escapeHtml(contract.naics_code || 'N/A')}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Set-Aside</span>
                        <span class="detail-value">${escapeHtml(contract.set_aside || 'None')}</span>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h3>Description</h3>
                <p>${escapeHtml(contract.description || 'No description available')}</p>
            </div>

            <div class="detail-section">
                <h3>Contact Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">Contact Name</span>
                        <span class="detail-value">${escapeHtml(contract.contact_name || 'N/A')}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Email</span>
                        <span class="detail-value">${contract.contact_email
                            ? `<a href="mailto:${escapeHtml(contract.contact_email)}">${escapeHtml(contract.contact_email)}</a>`
                            : 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Phone</span>
                        <span class="detail-value">${escapeHtml(contract.contact_phone || 'N/A')}</span>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h3>Links</h3>
                <p><a href="${escapeHtml(contract.url)}" target="_blank">View Original Contract</a></p>
            </div>
        `;

        elements.contractDetail.innerHTML = detailHTML;
        elements.contractModal.style.display = 'block';
    } catch (error) {
        console.error('Failed to load contract:', error);
        alert('Failed to load contract details: ' + error.message);
    }
}

function clearFilters() {
    elements.keywordSearch.value = '';
    elements.stateFilter.value = '';
    elements.statusFilter.value = '';
    elements.minValue.value = '';
    elements.maxValue.value = '';
    elements.dueAfter.value = '';
    elements.dueBefore.value = '';
    state.currentPage = 1;
}

// View Navigation
function showView(viewName) {
    state.currentView = viewName;

    elements.dashboardView.style.display = viewName === 'dashboard' ? 'block' : 'none';
    elements.searchView.style.display = viewName === 'search' ? 'block' : 'none';

    if (viewName === 'dashboard') {
        loadDashboard();
    }
}

// Utility Functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize
    updateAuthUI();
    loadDashboard();

    // Navigation
    document.getElementById('dashboardLink').addEventListener('click', (e) => {
        e.preventDefault();
        showView('dashboard');
    });

    document.getElementById('searchLink').addEventListener('click', (e) => {
        e.preventDefault();
        showView('search');
    });

    // Auth buttons
    elements.loginBtn.addEventListener('click', () => {
        elements.loginModal.style.display = 'block';
    });

    elements.registerBtn.addEventListener('click', () => {
        elements.registerModal.style.display = 'block';
    });

    elements.logoutBtn.addEventListener('click', logout);

    // Close modals
    document.getElementById('closeLogin').addEventListener('click', () => {
        elements.loginModal.style.display = 'none';
    });

    document.getElementById('closeRegister').addEventListener('click', () => {
        elements.registerModal.style.display = 'none';
    });

    document.getElementById('closeContract').addEventListener('click', () => {
        elements.contractModal.style.display = 'none';
    });

    // Login form
    elements.loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            await login(email, password);
            elements.loginModal.style.display = 'none';
            document.getElementById('loginError').textContent = '';
        } catch (error) {
            document.getElementById('loginError').textContent = error.message;
        }
    });

    // Register form
    elements.registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userData = {
            email: document.getElementById('regEmail').value,
            password: document.getElementById('regPassword').value,
            full_name: document.getElementById('regFullName').value || null,
            company_name: document.getElementById('regCompany').value || null
        };

        try {
            await register(userData);
            elements.registerModal.style.display = 'none';
            document.getElementById('registerError').textContent = '';
        } catch (error) {
            document.getElementById('registerError').textContent = error.message;
        }
    });

    // Search
    elements.searchBtn.addEventListener('click', () => {
        state.currentPage = 1;
        searchContracts();
    });

    elements.clearFiltersBtn.addEventListener('click', clearFilters);

    // Pagination
    elements.prevPage.addEventListener('click', () => {
        if (state.currentPage > 1) {
            state.currentPage--;
            searchContracts();
        }
    });

    elements.nextPage.addEventListener('click', () => {
        if (state.currentPage * state.pageSize < state.totalResults) {
            state.currentPage++;
            searchContracts();
        }
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === elements.loginModal) {
            elements.loginModal.style.display = 'none';
        }
        if (e.target === elements.registerModal) {
            elements.registerModal.style.display = 'none';
        }
        if (e.target === elements.contractModal) {
            elements.contractModal.style.display = 'none';
        }
    });

    // Enter key to search
    elements.keywordSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            state.currentPage = 1;
            searchContracts();
        }
    });
});

// Global function for contract detail
window.showContractDetail = showContractDetail;
