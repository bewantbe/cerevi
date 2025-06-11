<template>
  <el-dropdown @command="changeLanguage" trigger="click">
    <el-button text>
      <el-icon><Document /></el-icon>
      {{ currentLanguageLabel }}
      <el-icon class="el-icon--right"><ArrowDown /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="en" :disabled="currentLanguage === 'en'">
          English
        </el-dropdown-item>
        <el-dropdown-item command="zh" :disabled="currentLanguage === 'zh'">
          中文
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElDropdown, ElDropdownMenu, ElDropdownItem, ElButton, ElIcon } from 'element-plus'
import { Document, ArrowDown } from '@element-plus/icons-vue'

const emit = defineEmits<{
  change: [language: string]
}>()

const props = defineProps<{
  currentLanguage: string
}>()

const currentLanguageLabel = computed(() => {
  return props.currentLanguage === 'zh' ? '中文' : 'English'
})

const changeLanguage = (command: string) => {
  if (command !== props.currentLanguage) {
    emit('change', command)
  }
}
</script>

<style scoped>
.el-icon--right {
  margin-left: 4px;
}
</style>
