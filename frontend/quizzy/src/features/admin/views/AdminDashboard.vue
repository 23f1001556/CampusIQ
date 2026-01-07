<template>
    <div class="admin-dashboard">
        <div class="header">
            <h1>Admin Dashboard</h1>
            <p>Overview of application statistics</p>
        </div>

        <div v-if="loading" class="loading">Loading stats...</div>
        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else class="stats-grid">
            <div class="stat-card">
                <div class="icon-wrapper user-icon">
                    <span>👥</span>
                </div>
                <div class="stat-content">
                    <h3>Total Users</h3>
                    <p class="stat-value">{{ stats.user_count }}</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="icon-wrapper subject-icon">
                    <span>📚</span>
                </div>
                <div class="stat-content">
                    <h3>Total Subjects</h3>
                    <p class="stat-value">{{ stats.subject_count }}</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="icon-wrapper quiz-icon">
                    <span>🎯</span>
                </div>
                <div class="stat-content">
                    <h3>Total Quizzes</h3>
                    <p class="stat-value">{{ stats.quiz_count }}</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="icon-wrapper question-icon">
                    <span>❓</span>
                </div>
                <div class="stat-content">
                    <h3>Total Questions</h3>
                    <p class="stat-value">{{ stats.question_count }}</p>
                </div>
            </div>
        </div>

        <div v-if="!loading && chartData.labels.length" class="chart-section">
            <div class="chart-card">
                <Bar :data="chartData" :options="chartOptions" />
            </div>
        </div>

        <!-- User Management -->
        <UserManagement />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import UserManagement from '../components/UserManagement.vue';
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const stats = ref({
    user_count: 0,
    subject_count: 0,
    quiz_count: 0,
    question_count: 0
});
const loading = ref(true);
const error = ref(null);

const chartData = ref({
    labels: [],
    datasets: []
})

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false },
        title: {
            display: true,
            text: 'Recent Quiz Output (Latest 30 Attempts)',
            font: { size: 16 }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            title: { display: true, text: 'Score' }
        }
    }
}

const fetchStats = async () => {
    try {
        const response = await api.get('/admin/details');
        stats.value = response.data;

        const resChart = await api.get('/admin/attempts_stats');
        const attempts = resChart.data.attempts;

        // Prepare Chart Data
        // X-Axis: "User - QuizName (Date)"
        // Y-Axis: Score

        const labels = attempts.map(a => `${a.user} - ${a.quiz}`)
        const data = attempts.map(a => a.score)
        const bgColors = attempts.map(a => a.type === 'Mock' ? 'rgba(79, 70, 229, 0.6)' : 'rgba(34, 197, 94, 0.6)')

        chartData.value = {
            labels: labels,
            datasets: [{
                label: 'Score',
                backgroundColor: bgColors,
                data: data,
                borderRadius: 4
            }]
        }

    } catch (err) {
        console.error("Failed to fetch admin stats:", err);
        error.value = "Failed to load statistics. Are you an admin?";
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchStats();
});
</script>

<style scoped>
.admin-dashboard {
    padding: 1rem;
}

.header {
    margin-bottom: 2rem;
}

.header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.header p {
    color: var(--text-secondary);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.stat-card {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 1.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.icon-wrapper {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
}

.user-icon {
    background: rgba(99, 102, 241, 0.1);
    color: #6366f1;
}

.subject-icon {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
}

.quiz-icon {
    background: rgba(234, 179, 8, 0.1);
    color: #eab308;
}

.question-icon {
    background: rgba(236, 72, 153, 0.1);
    color: #ec4899;
}

.stat-content h3 {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
    font-weight: 500;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
}

.loading,
.error {
    padding: 2rem;
    text-align: center;
    color: var(--text-secondary);
}

.error {
    color: var(--danger-color);
}

.admin-actions h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
}

.actions-grid {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.action-btn {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-secondary);
    color: var(--text-secondary);
    cursor: pointer;
    font-weight: 500;
}

.action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.chart-section {
    margin-bottom: 3rem;
}

.chart-card {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid var(--border-color);
    height: 400px;
}
</style>
