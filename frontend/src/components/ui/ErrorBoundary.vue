<template>
  <div class="error-boundary">
    <div v-if="error" class="error-container">
      <div class="error-icon">
        <el-icon :size="48">
          <Warning />
        </el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">{{ error.message || 'An error occurred' }}</h3>
        <p v-if="error.details" class="error-details">{{ error.details }}</p>
        <div class="error-actions">
          <el-button type="primary" @click="retry" :loading="retrying">
            {{ $t('app.retry') }}
          </el-button>
          <el-button @click="reset">
            {{ $t('app.close') }}
          </el-button>
        </div>
        <div v-if="showDetails" class="error-stack">
          <el-collapse>
            <el-collapse-item title="Technical Details" name="stack">
              <pre>{{ errorStack }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
        <div class="error-toggle">
          <el-button text @click="showDetails = !showDetails">
            {{ showDetails ? 'Hide' : 'Show' }} Technical Details
          </el-button>
        </div>
      </div>
    </div>
    <div v-else>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { ElButton, ElIcon, ElCollapse, ElCollapseItem } from 'element-plus'
import { Warning } from '@element-plus/icons-vue'
import type { ViewerError } from '@/types'

interface Props {
  fallback?: string
  showStack?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  fallback: 'Something went wrong',
  showStack: false
})

const emit = defineEmits<{
  error: [error: ViewerError]
  retry: []
}>()

const error = ref<ViewerError | null>(null)
const errorStack = ref<string>('')
const showDetails = ref(props.showStack)
const retrying = ref(false)

onErrorCaptured((err: Error) => {
  console.error('Error captured by ErrorBoundary:', err)
  
  const viewerError: ViewerError = {
    type: 'unknown',
    message: err.message || props.fallback,
    details: err.cause?.toString(),
    timestamp: new Date(),
    recoverable: true
  }
  
  error.value = viewerError
  errorStack.value = err.stack || 'No stack trace available'
  
  emit('error', viewerError)
  
  // Prevent the error from propagating further
  return false
})

const retry = async () => {
  retrying.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500)) // Small delay for UX
    error.value = null
    errorStack.value = ''
    emit('retry')
  } finally {
    retrying.value = false
  }
}

const reset = () => {
  error.value = null
  errorStack.value = ''
  showDetails.value = props.showStack
}

// Expose methods for parent components
defineExpose({
  setError: (err: ViewerError) => {
    error.value = err
  },
  clearError: reset,
  hasError: () => !!error.value
})
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  min-height: 300px;
  text-align: center;
}

.error-icon {
  color: #f56c6c;
  margin-bottom: 20px;
}

.error-content {
  max-width: 500px;
}

.error-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 12px 0;
}

.error-details {
  font-size: 14px;
  color: #606266;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 20px;
}

.error-stack {
  margin: 20px 0;
  text-align: left;
}

.error-stack pre {
  font-size: 12px;
  color: #909399;
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 200px;
  margin: 0;
}

.error-toggle {
  margin-top: 12px;
}

:deep(.el-collapse-item__header) {
  font-size: 13px;
  color: #909399;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}
</style>
