<script setup>
import { ref, computed } from 'vue'
import PerformanceAnalysis from './PerformanceAnalysis.vue'
import QuestionGenerator from './QuestionGenerator.vue'
import AIHistory from './AIHistory.vue'

const currentTab = ref('generator') // Default to generator as it's the main feature
const prefilledTopic = ref('')

const tabs = [
    { 
        id: 'generator', 
        label: 'Question Generator', 
        icon: '⚡',
        desc: 'Create custom quizzes from any topic'
    },
    { 
        id: 'analysis', 
        label: 'Performance Analysis', 
        icon: '📊',
        desc: 'Deep dive into your strengths & weaknesses'
    },
    { 
        id: 'history', 
        label: 'Generation History', 
        icon: '📜',
        desc: 'Review past AI-generated content'
    }
]

const handlePractice = (topic) => {
    prefilledTopic.value = topic
    currentTab.value = 'generator'
}

const activeComponent = computed(() => {
    switch (currentTab.value) {
        case 'analysis': return PerformanceAnalysis
        case 'generator': return QuestionGenerator
        case 'history': return AIHistory
        default: return QuestionGenerator
    }
})
</script>

<template>
    <div class="ai-hub-container">
        <!-- Hero Header -->
        <div class="hub-header">
            <div class="header-content">
                <div class="icon-wrapper">
                    <span class="pulse-ring"></span>
                    <span class="ai-icon">✨</span>
                </div>
                <div>
                    <h1>AI Learning Hub</h1>
                    <p>Generate personalized quizzes, analyze your performance, and track your AI interaction history.</p>
                </div>
            </div>
        </div>

        <!-- Modern Tabs -->
        <div class="hub-tabs">
            <button v-for="tab in tabs" :key="tab.id" class="tab-card" :class="{ active: currentTab === tab.id }"
                @click="currentTab = tab.id">
                <div class="tab-icon">{{ tab.icon }}</div>
                <div class="tab-info">
                    <span class="tab-label">{{ tab.label }}</span>
                    <span class="tab-desc">{{ tab.desc }}</span>
                </div>
                <div class="active-indicator" v-if="currentTab === tab.id"></div>
            </button>
        </div>

        <!-- Content Area -->
        <div class="hub-content">
            <component :is="activeComponent" 
                :initial-topic="prefilledTopic"
                @practice-concept="handlePractice" />
        </div>
    </div>
</template>

<style scoped>
.ai-hub-container {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

/* Header */
.hub-header {
    background: linear-gradient(135deg, #4f46e5, #818cf8);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.15);
}

.header-content {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.icon-wrapper {
    position: relative;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    backdrop-filter: blur(10px);
}

.ai-icon {
    font-size: 2rem;
}

.hub-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    margin: 0 0 0.25rem 0;
    letter-spacing: -0.5px;
}

.hub-header p {
    font-size: 0.95rem;
    opacity: 0.9;
    max-width: 600px;
    line-height: 1.4;
}

/* Tabs */
.hub-tabs {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-bottom: 2.5rem;
}

.tab-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 1.5rem;
    border-radius: 16px;
    text-align: left;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 1rem;
    position: relative;
    overflow: hidden;
}

.tab-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.06);
    border-color: var(--primary-color);
}

.tab-card.active {
    background: var(--bg-secondary);
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px var(--primary-color);
}

.tab-icon {
    font-size: 2rem;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-accent);
    border-radius: 12px;
}

.active .tab-icon {
    background: rgba(79, 70, 229, 0.1);
}

.tab-info {
    flex: 1;
}

.tab-label {
    display: block;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.active .tab-label {
    color: var(--primary-color);
}

.tab-desc {
    display: block;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* Content */
.hub-content {
    background: var(--bg-secondary);
    border-radius: 20px;
    border: 1px solid var(--border-color);
    padding: 2rem;
    min-height: 400px;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
    .hub-tabs {
        grid-template-columns: 1fr;
    }
    
    .header-content {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }
}
</style>
