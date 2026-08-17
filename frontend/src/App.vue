<template>
  <el-config-provider :locale="elementLocale">
    <!-- 方向契约锚点见 index.html body 首注释（split-flap concourse 车站翻牌时刻表） -->
    <div class="app-shell" :class="{ dark: isDarkTheme }">
      <!-- 车站网格暗纹 -->
      <div class="concourse-bg" aria-hidden="true" />

      <!-- 站厅顶栏：站名 + 线路 + 时钟 -->
      <header class="station-bar">
        <div class="station-bar__brand">
          <img src="/logo.png" alt="PromptWorks" class="station-bar__logo" />
          <div class="station-bar__name">
            <span class="station-bar__title">PromptWorks</span>
            <span class="station-bar__sub">{{ t('app.stationSubtitle') }}</span>
          </div>
        </div>
        <div class="station-bar__clock">
          <span class="station-clock" aria-hidden="true">{{ clockText }}</span>
          <span class="station-bar__clock-label">{{ t('app.stationClock') }}</span>
        </div>
      </header>

      <el-container class="app-container">
        <el-aside width="224px" class="side-nav">
          <div class="brand-row">
            <img src="/logo.png" alt="PromptWorks" class="brand-logo" />
            <div class="brand-copy">
              <span class="app-title">PromptWorks</span>
              <span class="app-subtitle">{{ t('app.stationSubtitle') }}</span>
            </div>
          </div>
          <div class="side-divider" />
          <el-menu class="side-menu" :default-active="activeMenu" @select="handleMenuSelect">
            <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
              <el-icon>
                <component :is="item.icon" />
              </el-icon>
              <span>{{ item.label }}</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="main-view">
          <div class="main-toolbar-space" aria-hidden="true" />
          <router-view />
        </el-main>
      </el-container>

      <div class="global-action-card" aria-label="全局操作">
        <el-dropdown
          trigger="click"
          @command="handleLanguageCommand"
        >
          <span
            class="global-action-trigger"
            :data-tooltip="t('app.language')"
            @pointerenter="showActionTooltip"
            @pointerleave="hideActionTooltip"
            @mouseover="showActionTooltip"
            @mouseleave="hideActionTooltip"
            @focusin="showActionTooltip"
            @focusout="hideActionTooltip"
          >
            <el-button
              :icon="Reading"
              circle
              text
              class="global-action-button"
              :title="t('app.language')"
              :aria-label="t('app.language')"
            />
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="zh-CN" :disabled="language === 'zh-CN'">
                {{ t('app.languageCn') }}
              </el-dropdown-item>
              <el-dropdown-item command="en-US" :disabled="language === 'en-US'">
                {{ t('app.languageEn') }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown
          trigger="click"
          @command="handleThemeCommand"
        >
          <span
            class="global-action-trigger"
            :data-tooltip="themeActionTooltip"
            @pointerenter="showActionTooltip"
            @pointerleave="hideActionTooltip"
            @mouseover="showActionTooltip"
            @mouseleave="hideActionTooltip"
            @focusin="showActionTooltip"
            @focusout="hideActionTooltip"
          >
            <el-button
              :icon="themeIcon"
              circle
              text
              class="global-action-button"
              :title="themeActionTooltip"
              :aria-label="themeActionTooltip"
            />
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="system" :disabled="themeMode === 'system'">
                <el-icon><Monitor /></el-icon>
                <span>{{ t('app.themeSystem') }}</span>
              </el-dropdown-item>
              <el-dropdown-item command="light" :disabled="themeMode === 'light'">
                <el-icon><Sunny /></el-icon>
                <span>{{ t('app.themeLight') }}</span>
              </el-dropdown-item>
              <el-dropdown-item command="dark" :disabled="themeMode === 'dark'">
                <el-icon><Moon /></el-icon>
                <span>{{ t('app.themeDark') }}</span>
              </el-dropdown-item>
              <li class="theme-color-panel" role="presentation">
                <div class="theme-color-panel__title">{{ t('app.themeColor') }}</div>
                <div class="theme-color-options" role="group" :aria-label="t('app.themeColor')">
                  <button
                    v-for="item in themeColorOptions"
                    :key="item.value"
                    type="button"
                    class="theme-color-option"
                    :class="{ 'is-active': themeColor === item.value }"
                    :style="{ '--theme-option-color': item.primary }"
                    :aria-label="t(item.labelKey)"
                    :aria-pressed="themeColor === item.value"
                    :title="t(item.labelKey)"
                    @click.stop="handleThemeColorSelect(item.value)"
                  />
                </div>
              </li>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-tooltip :content="t('app.settings')" placement="bottom">
          <el-button
            :icon="Setting"
            circle
            text
            class="global-action-button"
            :title="t('app.settings')"
            :aria-label="t('app.settings')"
            @click="handleOpenSettings"
          />
        </el-tooltip>
      </div>
    </div>

    <el-dialog
      v-model="settingsDialogVisible"
      :title="t('app.settingsDialogTitle')"
      width="460px"
      :close-on-click-modal="false"
      :destroy-on-close="true"
    >
      <el-skeleton v-if="settingsLoading" :rows="3" animated />
      <el-form
        v-else
        ref="settingsFormRef"
        :model="settingsForm"
        :rules="settingsRules"
        label-position="top"
        class="settings-form"
      >
        <el-form-item :label="t('app.settingsQuickTestTimeoutLabel')" prop="quickTestTimeout">
          <div class="settings-input-row">
            <el-input-number
              v-model="settingsForm.quickTestTimeout"
              :min="TIMEOUT_MIN"
              :max="TIMEOUT_MAX"
              :step="5"
              :precision="0"
              :disabled="settingsSaving"
              controls-position="right"
            />
            <span class="settings-input-unit">{{ t('app.settingsSecondsUnit') }}</span>
          </div>
        </el-form-item>
        <el-form-item :label="t('app.settingsTestTaskTimeoutLabel')" prop="testTaskTimeout">
          <div class="settings-input-row">
            <el-input-number
              v-model="settingsForm.testTaskTimeout"
              :min="TIMEOUT_MIN"
              :max="TIMEOUT_MAX"
              :step="5"
              :precision="0"
              :disabled="settingsSaving"
              controls-position="right"
            />
            <span class="settings-input-unit">{{ t('app.settingsSecondsUnit') }}</span>
          </div>
        </el-form-item>
        <el-form-item
          :label="t('app.settingsAiOptimizationTimeoutLabel')"
          prop="aiOptimizationTimeout"
        >
          <div class="settings-input-row">
            <el-input-number
              v-model="settingsForm.aiOptimizationTimeout"
              :min="TIMEOUT_MIN"
              :max="TIMEOUT_MAX"
              :step="30"
              :precision="0"
              :disabled="settingsSaving"
              controls-position="right"
            />
            <span class="settings-input-unit">{{ t('app.settingsSecondsUnit') }}</span>
          </div>
        </el-form-item>
        <p class="settings-hint">
          {{ t('app.settingsTimeoutHint', { min: TIMEOUT_MIN, max: TIMEOUT_MAX }) }}
        </p>
      </el-form>
      <template #footer>
        <el-button @click="handleSettingsCancel" :disabled="settingsSaving">
          {{ t('common.cancel') }}
        </el-button>
        <el-button type="primary" :loading="settingsSaving" @click="handleSettingsConfirm">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import type { Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Setting,
  Collection,
  MagicStick,
  Memo,
  Files,
  Tickets,
  Cpu,
  Histogram,
  InfoFilled,
  Sunny,
  Moon,
  Monitor,
  Reading
} from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import enUs from 'element-plus/es/locale/lang/en'
import { useI18n } from 'vue-i18n'
import { setLocale } from './i18n'
import type { SupportedLocale } from './i18n/messages'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { version as APP_VERSION } from '@/version.json'
import {
  useTestingSettings,
  DEFAULT_AI_OPTIMIZATION_TIMEOUT_SECONDS,
  DEFAULT_TIMEOUT_SECONDS
} from './composables/useTestingSettings'
import {
  checkProjectVersionOncePerDay,
  writeProjectVersionCheckCache
} from './utils/projectVersionCheck'

interface MenuItem {
  index: string
  label: string
  routeName: string
  icon: Component
}

const router = useRouter()
const route = useRoute()

const { t, locale } = useI18n()
const language = ref<SupportedLocale>(locale.value as SupportedLocale)
const elementLocale = computed(() => (language.value === 'zh-CN' ? zhCn : enUs))
type ThemeMode = 'system' | 'light' | 'dark'
type ThemeColor = 'amber' | 'blue' | 'green' | 'violet' | 'orange' | 'rose'
interface ThemeColorOption {
  value: ThemeColor
  labelKey: string
  primary: string
  dark2: string
  light3: string
  light5: string
  light7: string
  light8: string
  light9: string
}

const THEME_MODE_STORAGE_KEY = 'promptworks-theme-mode'
const THEME_COLOR_STORAGE_KEY = 'promptworks-theme-color'
const themeColorOptions: ThemeColorOption[] = [
  {
    value: 'amber',
    labelKey: 'app.themeColorAmber',
    primary: '#d9962f',
    dark2: '#b57f26',
    light3: '#e2a84a',
    light5: '#eabf77',
    light7: '#f0d5a8',
    light8: '#f5e4c8',
    light9: '#faf0de'
  },
  {
    value: 'blue',
    labelKey: 'app.themeColorBlue',
    primary: '#409eff',
    dark2: '#337ecc',
    light3: '#79bbff',
    light5: '#a0cfff',
    light7: '#c6e2ff',
    light8: '#d9ecff',
    light9: '#ecf5ff'
  },
  {
    value: 'green',
    labelKey: 'app.themeColorGreen',
    primary: '#10b981',
    dark2: '#0f8f69',
    light3: '#5ed0aa',
    light5: '#88dcc2',
    light7: '#b7ead8',
    light8: '#d1f3e8',
    light9: '#ecfdf5'
  },
  {
    value: 'violet',
    labelKey: 'app.themeColorViolet',
    primary: '#7c3aed',
    dark2: '#6429c7',
    light3: '#a377f3',
    light5: '#bd9bf6',
    light7: '#d7c4fa',
    light8: '#e8ddfd',
    light9: '#f3efff'
  },
  {
    value: 'orange',
    labelKey: 'app.themeColorOrange',
    primary: '#f97316',
    dark2: '#c75b12',
    light3: '#fb9d5c',
    light5: '#fdbc8a',
    light7: '#fed8b8',
    light8: '#fee8d5',
    light9: '#fff4eb'
  },
  {
    value: 'rose',
    labelKey: 'app.themeColorRose',
    primary: '#e11d48',
    dark2: '#b91c3f',
    light3: '#ea6380',
    light5: '#f099a9',
    light7: '#f5c2cc',
    light8: '#fadce3',
    light9: '#fff1f4'
  }
]

function readStoredThemeMode(): ThemeMode {
  if (typeof window === 'undefined') {
    return 'system'
  }
  const stored = window.localStorage.getItem(THEME_MODE_STORAGE_KEY)
  return stored === 'light' || stored === 'dark' || stored === 'system'
    ? stored
    : 'system'
}

function readStoredThemeColor(): ThemeColor {
  if (typeof window === 'undefined') {
    return 'amber'
  }
  const stored = window.localStorage.getItem(THEME_COLOR_STORAGE_KEY)
  return themeColorOptions.some((item) => item.value === stored)
    ? (stored as ThemeColor)
    : 'amber'
}

const themeMode = ref<ThemeMode>(readStoredThemeMode())
const themeColor = ref<ThemeColor>(readStoredThemeColor())

/* 站厅时钟（翻牌风格，HH:MM:SS） */
const clockText = ref('--:--:--')
let clockTimer: number | undefined
function tickClock() {
  const now = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  clockText.value = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}
onMounted(() => {
  tickClock()
  clockTimer = window.setInterval(tickClock, 1000)
})
onUnmounted(() => {
  if (clockTimer !== undefined) {
    window.clearInterval(clockTimer)
  }
})
const systemPrefersDark = ref(
  typeof window !== 'undefined'
    ? window.matchMedia('(prefers-color-scheme: dark)').matches
    : false
)
let colorSchemeQuery: MediaQueryList | null = null
function handleSystemThemeChange(event: MediaQueryListEvent) {
  systemPrefersDark.value = event.matches
}

const {
  quickTestTimeout,
  testTaskTimeout,
  aiOptimizationTimeout,
  fetchTimeouts,
  saveTimeouts
} = useTestingSettings()

const settingsDialogVisible = ref(false)
const settingsLoading = ref(false)
const settingsSaving = ref(false)
const settingsFormRef = ref<FormInstance>()
const settingsForm = reactive({
  quickTestTimeout: DEFAULT_TIMEOUT_SECONDS,
  testTaskTimeout: DEFAULT_TIMEOUT_SECONDS,
  aiOptimizationTimeout: DEFAULT_AI_OPTIMIZATION_TIMEOUT_SECONDS
})

const TIMEOUT_MIN = 1
const TIMEOUT_MAX = 600
function validateTimeout(
  _: unknown,
  value: number,
  callback: (error?: Error) => void
) {
  if (value == null || Number.isNaN(value)) {
    callback(new Error(t('app.settingsTimeoutRequired')))
    return
  }
  if (value < TIMEOUT_MIN || value > TIMEOUT_MAX) {
    callback(
      new Error(
        t('app.settingsTimeoutRange', { min: TIMEOUT_MIN, max: TIMEOUT_MAX })
      )
    )
    return
  }
  callback()
}

const settingsRules: FormRules = {
  quickTestTimeout: [
    {
      required: true,
      message: t('app.settingsTimeoutRequired'),
      trigger: 'blur'
    },
    {
      validator: validateTimeout,
      trigger: ['change', 'blur']
    }
  ],
  testTaskTimeout: [
    {
      required: true,
      message: t('app.settingsTimeoutRequired'),
      trigger: 'blur'
    },
    {
      validator: validateTimeout,
      trigger: ['change', 'blur']
    }
  ],
  aiOptimizationTimeout: [
    {
      required: true,
      message: t('app.settingsTimeoutRequired'),
      trigger: 'blur'
    },
    {
      validator: validateTimeout,
      trigger: ['change', 'blur']
    }
  ]
}

function syncSettingsFormFromRefs() {
  settingsForm.quickTestTimeout =
    quickTestTimeout.value ?? DEFAULT_TIMEOUT_SECONDS
  settingsForm.testTaskTimeout =
    testTaskTimeout.value ?? DEFAULT_TIMEOUT_SECONDS
  settingsForm.aiOptimizationTimeout =
    aiOptimizationTimeout.value ?? DEFAULT_AI_OPTIMIZATION_TIMEOUT_SECONDS
}

const menuItems = computed<MenuItem[]>(() => [
  { index: 'prompt', label: t('menu.prompt'), routeName: 'prompt-management', icon: Collection },
  { index: 'test-job', label: t('menu.testJob'), routeName: 'prompt-test-task-create', icon: Memo },
  { index: 'class', label: t('menu.class'), routeName: 'class-management', icon: Files },
  { index: 'tag', label: t('menu.tag'), routeName: 'tag-management', icon: Tickets },
  { index: 'llm', label: t('menu.llm'), routeName: 'llm-management', icon: Cpu },
  { index: 'usage', label: t('menu.usage'), routeName: 'usage-management', icon: Histogram },
  { index: 'project-info', label: t('menu.projectInfo'), routeName: 'project-info', icon: InfoFilled }
])

const activeMenu = computed(() => (route.meta.menu as string | undefined) ?? 'prompt')
const isDarkTheme = computed(() =>
  themeMode.value === 'system'
    ? systemPrefersDark.value
    : themeMode.value === 'dark'
)
const themeIcon = computed(() => {
  if (themeMode.value === 'system') {
    return Monitor
  }
  return isDarkTheme.value ? Moon : Sunny
})
const themeActionTooltip = computed(() => t('app.themeSwitch'))

watch(language, (value) => {
  setLocale(value)
})

watch(isDarkTheme, (value) => toggleTheme(value), { immediate: true })
watch(themeMode, (value) => {
  window.localStorage.setItem(THEME_MODE_STORAGE_KEY, value)
})
watch(themeColor, (value) => {
  applyThemeColor(value)
  window.localStorage.setItem(THEME_COLOR_STORAGE_KEY, value)
}, { immediate: true })

watch(
  () => [
    quickTestTimeout.value,
    testTaskTimeout.value,
    aiOptimizationTimeout.value
  ],
  () => {
    if (!settingsDialogVisible.value || settingsLoading.value) {
      return
    }
    syncSettingsFormFromRefs()
  }
)

watch(settingsDialogVisible, (visible) => {
  if (!visible) {
    settingsFormRef.value?.clearValidate()
  }
})

async function handleOpenSettings() {
  settingsDialogVisible.value = true
  settingsLoading.value = true
  try {
    await fetchTimeouts(true)
    syncSettingsFormFromRefs()
    await nextTick()
    settingsFormRef.value?.clearValidate()
  } catch (error) {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.warn('[settings] load failed', error)
    }
    ElMessage.error(t('app.settingsLoadFailed'))
    syncSettingsFormFromRefs()
  } finally {
    settingsLoading.value = false
  }
}

