<script setup>
import { useTheme } from './composables/useTheme'
// Initialize theme globally
useTheme()
</script>

<template>
  <router-view></router-view>
</template>

<style>
/* Global resets if needed, but style.css usually handles it */
body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
