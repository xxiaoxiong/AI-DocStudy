<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-loading="loading" class="progress-container">
      <!-- 进度条 -->
      <div class="progress-section">
        <el-progress
          :percentage="progress?.progress || 0"
          :status="getProgressStatus()"
          :stroke-width="20"
        >
          <template #default="{ percentage }">
            <span class="percentage-text">{{ percentage }}%</span>
          </template>
        </el-progress>
        
        <div class="current-step">
          <el-icon class="step-icon" :class="{ 'is-loading': isProcessing }">
            <Loading v-if="isProcessing" />
            <Check v-else-if="isCompleted" />
            <Close v-else-if="isFailed" />
            <Clock v-else />
          </el-icon>
          <span class="step-text">{{ progress?.current_step || '准备中...' }}</span>
        </div>

        <div class="steps-info">
          <span>已完成 {{ progress?.completed_steps || 0 }} / {{ progress?.total_steps || 6 }} 步</span>
        </div>
      </div>

      <!-- 统计信息 -->
      <div v-if="progress && hasStatistics" class="statistics-section">
        <el-divider content-position="left">
          <el-icon><DataAnalysis /></el-icon>
          处理统计
        </el-divider>
        
        <el-row :gutter="16">
          <el-col :span="12" v-if="progress.parsed_text_length">
            <el-statistic title="解析文本" :value="progress.parsed_text_length" suffix="字" />
          </el-col>
          <el-col :span="12" v-if="progress.sections_count">
            <el-statistic title="章节数量" :value="progress.sections_count" suffix="个" />
          </el-col>
          <el-col :span="12" v-if="progress.chunks_count">
            <el-statistic title="分块数量" :value="progress.chunks_count" suffix="块" />
          </el-col>
          <el-col :span="12" v-if="progress.ai_analysis_time">
            <el-statistic title="AI分析耗时" :value="progress.ai_analysis_time" suffix="秒" :precision="2" />
          </el-col>
        </el-row>

        <div v-if="progress.total_time" class="total-time">
          <el-tag type="success" size="large">
            <el-icon><Timer /></el-icon>
            总耗时: {{ progress.total_time }} 秒
          </el-tag>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="progress?.error_message" class="error-section">
        <el-alert
          type="error"
          title="处理失败"
          :description="progress.error_message"
          show-icon
          :closable="false"
        />
      </div>

      <!-- 处理日志 -->
      <div class="logs-section">
        <el-divider content-position="left">
          <el-icon><Document /></el-icon>
          处理日志
        </el-divider>
        
        <div class="logs-container">
          <el-timeline>
            <el-timeline-item
              v-for="(log, index) in progress?.logs || []"
              :key="index"
              :timestamp="log.time"
              :type="getLogType(log.level)"
              :icon="getLogIcon(log.level)"
              placement="top"
            >
              <div class="log-content">
                <div class="log-message">{{ log.message }}</div>
                <div v-if="log.details" class="log-details">
                  <el-tag
                    v-for="(value, key) in log.details"
                    :key="key"
                    size="small"
                    type="info"
                    effect="plain"
                  >
                    {{ key }}: {{ value }}
                  </el-tag>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <div class="footer-left">
          <el-tag v-if="progress?.started_at" type="info" size="large">
            开始时间: {{ progress.started_at }}
          </el-tag>
          <el-tag v-if="progress?.completed_at" type="success" size="large">
            完成时间: {{ progress.completed_at }}
          </el-tag>
        </div>
        <div class="footer-right">
          <el-button @click="handleClose">关闭</el-button>
          <el-button 
            v-if="isProcessing"
            type="primary" 
            @click="refreshProgress" 
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button
            v-if="isCompleted"
            type="success"
            @click="viewDocument"
          >
            <el-icon><View /></el-icon>
            查看文档
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Loading, Check, Close, Clock, DataAnalysis, Timer, Document,
  Refresh, View, SuccessFilled, WarningFilled, CircleCloseFilled, InfoFilled
} from '@element-plus/icons-vue'
import { progressApi, type ProcessProgress } from '../api/progress'
import { ElMessage } from 'element-plus'