function handleSettingsCancel() {
  settingsDialogVisible.value = false
}

function handleLanguageCommand(command: string | number | object) {
  if (command === 'zh-CN' || command === 'en-US') {
    language.value = command
  }
}

function handleThemeCommand(command: string | number | object) {
  if (command === 'system' || command === 'light' || command === 'dark') {
    themeMode.value = command
  }
}

function handleThemeColorSelect(value: ThemeColor) {
  themeColor.value = value
}

function showActionTooltip(event: Event) {
  if (event.currentTarget instanceof HTMLElement) {
    event.currentTarget.classList.add('is-tooltip-visible')
  }
}

function hideActionTooltip(event: Event) {
  if (event.currentTarget instanceof HTMLElement) {
    event.currentTarget.classList.remove('is-tooltip-visible')
  }
}

async function handleSettingsConfirm() {
  if (settingsSaving.value) {
    return
  }
  const form = settingsFormRef.value
  if (!form) {
    return
  }

  try {
    await form.validate()
  } catch (error) {
    void error
    return
  }

  settingsSaving.value = true
  try {
    await saveTimeouts({
      quickTestTimeout: settingsForm.quickTestTimeout,
      testTaskTimeout: settingsForm.testTaskTimeout,
      aiOptimizationTimeout: settingsForm.aiOptimizationTimeout
    })
    ElMessage.success(t('app.settingsSaveSuccess'))
    settingsDialogVisible.value = false
  } catch (error) {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.error('[settings] save failed', error)
    }
    ElMessage.error(t('app.settingsSaveFailed'))
  } finally {
    settingsSaving.value = false
  }
}

