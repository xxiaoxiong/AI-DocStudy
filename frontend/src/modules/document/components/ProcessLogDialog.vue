<template>
  <el-dialog
    v-model="visible"
    title="处理日志详情"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
    class="process-log-dialog"
  >
    <div v-loading="loading" class="log-container">
      <!-- 处理状态概览 -->
      <el-card class="status-card" shadow="never">
        <div class="status-header">
          <div class="status-info">
            <el-tag :type="getStatusType(log?.status)" size="large">
              {{ getStatusText(log?.status) }}
            </el-tag>
            <span class="current-step">{{ log?.current_step }}</span>
          </div>
          <div class="progress-info">
            <el-progress
              :percentage="log?.progress || 0"
              :status="log?.status === 'failed' ? 'exception' : log?.status === 'completed' ? 'success' : undefined"
            />
          </div>
        </div>

        <!-- 统计信息 -->
        <el-row :gutter="16" class="stats-row">
          <el-col :span="6">
            <div class="stat-item">
              <span class="stat-label">解析文本</span>
              <span class="stat-value">{{ formatNumber(log?.parsed_text_length) }} 字</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <span class="stat-label">章节数量</span>
              <span class="stat-value">{{ log?.sections_count || 0 }} 个</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <span class="stat-label">分块数量</span>
              <span class="stat-value">{{ log?.chunks_count || 0 }} 块</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <span class="stat-label">AI分析耗时</span>
              <span class="stat-value">{{ log?.ai_analysis_time || 0 }} 秒</span>
            </div>
          </el-col>
        </el-row>

        <!-- 错误信息 -->
        <el-alert
          v-if="log?.error_message"
          type="error"
          :title="log.error_message"
          :closable="false"
          show-icon
        >
          <template v-if="log.error_traceback">
            <el-button size="small" text @click="showErrorDetail = !showErrorDetail">
              {{ showErrorDetail ? '隐藏' : '查看' }}错误堆栈
            </el-button>
            <pre v-if="showErrorDetail" class="error-trace">{{ log.error_traceback }}</pre>
          </template>
        </el-alert>
      </el-card>

      <!-- 详细日志 -->
      <el-card class="logs-card" shadow="never">
        <template #header>
          <div class="logs-header">
            <span>
              <el-icon><Tickets /></el-icon>
              详细日志 ({{ logs.length }} 条)
            </span>
            <div class="log-filters">
              <el-radio-group v-model="logLevelFilter" size="small">
                <el-radio-button label="">全部</el-radio-button>
                <el-radio-button label="info">信息</el-radio-button>
                <el-radio-button label="success">成功</el-radio-button>
                <el-radio-button label="warning">警告</el-radio-button>
                <el-radio-button label="error">错误</el-radio-button>
              </el-radio-group>
              <el-button size="small" @click="copyLogs">
                <el-icon><CopyDocument /></el-icon>
                复制日志
              </el-button>
            </div>
          </div>
        </template>

        <div class="logs-list">
          <el-empty v-if="filteredLogs.length === 0" description="暂无日志" />
          
          <div
            v-for="(logItem, index) in filteredLogs"
            :key="index"
            :class="['log-item', `log-${logItem.level}`]"
          >
            <div class="log-header">
              <el-tag :type="getLogLevelType(logItem.level)" size="small">
                {{ getLogLevelText(logItem.level) }}
              </el-tag>
              <span class="log-time">{{ logItem.time }}</span>
            </div>
            <div class="log-message">{{ logItem.message }}</div>
            <div v-if="logItem.details" class="log-details">
              <el-button size="small" text @click="toggleDetails(index)">
                <el-icon><InfoFilled /></el-icon>
                {{ expandedLogs.has(index) ? '隐藏' : '查看' }}详情
              </el-button>
              <pre v-if="expandedLogs.has(index)" class="details-content">{{ formatDetails(logItem.details) }}</pre>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  Tickets, CopyDocument, Refresh, InfoFilled
} from '@element-plus/icons-vue'
import { progressApi, type ProcessLog } from '../api/progress'
import { ElMessage } from 'element-plus'

