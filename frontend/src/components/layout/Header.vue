<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Logo and title -->
      <div class="header-left">
        <router-link to="/" class="logo-section">
          <el-icon class="logo-icon" size="28">
            <View />
          </el-icon>
          <h1 class="app-title">VISoR Platform</h1>
        </router-link>
      </div>

      <!-- Navigation -->
      <nav class="header-nav">
        <el-menu
          mode="horizontal"
          :default-active="currentRoute"
          class="nav-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>Home</span>
          </el-menu-item>
          <el-menu-item index="/about">
            <el-icon><InfoFilled /></el-icon>
            <span>About</span>
          </el-menu-item>
        </el-menu>
      </nav>

      <!-- Controls and status -->
      <div class="header-right">
        <!-- Specimen selector -->
        <div v-if="visorStore.specimens.length > 0" class="specimen-selector">
          <el-select
            :model-value="visorStore.currentSpecimen?.id"
            placeholder="Select specimen"
            size="small"
            style="width: 200px"
            @change="handleSpecimenChange"
          >
            <el-option
              v-for="specimen in visorStore.specimens"
              :key="specimen.id"
              :label="specimen.name"
              :value="specimen.id"
            >
              <div class="specimen-option">
                <span class="specimen-name">{{ specimen.name }}</span>
                <span class="specimen-species">{{ specimen.species }}</span>
              </div>
            </el-option>
          </el-select>
        </div>

        <!-- Language toggle -->
        <el-button-group size="small" class="language-toggle">
          <el-button :type="currentLanguage === 'en' ? 'primary' : 'default'" @click="setLanguage('en')">
            EN
          </el-button>
          <el-button :type="currentLanguage === 'zh' ? 'primary' : 'default'" @click="setLanguage('zh')">
            中文
          </el-button>
        </el-button-group>

        <!-- Loading indicator -->
        <div v-if="visorStore.loading" class="loading-indicator">
          <el-icon class="is-loading">
            <Loading />
          </el-icon>
        </div>

        <!-- Error indicator -->
        <el-popover
          v-if="visorStore.error"
          placement="bottom"
          trigger="click"
          width="300"
        >
          <template #reference>
            <el-button type="danger" size="small" :icon="WarningFilled" circle />
          </template>
          <div class="error-popup">
            <h4>Error</h4>
            <p>{{ visorStore.error }}</p>
            <el-button size="small" @click="visorStore.clearError">
              Dismiss
            </el-button>
          </div>
        </el-popover>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useVISoRStore } from '@/stores/visor'
import {
  View,
  House,
  InfoFilled,
  Loading,
  WarningFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const visorStore = useVISoRStore()

// Local state
const currentLanguage = ref('en')

// Computed
const currentRoute = computed(() => {
  return route.path
})

// Methods
function handleMenuSelect(index: string) {
  if (index !== route.path) {
    router.push(index)
  }
}

async function handleSpecimenChange(specimenId: string) {
  if (specimenId && specimenId !== visorStore.currentSpecimen?.id) {
    // Navigate to viewer if not already there
    if (route.name !== 'atlas-viewer') {
      await router.push(`/viewer/${specimenId}`)
    } else {
      // Update current specimen
      await visorStore.setCurrentSpecimen(specimenId)
    }
  }
}

function setLanguage(lang: 'en' | 'zh') {
  currentLanguage.value = lang
  // TODO: Implement i18n language switching
  console.log('Language changed to:', lang)
}
</script>

<style scoped>
.app-header {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
  gap: 12px;
}

.logo-icon {
  color: #409eff;
}

.app-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu {
  border-bottom: none;
  background: transparent;
}

.nav-menu .el-menu-item {
  height: 60px;
  line-height: 60px;
  border-bottom: 2px solid transparent;
}

.nav-menu .el-menu-item:hover,
.nav-menu .el-menu-item.is-active {
  color: #409eff;
  border-bottom-color: #409eff;
  background: transparent;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.specimen-selector {
  min-width: 200px;
}

.specimen-option {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.specimen-name {
  font-weight: 500;
  color: #303133;
}

.specimen-species {
  font-size: 12px;
  color: #909399;
}

.language-toggle {
  /* Styling handled by Element Plus */
}

.loading-indicator {
  display: flex;
  align-items: center;
  color: #409eff;
}

.error-popup h4 {
  margin: 0 0 8px 0;
  color: #f56c6c;
}

.error-popup p {
  margin: 0 0 16px 0;
  color: #606266;
  line-height: 1.4;
}

/* Responsive design */
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
    height: auto;
    flex-direction: column;
    gap: 12px;
    padding-top: 12px;
    padding-bottom: 12px;
  }

  .header-nav {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .header-right {
    order: 2;
    justify-content: space-between;
    width: 100%;
  }

  .app-title {
    font-size: 20px;
  }

  .specimen-selector {
    min-width: 150px;
  }
}

@media (max-width: 480px) {
  .app-title {
    display: none;
  }

  .header-right {
    flex-direction: column;
    gap: 8px;
  }

  .specimen-selector {
    width: 100%;
    min-width: auto;
  }
}
</style>