function toggleTheme(value: boolean) {
  const root = document.documentElement
  if (value) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

function applyThemeColor(value: ThemeColor) {
  const option =
    themeColorOptions.find((item) => item.value === value) ?? themeColorOptions[0]
  const root = document.documentElement
  root.style.setProperty('--el-color-primary', option.primary)
  root.style.setProperty('--el-color-primary-dark-2', option.dark2)
  root.style.setProperty('--el-color-primary-light-3', option.light3)
  root.style.setProperty('--el-color-primary-light-5', option.light5)
  root.style.setProperty('--el-color-primary-light-7', option.light7)
  root.style.setProperty('--el-color-primary-light-8', option.light8)
  root.style.setProperty('--el-color-primary-light-9', option.light9)
}

function handleMenuSelect(index: string) {
  const target = menuItems.value.find((item) => item.index === index)
  if (target) {
    router.push({ name: target.routeName })
  }
}

onMounted(() => {
  colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)')
  systemPrefersDark.value = colorSchemeQuery.matches
  colorSchemeQuery.addEventListener('change', handleSystemThemeChange)

  checkProjectVersionOncePerDay().catch((error) => {
    if (import.meta.env.DEV) {
      console.warn('[project-version] daily check failed', error)
    }
    writeProjectVersionCheckCache({
      current: APP_VERSION,
      latest: null,
      has_update: false,
      check_status: 'failed',
      release_url: null,
      deployment_type: 'unknown',
      update_guidance: {
        deployment_type: 'unknown',
        title: '',
        steps: [],
        commands: []
      }
    })
  })
})

