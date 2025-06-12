<template>
  <div id="app">
    <Header />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import Header from './components/layout/Header.vue'
import { useVISoRStore } from './stores/visor'

const visorStore = useVISoRStore()

onMounted(() => {
  // Initialize the application
  visorStore.initialize()
})
</script>

<style>
/* Global styles */
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  overflow-y: auto;
}

/* Reset some default styles */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  overflow-y: auto;
}

html {
  height: 100vh;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Loading states */
.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

/* Error states */
.error-message {
  color: #f56c6c;
  text-align: center;
  padding: 20px;
}

/* Utility classes */
.text-center {
  text-align: center;
}

.full-height {
  height: 100%;
}

.flex {
  display: flex;
}

.flex-1 {
  flex: 1;
}

.relative {
  position: relative;
}

.absolute {
  position: absolute;
}

.hidden {
  display: none;
}

/* Responsive design helpers */
@media (max-width: 768px) {
  .mobile-hidden {
    display: none !important;
  }
}

@media (min-width: 769px) {
  .desktop-hidden {
    display: none !important;
  }
}
</style>
