<template>
    <div class="admin-dashboard">
        <div class="header">
            <h1>Admin Analytics Hub</h1>
            <p>Institute-level performance and AI adoption metrics</p>
        </div>

        <div v-if="loading" class="loading-state">
            <div class="loader"></div>
            <p>Crunching numbers...</p>
        </div>
        <div v-else-if="error" class="error-state">{{ error }}</div>

        <div v-else class="content-wrapper">
            <!-- High Level KPI Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon institute">🏛️</div>
                    <div class="stat-info">
                        <h3>Institutes</h3>
                        <p class="value">{{ stats.institute_count }}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon manager">👔</div>
                    <div class="stat-info">
                        <h3>Total Managers</h3>
                        <p class="value">{{ stats.manager_count }}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon user">👥</div>
                    <div class="stat-info">
                        <h3>Overall Users</h3>
                        <p class="value">{{ stats.user_count }}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon ai">⚡</div>
                    <div class="stat-info">
                        <h3>AI Tool Usage</h3>
                        <p class="value">{{ stats.ai_usage_count }}</p>
                    </div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="charts-row">
                <div class="chart-container">
                    <h3>Growth Trends (Last 30 Days)</h3>
                    <div class="chart-wrapper">
                        <Line :data="trendChartData" :options="chartOptions" />
                    </div>
                </div>
                <div class="chart-container">
                    <h3>AI Activity by Domain</h3>
                    <div class="chart-wrapper">
                        <Bar :data="instituteChartData" :options="chartOptions" />
                    </div>
                </div>
            </div>

            <!-- Institute Breakdown Table -->
            <div class="data-section">
                <div class="section-header">
                    <div class="title-group">
                        <h2>Institute Comparison</h2>
                        <div class="search-box inst-search">
                            <input v-model="instSearchQuery" placeholder="Search by domain..." class="search-input">
                        </div>
                    </div>
                    <button @click="exportData" class="export-btn">Download CSV</button>
                </div>
                <div class="table-card">
                    <table>
                        <thead>
                            <tr>
                                <th>Domain / Institute</th>
                                <th>Users</th>
                                <th>Managers</th>
                                <th>AI Actions</th>
                                <th>Block Status</th>
                                <th v-if="isSuperAdmin">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="inst in filteredInstitutes" :key="inst.domain">
                                <td>
                                    <span class="domain-badge">{{ inst.domain }}</span>
                                </td>
                                <td>{{ inst.user_count }}</td>
                                <td>{{ inst.manager_count }}</td>
                                <td>{{ inst.ai_usage }}</td>
                                <td>
                                    <label class="toggle-switch">
                                        <input type="checkbox" :checked="inst.is_blocked"
                                            @change="initiateAction('block_toggle', inst.domain, $event.target.checked)">
                                        <span class="slider round"></span>
                                    </label>
                                </td>
                                <td v-if="isSuperAdmin">
                                    <div class="action-buttons">
                                        <button @click="scrollToUsers(inst.domain)" class="btn-icon"
                                            title="Search Students">🔍</button>
                                        <button @click="initiateAction('delete', inst.domain)"
                                            class="btn-icon delete-btn" title="Delete Institute">🗑️</button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Top AI Users -->
            <div class="data-section">
                <h2>Top 10 Active Users (AI Adoption)</h2>
                <div class="top-users-grid">
                    <div v-for="user in topUsers" :key="user.email" class="user-chip">
                        <div class="user-rank">{{ user.count }}</div>
                        <div class="user-meta">
                            <span class="name">{{ user.username }}</span>
                            <span class="email">{{ user.email }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- User Management Component -->
            <div class="management-section">
                <UserManagement :initialSearch="externalUserSearch" />
            </div>
        </div>

        <!-- Confirmation Modal -->
        <div v-if="showModal" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>{{ modalTitle }}</h2>
                    <button @click="closeModal" class="close-btn">×</button>
                </div>

                <div class="modal-body">
                    <!-- Step 1: Initial Warning -->
                    <div v-if="modalStep === 1">
                        <p class="warning-text">{{ initialWarningText }}</p>
                        <div class="modal-actions">
                            <button @click="closeModal" class="btn-secondary">Cancel</button>
                            <button @click="nextStep" class="btn-danger">Yes, I'm sure</button>
                        </div>
                    </div>

                    <!-- Step 2: Double Confirmation -->
                    <div v-if="modalStep === 2">
                        <p class="warning-text strong">⚠️ This action is serious. Are you absolutely certain?</p>
                        <p v-if="pendingAction.type === 'delete'" class="sub-warning">This will permanently delete ALL
                            users and data for this institute.</p>
                        <div class="modal-actions">
                            <button @click="closeModal" class="btn-secondary">Cancel</button>
                            <button @click="nextStep" class="btn-danger">Proceed</button>
                        </div>
                    </div>

                    <!-- Step 3: Password Verification -->
                    <div v-if="modalStep === 3">
                        <p>Please enter your Admin Password to confirm:</p>
                        <input type="password" v-model="adminPassword" class="password-input"
                            placeholder="Admin Password" @keyup.enter="executeAction">
                        <div v-if="passwordError" class="error-msg">{{ passwordError }}</div>
                        <div class="modal-actions">
                            <button @click="closeModal" class="btn-secondary">Cancel</button>
                            <button @click="executeAction" class="btn-primary" :disabled="verifying">
                                {{ verifying ? 'Verifying...' : 'Confirm' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import UserManagement from '../components/UserManagement.vue'
import { Line, Bar } from 'vue-chartjs'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    BarElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Filler
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, BarElement, PointElement, CategoryScale, LinearScale, Filler)

const loading = ref(true)
const error = ref(null)
const stats = ref({})
const institutes = ref([])
const topUsers = ref([])
const trends = ref({ registrations: [], ai_usage: [] })
const instSearchQuery = ref('')
const externalUserSearch = ref('')

// Modal State
const showModal = ref(false)
const modalStep = ref(1)
const adminPassword = ref('')
const passwordError = ref('')
const verifying = ref(false)
const pendingAction = ref(null) // { type: 'delete' | 'block_toggle', domain: string, value: boolean }

const user = JSON.parse(localStorage.getItem('user') || '{}')
const isSuperAdmin = computed(() => user.role === 'admin' || user.isadmin)

const filteredInstitutes = computed(() => {
    if (!instSearchQuery.value) return institutes.value
    const q = instSearchQuery.value.toLowerCase()
    return institutes.value.filter(i => i.domain.toLowerCase().includes(q))
})

const trendChartData = computed(() => ({
    labels: trends.value.registrations.map(r => r.date),
    datasets: [
        {
            label: 'New Registrations',
            data: trends.value.registrations.map(r => r.count),
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            fill: true,
            tension: 0.4
        },
        {
            label: 'AI Usage',
            data: trends.value.ai_usage.map(a => a.count),
            borderColor: '#d946ef',
            backgroundColor: 'rgba(217, 70, 239, 0.1)',
            fill: true,
            tension: 0.4
        }
    ]
}))

const instituteChartData = computed(() => ({
    labels: institutes.value.slice(0, 7).map(i => i.domain),
    datasets: [
        {
            label: 'AI Actions',
            data: institutes.value.slice(0, 7).map(i => i.ai_usage),
            backgroundColor: '#3b82f6',
            borderRadius: 8
        }
    ]
}))

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: true, position: 'bottom' }
    },
    scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
        x: { grid: { display: false } }
    }
}