onUnmounted(() => {
  colorSchemeQuery?.removeEventListener('change', handleSystemThemeChange)
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--cyc-black);
  position: relative;
  z-index: 1;
}

/* ---- 站厅顶栏 ---- */
.station-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 40;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px 0 252px;
  background: #1a1815;
  border-bottom: 1px solid var(--board-line);
}

.station-bar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.station-bar__logo {
  width: 34px;
  height: 34px;
  object-fit: contain;
  border-radius: 4px;
}

.station-bar__name {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.station-bar__title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--flap-white);
}

.station-bar__sub {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--flap-faint);
  text-transform: uppercase;
}

.station-bar__clock {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.station-clock {
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--lamp-amber);
  letter-spacing: 0.06em;
}

.station-bar__clock-label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--flap-faint);
}

/* ---- 主体容器 ---- */
.app-container {
  min-height: 100vh;
  padding-left: 224px;
  padding-top: 56px;
}

/* ---- 侧边站牌导航 ---- */
.brand-row {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 76px;
  padding: 0 20px;
}

.brand-logo {
  width: 40px;
  height: 40px;
  flex: none;
  object-fit: contain;
  border-radius: 6px;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.app-title {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--flap-white);
}

.app-subtitle {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--flap-faint);
  margin-top: 2px;
}

