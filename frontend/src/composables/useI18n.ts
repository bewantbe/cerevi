import { ref, computed } from 'vue'
import en from '@/locales/en.json'
import zh from '@/locales/zh.json'

type Locale = 'en' | 'zh'
type Messages = typeof en

const currentLocale = ref<Locale>('en')

const messages: Record<Locale, Messages> = {
  en,
  zh
}

export function useI18n() {
  const locale = computed(() => currentLocale.value)
  
  const setLocale = (newLocale: Locale) => {
    currentLocale.value = newLocale
    // Save to localStorage
    try {
      localStorage.setItem('visor-locale', newLocale)
    } catch (e) {
      console.warn('Failed to save locale to localStorage:', e)
    }
  }

  const t = (key: string): string => {
    const keys = key.split('.')
    let value: any = messages[currentLocale.value]
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        // Fallback to English if key not found
        value = messages.en
        for (const fallbackKey of keys) {
          if (value && typeof value === 'object' && fallbackKey in value) {
            value = value[fallbackKey]
          } else {
            return key // Return key itself if not found
          }
        }
        break
      }
    }
    
    return typeof value === 'string' ? value : key
  }

  // Initialize from localStorage
  const initializeLocale = () => {
    try {
      const saved = localStorage.getItem('visor-locale')
      if (saved && (saved === 'en' || saved === 'zh')) {
        currentLocale.value = saved
      }
    } catch (e) {
      console.warn('Failed to load locale from localStorage:', e)
    }
  }

  return {
    locale,
    setLocale,
    t,
    initializeLocale
  }
}

// Global instance
const globalI18n = useI18n()
globalI18n.initializeLocale()

export default globalI18n