const fetchData = async () => {
    try {
        loading.value = true
        const [dRes, iRes, aRes, tRes] = await Promise.all([
            api.get('/admin/details'),
            api.get('/admin/institute-stats'),
            api.get('/admin/ai-usage-stats'),
            api.get('/admin/growth-trends')
        ])
        stats.value = dRes.data
        institutes.value = iRes.data.institutes
        topUsers.value = aRes.data.top_users
        trends.value = tRes.data
    } catch (err) {
        console.error("Failed to fetch admin stats:", err)
        error.value = `Failed to load specialized analytics: ${err.response?.data?.message || err.message}`
    } finally {
        loading.value = false
    }
}

const calculateActivity = (inst) => {
    const max = Math.max(...institutes.value.map(i => i.ai_usage), 1)
    return (inst.ai_usage / max) * 100
}

const scrollToUsers = (domain) => {
    externalUserSearch.value = domain
    document.querySelector('.management-section')?.scrollIntoView({ behavior: 'smooth' })
}

// Action Handlers
const initiateAction = (type, domain, value = null) => {
    pendingAction.value = { type, domain, value }
    modalStep.value = 1
    adminPassword.value = ''
    passwordError.value = ''
    showModal.value = true
}

const modalTitle = computed(() => {
    if (!pendingAction.value) return ''
    if (pendingAction.value.type === 'delete') return `Delete Institute: ${pendingAction.value.domain}`
    const action = pendingAction.value.value ? 'Block' : 'Unblock'
    return `${action} Institute: ${pendingAction.value.domain}`
})

const initialWarningText = computed(() => {
    if (!pendingAction.value) return ''
    if (pendingAction.value.type === 'delete') return `Are you sure you want to DELETE ${pendingAction.value.domain}? This cannot be undone.`
    const action = pendingAction.value.value ? 'BLOCK' : 'UNBLOCK'
    return `Are you sure you want to ${action} all users in ${pendingAction.value.domain}?`
})

const nextStep = () => {
    modalStep.value++
}

const closeModal = () => {
    showModal.value = false
    pendingAction.value = null
    // If it was a checkbox toggle attempt that got cancelled, we need to revert the UI state visually
    // Since UI is bound to 'inst.is_blocked', Vue should handle it, 
    // but the @change event already fired. Just refreshing data resets it to source truth.
    if (pendingAction.value?.type === 'block_toggle') {
        fetchData()
    }
}