.side-divider {
  height: 1px;
  margin: 0 16px 12px;
  background: var(--board-line);
}

.side-nav {
  position: fixed;
  inset: 56px auto 0 0;
  z-index: 30;
  width: 224px;
  height: calc(100vh - 56px);
  background: var(--board-black);
  border-right: 1px solid var(--board-line);
  overflow-y: auto;
  overflow-x: hidden;
}

.side-menu {
  border-right: none;
  background: transparent;
  padding: 4px 0;
}

.side-menu :deep(.el-menu-item) {
  height: 40px;
  margin: 3px 10px;
  border-radius: 4px;
  font-size: 13px;
  letter-spacing: 0.02em;
  transition: background 0.15s ease, color 0.15s ease;
}

.side-menu :deep(.el-menu-item.is-active) {
  background: var(--board-raised);
  color: var(--lamp-amber);
  font-weight: 600;
  border-left: 2px solid var(--lamp-amber);
}

.side-menu :deep(.el-menu-item:hover) {
  background: var(--board-raised);
  color: var(--flap-white);
}

.side-menu :deep(.el-menu-item:hover .el-icon),
.side-menu :deep(.el-menu-item.is-active .el-icon) {
  color: inherit;
}

.main-view {
  min-height: calc(100vh - 56px);
  padding: 24px 28px 32px;
  position: relative;
  z-index: 1;
}

