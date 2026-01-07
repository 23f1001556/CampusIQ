<template>
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1>Forgot Password</h1>
                <p>Enter your email to receive reset instructions</p>
            </div>

            <form @submit.prevent="handleReset" class="auth-form">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" v-model="email" placeholder="name@example.com" required />
                </div>

                <button type="submit" class="btn-primary" :disabled="isLoading">
                    <span v-if="isLoading">Sending...</span>
                    <span v-else>Send Reset Link</span>
                </button>

                <div v-if="message" :class="[status === 'success' ? 'success-message' : 'error-message']">
                    {{ message }}
                </div>
            </form>

            <div class="auth-footer">
                <p>Remember your password? <router-link to="/login">Sign in</router-link></p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const email = ref('')
const isLoading = ref(false)
const message = ref('')
const status = ref('')

const handleReset = async () => {
    // Backend API not yet implemented for this
    isLoading.value = true
    message.value = ''

    // Simulate API call for now or call real endpoint if exists
    try {
        // await api.post('/auth/forgot_password', { email: email.value })

        // Mock success for UI demo
        setTimeout(() => {
            status.value = 'success'
            message.value = 'If an account exists, a reset link has been sent.'
            isLoading.value = false
        }, 1500)

    } catch (err) {
        status.value = 'error'
        message.value = 'Failed to process request.'
        isLoading.value = false
    }
}
</script>

<style scoped>
/* Reuse existing auth styles */
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
    max-width: 420px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.auth-header {
    text-align: center;
    margin-bottom: 2.5rem;
}

.auth-header h1 {
    color: #fff;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
}

.auth-header p {
    color: #94a3b8;
    font-size: 1rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    color: #e2e8f0;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
}

.form-group input {
    width: 100%;
    padding: 0.875rem 1rem;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: #fff;
    font-size: 1rem;
}

.btn-primary {
    width: 100%;
    padding: 0.875rem;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    border: none;
    border-radius: 12px;
    color: #fff;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary:hover {
    transform: translateY(-1px);
}

.error-message {
    margin-top: 1rem;
    padding: 0.75rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: 8px;
    color: #f87171;
    text-align: center;
}

.success-message {
    margin-top: 1rem;
    padding: 0.75rem;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: 8px;
    color: #4ade80;
    text-align: center;
}

.auth-footer {
    margin-top: 2rem;
    text-align: center;
    color: #94a3b8;
}

.auth-footer a {
    color: #6366f1;
    text-decoration: none;
    font-weight: 600;
}
</style>