const executeAction = async () => {
    if (!adminPassword.value) {
        passwordError.value = 'Password is required'
        return
    }

    verifying.value = true
    passwordError.value = ''

    try {
        // Verify Password first
        const verifyRes = await api.post('/auth/verify_password', { password: adminPassword.value })
        if (!verifyRes.data.verified) {
            throw new Error("Invalid admin password")
        }

        // Proceed with Action
        const { type, domain, value } = pendingAction.value

        if (type === 'delete') {
            await api.delete('/admin/delete-institute', { data: { domain } }) // axios delete body
            alert(`Institute ${domain} deleted successfully`)
        } else if (type === 'block_toggle') {
            if (value) {
                await api.post('/admin/block-institute', { domain })
                alert(`Blocked ${domain}`)
            } else {
                await api.post('/admin/unblock-institute', { domain })
                alert(`Unblocked ${domain}`)
            }
        }

        closeModal()
        fetchData() // Refresh list

    } catch (err) {
        console.error(err)
        passwordError.value = err.response?.data?.message || err.message || 'Verification failed'
    } finally {
        verifying.value = false
    }
}

const exportData = () => {
    const csv = institutes.value.map(i => `${i.domain},${i.user_count},${i.manager_count},${i.ai_usage}`).join('\n')
    const blob = new Blob([`Domain,Users,Managers,AI_Actions\n${csv}`], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.setAttribute('href', url)
    a.setAttribute('download', 'institute_stats.csv')
    a.click()
}

onMounted(fetchData)
</script>

<style scoped>
.admin-dashboard {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

.header {
    margin-bottom: 2.5rem;
}

.header h1 {
    font-size: 2.2rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(90deg, #fff, #999);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header p {
    color: var(--text-secondary);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2.5rem;
}

.stat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 1.5rem;
    border-radius: 20px;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    transition: transform 0.2s;
}

.stat-card:hover {
    transform: translateY(-4px);
}

.stat-icon {
    font-size: 2rem;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.05);
}

.stat-info h3 {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 0.2rem;
}

.stat-info .value {
    font-size: 1.8rem;
    font-weight: 800;
}

.charts-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 3rem;
}

.chart-container {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 1.5rem;
    border-radius: 24px;
}

.chart-container h3 {
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
    opacity: 0.8;
}

.chart-wrapper {
    height: 300px;
}

.data-section {
    margin-bottom: 3rem;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.title-group {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.inst-search {
    width: 250px;
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
}

.btn-icon {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}

.delete-btn:hover {
    background: #ef4444;
    color: white;
    border-color: #ef4444;
}

.export-btn {
    background: transparent;
    border: 1px solid var(--primary-color);
    color: var(--primary-color);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
}

.table-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 24px;
    overflow: hidden;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    text-align: left;
    padding: 1.25rem;
    background: rgba(255, 255, 255, 0.02);
    color: var(--text-secondary);
    font-size: 0.85rem;
    text-transform: uppercase;
}

td {
    padding: 1.25rem;
    border-top: 1px solid var(--border-color);
    vertical-align: middle;
}

.domain-badge {
    background: rgba(99, 102, 241, 0.1);
    color: #818cf8;
    padding: 0.4rem 0.8rem;
    border-radius: 8px;
    font-weight: 600;
    font-family: monospace;
}

/* Toggle Switch */
.toggle-switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 26px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #22c55e;
    /* Default unblocked (Green) */
    transition: .4s;
    border-radius: 34px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    /* Start right for unblocked */
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
    transform: translateX(24px);
    /* Default to unblocked position */
}

input:checked+.slider {
    background-color: #ef4444;
    /* Blocked (Red) */
}

input:checked+.slider:before {
    transform: translateX(0);
    /* Move left for blocked */
}

/* Top Users */
.top-users-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
}

.user-chip {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 1rem;
    border-radius: 16px;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.user-rank {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: var(--primary-color);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.user-meta .name {
    display: block;
    font-weight: 600;
}

.user-meta .email {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.loading-state,
.error-state {
    padding: 5rem;
    text-align: center;
}

.loader {
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1.5rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(5px);
}

.modal-content {
    background: #1e293b;
    padding: 2rem;
    border-radius: 16px;
    width: 90%;
    max-width: 500px;
    border: 1px solid var(--border-color);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.modal-header h2 {
    font-size: 1.5rem;
    color: #fff;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 1.5rem;
    cursor: pointer;
}

.warning-text {
    color: #e2e8f0;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

.warning-text.strong {
    color: #ef4444;
    font-weight: bold;
}

.sub-warning {
    color: #94a3b8;
    margin-bottom: 2rem;
    font-size: 0.95rem;
}

.password-input {
    width: 100%;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: white;
    margin-bottom: 1rem;
    font-size: 1rem;
}

.error-msg {
    color: #ef4444;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
}

.btn-secondary {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
}

.btn-danger {
    background: #ef4444;
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
}

.btn-primary {
    background: var(--primary-color);
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
}

.btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}
</style>