.main-toolbar-space {
  height: 12px;
}

.global-action-card {
  position: fixed;
  top: 10px;
  right: 24px;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px;
  border: 1px solid var(--board-line);
  border-radius: 4px;
  background: #1a1815;
}

.global-action-button {
  width: 34px;
  height: 34px;
}

.global-action-trigger {
  position: relative;
  display: inline-flex;
  line-height: 1;
}

.global-action-trigger::after {
  position: absolute;
  top: calc(100% + 10px);
  left: 50%;
  z-index: 1000;
  padding: 6px 10px;
  border-radius: 4px;
  background: var(--el-text-color-primary);
  color: var(--el-bg-color);
  content: attr(data-tooltip);
  font-size: 12px;
  line-height: 1;
  opacity: 0;
  pointer-events: none;
  transform: translateX(-50%);
  transition: opacity 0.16s ease, transform 0.16s ease;
  white-space: nowrap;
}

.global-action-trigger:hover::after,
.global-action-trigger:focus-within::after,
.global-action-trigger.is-tooltip-visible::after {
  opacity: 1;
  transform: translateX(-50%) translateY(2px);
}

.theme-color-panel {
  margin: 4px 0 0;
  padding: 8px 12px 10px;
  border-top: 1px solid var(--el-border-color-lighter);
  list-style: none;
}

.theme-color-panel__title {
  margin-bottom: 8px;
  font-size: 12px;
  line-height: 1;
  color: var(--el-text-color-secondary);
}

.theme-color-options {
  display: grid;
  grid-template-columns: repeat(5, 24px);
  gap: 8px;
}

.theme-color-option {
  width: 24px;
  height: 24px;
  padding: 0;
  border: 2px solid transparent;
  border-radius: 50%;
  background: var(--theme-option-color);
  box-shadow: inset 0 0 0 1px rgb(255 255 255 / 58%);
  cursor: pointer;
}

.theme-color-option:hover,
.theme-color-option:focus-visible {
  border-color: var(--el-color-primary-light-5);
  outline: none;
}

.theme-color-option.is-active {
  border-color: var(--el-color-primary);
  box-shadow:
    0 0 0 2px var(--el-color-primary-light-8),
    inset 0 0 0 1px rgb(255 255 255 / 70%);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-input-unit {
  color: var(--el-text-color-secondary);
}

.settings-hint {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

@media (max-width: 768px) {
  .app-container {
    padding-left: 72px;
  }

  .station-bar {
    padding: 0 16px 0 84px;
  }

  .station-bar__clock-label,
  .station-bar__sub {
    display: none;
  }

  .station-clock {
    font-size: 16px;
  }

  .side-nav {
    width: 72px !important;
  }

  .brand-row {
    justify-content: center;
    padding: 0;
  }

  .app-title,
  .app-subtitle,
  .side-menu :deep(.el-menu-item span) {
    display: none;
  }

  .side-menu :deep(.el-menu-item) {
    justify-content: center;
    margin: 4px 8px;
    padding: 0;
  }

  .main-view {
    padding: 16px 16px 20px;
  }

  .main-toolbar-space {
    height: 8px;
  }

  .global-action-card {
    top: 8px;
    right: 12px;
  }
}
</style>
