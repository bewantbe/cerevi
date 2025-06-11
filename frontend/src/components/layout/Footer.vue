<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-info">
        <div class="footer-section">
          <h4>VISoR Platform</h4>
          <p>Volumetric Imaging with Synchronized on-the-fly-scan and Readout</p>
          <p class="version">Version {{ version }}</p>
        </div>
        
        <div class="footer-section">
          <h4>Technology</h4>
          <ul class="tech-list">
            <li>High-resolution brain imaging</li>
            <li>Multi-channel fluorescence</li>
            <li>3D reconstruction</li>
            <li>Real-time visualization</li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h4>Data</h4>
          <ul class="data-list">
            <li>{{ totalSpecimens }} specimen{{ totalSpecimens !== 1 ? 's' : '' }}</li>
            <li>{{ totalRegions }} brain regions</li>
            <li>Multi-resolution pyramids</li>
            <li>Interactive 3D models</li>
          </ul>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="copyright">
          <p>&copy; {{ currentYear }} VISoR Platform. All rights reserved.</p>
        </div>
        
        <div class="footer-links">
          <router-link to="/about" class="footer-link">About</router-link>
          <a href="#" class="footer-link" @click.prevent="showHelp">Help</a>
          <a href="#" class="footer-link" @click.prevent="showContact">Contact</a>
        </div>
        
        <div class="footer-status">
          <div class="status-indicator" :class="{ online: isOnline, offline: !isOnline }">
            <el-icon class="status-icon">
              <CircleCheckFilled v-if="isOnline" />
              <CircleCloseFilled v-else />
            </el-icon>
            <span class="status-text">{{ isOnline ? 'Online' : 'Offline' }}</span>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useVISoRStore } from '@/stores/visor'
import VISoRAPI from '@/services/api'
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const visorStore = useVISoRStore()

// Local state
const isOnline = ref(true)
const version = ref('1.0.0')
const healthCheckInterval = ref<number | null>(null)

// Computed
const currentYear = computed(() => new Date().getFullYear())

const totalSpecimens = computed(() => visorStore.specimens.length)

const totalRegions = computed(() => visorStore.regions.length || 241) // Fallback to known count

// Methods
async function checkHealth() {
  try {
    const health = await VISoRAPI.healthCheck()
    isOnline.value = true
    if (health.version) {
      version.value = health.version
    }
  } catch (error) {
    isOnline.value = false
    console.warn('Health check failed:', error)
  }
}

function showHelp() {
  ElMessage.info('Help documentation coming soon!')
}

function showContact() {
  ElMessage.info('Contact information coming soon!')
}

function startHealthCheck() {
  // Initial check
  checkHealth()
  
  // Periodic checks every 60 seconds
  healthCheckInterval.value = window.setInterval(checkHealth, 60000)
}

function stopHealthCheck() {
  if (healthCheckInterval.value) {
    clearInterval(healthCheckInterval.value)
    healthCheckInterval.value = null
  }
}

// Lifecycle
onMounted(() => {
  startHealthCheck()
})

onUnmounted(() => {
  stopHealthCheck()
})
</script>

<style scoped>
.app-footer {
  background: #303133;
  color: #e4e7ed;
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px 20px;
}

.footer-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.footer-section h4 {
  color: #409eff;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
}

.footer-section p {
  margin: 0 0 8px 0;
  line-height: 1.5;
  color: #c0c4cc;
}

.version {
  font-size: 12px;
  color: #909399;
}

.tech-list,
.data-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tech-list li,
.data-list li {
  margin-bottom: 8px;
  color: #c0c4cc;
  position: relative;
  padding-left: 16px;
}

.tech-list li:before,
.data-list li:before {
  content: '•';
  color: #409eff;
  position: absolute;
  left: 0;
}

.footer-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid #434343;
  flex-wrap: wrap;
  gap: 16px;
}

.copyright p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-link {
  color: #c0c4cc;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.footer-link:hover {
  color: #409eff;
}

.footer-status {
  display: flex;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  transition: all 0.3s;
}

.status-indicator.online {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.status-indicator.offline {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.status-icon {
  font-size: 12px;
}

.status-text {
  font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
  .footer-content {
    padding: 30px 16px 16px;
  }

  .footer-info {
    grid-template-columns: 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }

  .footer-bottom {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .footer-links {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .footer-info {
    grid-template-columns: 1fr;
  }

  .footer-section {
    text-align: center;
  }

  .footer-links {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
