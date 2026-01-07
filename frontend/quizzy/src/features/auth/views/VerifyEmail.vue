<template>
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1>Email Verification</h1>
            </div>

            <div class="message-content">
                <div v-if="isLoading" class="loading">
                    <div class="spinner"></div>
                    <p>Verifying your email...</p>
                </div>

                <div v-else-if="status === 'success'" class="success">
                    <div class="icon">✅</div>
                    <h2>Verified!</h2>
                    <p>{{ message }}</p>
                    <button @click="goToLogin" class="btn-primary">Go to Login</button>
                </div>

                <div v-else-if="status === 'error'" class="error">
                    <div class="icon">❌</div>
                    <h2>Verification Failed</h2>
                    <p>{{ message }}</p>
                    <button @click="goToLogin" class="btn-secondary">Back to Login</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const isLoading = ref(true)
const status = ref('') // 'success' or 'error'
const message = ref('')

onMounted(async () => {
    const token = route.params.token

    if (!token) {
        status.value = 'error'
        message.value = 'No token provided.'
        isLoading.value = false
        return
    }

    try {
        const response = await api.get(`/auth/verify_email/${token}`)
        status.value = 'success'
        message.value = response.data.message || 'Email verified successfully.'
    } catch (err) {
        status.value = 'error'
        message.value = err.response?.data?.message || 'Verification failed. Token may be invalid or expired.'
    } finally {
        isLoading.value = false
    }
})

const goToLogin = () => {
    router.push('/login')
}
</script>

<style scoped>
.auth-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-primary);
    padding: 2rem;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

.auth-card {
    width: 100%;
    max-width: 400px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    text-align: center;
}

.auth-header h1 {
    color: #fff;
    font-size: 1.5rem;
    margin-bottom: 2rem;
}

.message-content {
    color: #e2e8f0;
}

.icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

h2 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
    color: #fff;
}

p {
    color: #94a3b8;
    margin-bottom: 2rem;
}

.btn-primary {
    width: 100%;
    padding: 0.875rem;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    border: none;
    border-radius: 12px;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.btn-secondary {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #fff;
    width: 100%;
    padding: 0.875rem;
    border-radius: 12px;
    cursor: pointer;
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.05);
}

/* Spinner */
.spinner {
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top: 3px solid #6366f1;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
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