interface Props {
  documentId: number
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const loading = ref(false)
const log = ref<ProcessLog | null>(null)
const logLevelFilter = ref('')
const showErrorDetail = ref(false)
const expandedLogs = ref(new Set<number>())

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    fetchLog()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const logs = computed(() => {
  if (!log.value?.logs) return []
  try {
    const logsData = typeof log.value.logs === 'string' 
      ? JSON.parse(log.value.logs) 
      : log.value.logs
    return Array.isArray(logsData) ? logsData : []
  } catch {
    return []
  }
})

const filteredLogs = computed(() => {
  if (!logLevelFilter.value) return logs.value
  return logs.value.filter(item => item.level === logLevelFilter.value)
})

const getStatusType = (status?: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    parsing: 'warning',
    analyzing: 'warning',
    extracting: 'warning',
    chunking: 'warning',
    vectorizing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status || ''] || 'info'
}

const getStatusText = (status?: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    parsing: '解析中',
    analyzing: '分析中',
    extracting: '提取中',
    chunking: '分块中',
    vectorizing: '向量化中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status || ''] || status || '未知'
}

const getLogLevelType = (level: string) => {
  const map: Record<string, any> = {
    info: 'info',
    success: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return map[level] || 'info'
}

const getLogLevelText = (level: string) => {
  const map: Record<string, string> = {
    info: '信息',
    success: '成功',
    warning: '警告',
    error: '错误'
  }
  return map[level] || level
}

const formatNumber = (num?: number) => {
  if (!num) return 0
  return num.toLocaleString()
}

const formatDetails = (details: any) => {
  return JSON.stringify(details, null, 2)
}

const toggleDetails = (index: number) => {
  if (expandedLogs.value.has(index)) {
    expandedLogs.value.delete(index)
  } else {
    expandedLogs.value.add(index)
  }
}

const fetchLog = async () => {
  try {
    loading.value = true
    log.value = await progressApi.getProgress(props.documentId)
  } catch (error) {
    ElMessage.error('获取处理日志失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchLog()
}

const copyLogs = async () => {
  try {
    const logsText = logs.value
      .map(item => `[${item.time}] [${item.level.toUpperCase()}] ${item.message}`)
      .join('\n')
    await navigator.clipboard.writeText(logsText)
    ElMessage.success('已复制日志')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped lang="scss">
.process-log-dialog {
  :deep(.el-dialog__body) {
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
  }
}

.log-container {
  display: flex;
  flex-direction: column;
  gap: 16px;

  .status-card {
    .status-header {
      margin-bottom: 20px;

      .status-info {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;

        .current-step {
          font-size: 16px;
          font-weight: 500;
          color: #303133;
        }
      }
    }

    .stats-row {
      margin-top: 20px;

      .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 12px;
        background: #f5f7fa;
        border-radius: 6px;

        .stat-label {
          font-size: 12px;
          color: #909399;
          margin-bottom: 4px;
        }

        .stat-value {
          font-size: 18px;
          font-weight: 600;
          color: #303133;
        }
      }
    }

    .el-alert {
      margin-top: 16px;

      .error-trace {
        margin-top: 12px;
        padding: 12px;
        background: #f5f7fa;
        border-radius: 4px;
        font-size: 12px;
        line-height: 1.6;
        overflow-x: auto;
      }
    }
  }

  .logs-card {
    .logs-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .log-filters {
        display: flex;
        gap: 12px;
      }
    }

    .logs-list {
      max-height: 500px;
      overflow-y: auto;

      .log-item {
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        border-left: 3px solid #dcdfe6;
        background: #f5f7fa;
        transition: all 0.3s;

        &:hover {
          background: #ebeef5;
        }

        &.log-info {
          border-left-color: #409eff;
        }

        &.log-success {
          border-left-color: #67c23a;
          background: #f0f9ff;
        }

        &.log-warning {
          border-left-color: #e6a23c;
          background: #fdf6ec;
        }

        &.log-error {
          border-left-color: #f56c6c;
          background: #fef0f0;
        }

        .log-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .log-time {
            font-size: 12px;
            color: #909399;
          }
        }

        .log-message {
          font-size: 14px;
          line-height: 1.6;
          color: #303133;
          word-break: break-word;
        }

        .log-details {
          margin-top: 8px;

          .details-content {
            margin-top: 8px;
            padding: 12px;
            background: #fff;
            border-radius: 4px;
            font-size: 12px;
            line-height: 1.6;
            overflow-x: auto;
          }
        }
      }
    }
  }
}
</style>

