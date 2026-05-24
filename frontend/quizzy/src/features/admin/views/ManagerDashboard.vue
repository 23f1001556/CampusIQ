<template>
    <div class="admin-dashboard">
        <div class="header">
            <h1>Institute Analytics</h1>
            <p>Performance metrics for your institution</p>
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
                    <div class="stat-icon user"></div>
                    <div class="stat-info">
                        <h3>Institute Users</h3>
                        <p class="value">{{ stats.user_count }}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon manager">👔</div>
                    <div class="stat-info">
                        <h3>Managers</h3>
                        <p class="value">{{ stats.manager_count }}</p>
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
                    <h3>Top 10 Active Users (AI Adoption)</h3>
                    <div class="top-users-list">
                        <div v-for="user in topUsers" :key="user.email" class="user-chip">
                            <div class="user-rank">{{ user.count }}</div>
                            <div class="user-meta">
                                <span class="name">{{ user.username }}</span>
                                <span class="email">{{ user.email }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- User Management Component -->
            <div class="management-section">
                <UserManagement />
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import UserManagement from '../components/UserManagement.vue'
import { Line } from 'vue-chartjs'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Filler
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

const loading = ref(true)
const error = ref(null)
const stats = ref({})
const topUsers = ref([])
const trends = ref({ registrations: [], ai_usage: [] })

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
        const [dRes, aRes, tRes] = await Promise.all([
            api.get('/admin/details'),
            api.get('/admin/ai-usage-stats'),
            api.get('/admin/growth-trends')
        ])
        stats.value = dRes.data
        topUsers.value = aRes.data.top_users
        trends.value = tRes.data
    } catch (err) {
        console.error("Failed to fetch manager stats:", err)
        error.value = `Failed to load analytics: ${err.response?.data?.message || err.message}`
    } finally {
        loading.value = false
    }
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

.top-users-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    max-height: 300px;
    overflow-y: auto;
}

.user-chip {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    padding: 0.75rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.user-rank {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: var(--primary-color);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.9rem;
}

.user-meta .name {
    display: block;
    font-weight: 600;
    font-size: 0.9rem;
}

.user-meta .email {
    font-size: 0.75rem;
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
</style>