interface Props {
  documentId: number
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue', 'completed'])

const router = useRouter()
const visible = ref(false)
const loading = ref(false)
const progress = ref<ProcessProgress | null>(null)
const autoRefreshTimer = ref<number | null>(null)

const dialogTitle = computed(() => {
  if (isCompleted.value) {
    return '文档处理记录（已完成）'
  } else if (isFailed.value) {
    return '文档处理记录（失败）'
  } else if (isProcessing.value) {
    return '文档处理进度（实时）'
  }
  return '文档处理记录'
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.documentId) {
    startMonitoring()
  } else {
    stopMonitoring()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 监听 documentId 变化，如果对话框已打开且 documentId 有效，则开始监控
watch(() => props.documentId, (newId) => {
  if (visible.value && newId) {
    startMonitoring()
  }
})

const isProcessing = computed(() => {
  const status = progress.value?.status
  return status && ['pending', 'parsing', 'analyzing', 'extracting', 'chunking', 'vectorizing'].includes(status)
})

const isCompleted = computed(() => progress.value?.status === 'completed')
const isFailed = computed(() => progress.value?.status === 'failed')

const hasStatistics = computed(() => {
  return progress.value && (
    progress.value.parsed_text_length ||
    progress.value.sections_count ||
    progress.value.chunks_count ||
    progress.value.ai_analysis_time
  )
})

const getProgressStatus = () => {
  if (isFailed.value) return 'exception'
  if (isCompleted.value) return 'success'
  return undefined
}

const getLogType = (level: string) => {
  const map: Record<string, any> = {
    success: 'success',
    error: 'danger',
    warning: 'warning',
    info: 'primary'
  }
  return map[level] || 'primary'
}

const getLogIcon = (level: string) => {
  const map: Record<string, any> = {
    success: SuccessFilled,
    error: CircleCloseFilled,
    warning: WarningFilled,
    info: InfoFilled
  }
  return map[level] || InfoFilled
}

const fetchProgress = async () => {
  // 确保 documentId 有效
  if (!props.documentId || props.documentId <= 0) {
    console.warn('无效的 documentId:', props.documentId)
    return
  }
  
  try {
    loading.value = true
    progress.value = await progressApi.getProgress(props.documentId)
    
    // 如果完成或失败，停止自动刷新
    if (isCompleted.value || isFailed.value) {
      stopMonitoring()
      if (isCompleted.value) {
        emit('completed')
      }
    }
  } catch (error: any) {
    console.error('获取进度失败:', error)
    // 如果是404，说明还没有日志记录，继续等待
    if (error.response?.status !== 404) {
      ElMessage.error('获取处理进度失败')
    }
  } finally {
    loading.value = false
  }
}

const refreshProgress = () => {
  fetchProgress()
}

const startMonitoring = () => {
  fetchProgress()
  
  // 每2秒自动刷新一次
  autoRefreshTimer.value = window.setInterval(() => {
    if (isProcessing.value) {
      fetchProgress()
    }
  }, 2000)
}

const stopMonitoring = () => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value)
    autoRefreshTimer.value = null
  }
}

const handleClose = () => {
  visible.value = false
  stopMonitoring()
}

const viewDocument = () => {
  router.push(`/documents/${props.documentId}`)
  handleClose()
}

defineExpose({
  fetchProgress
})
</script>

<style scoped lang="scss">
.progress-container {
  .progress-section {
    margin-bottom: 24px;

    .current-step {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 16px;
      padding: 12px;
      background: #f5f7fa;
      border-radius: 6px;

      .step-icon {
        font-size: 20px;
        color: #409eff;

        &.is-loading {
          animation: rotating 2s linear infinite;
        }
      }

      .step-text {
        font-size: 15px;
        font-weight: 500;
        color: #303133;
      }
    }

    .steps-info {
      margin-top: 12px;
      text-align: center;
      color: #909399;
      font-size: 14px;
    }
  }

  .statistics-section {
    margin-bottom: 24px;

    .el-row {
      margin-bottom: 16px;
    }

    .total-time {
      text-align: center;
      margin-top: 16px;

      .el-tag {
        padding: 12px 24px;
        font-size: 16px;

        .el-icon {
          margin-right: 8px;
        }
      }
    }
  }

  .error-section {
    margin-bottom: 24px;
  }

  .logs-section {
    .logs-container {
      max-height: 400px;
      overflow-y: auto;
      padding: 12px;
      background: #fafafa;
      border-radius: 6px;

      .log-content {
        .log-message {
          font-size: 14px;
          color: #303133;
          margin-bottom: 8px;
        }

        .log-details {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
      }
    }
  }

  .percentage-text {
    font-size: 16px;
    font-weight: 600;
  }
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;

  .footer-left {
    display: flex;
    gap: 12px;
  }

  .footer-right {
    display: flex;
    gap: 12px;
  }
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

