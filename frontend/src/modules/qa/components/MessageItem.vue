<template>
  <div class="message-item" :class="{ 'is-question': isQuestion }">
    <div class="message-header">
      <div class="avatar">
        <el-icon v-if="isQuestion"><user /></el-icon>
        <el-icon v-else><chat-dot-round /></el-icon>
      </div>
      <div class="meta">
        <span class="role">{{ isQuestion ? '我' : 'AI助手' }}</span>
        <span class="time">{{ formatTime(message.created_at) }}</span>
      </div>
    </div>

    <div class="message-content">
      <div v-if="isQuestion" class="question-text">
        {{ message.question }}
      </div>
      <div v-else class="answer-text">
        <div class="answer-body">{{ message.answer }}</div>
        
        <!-- 来源引用 -->
        <div v-if="message.sources && message.sources.length > 0" class="sources">
          <div class="sources-title">
            <el-icon><document /></el-icon>
            参考来源
          </div>
          <div class="source-list">
            <el-collapse accordion>
              <el-collapse-item
                v-for="(source, index) in message.sources"
                :key="index"
                :title="`来源 ${index + 1} (相关度: ${(source.relevance_score * 100).toFixed(0)}%)`"
              >
                <div class="source-content">{{ source.content }}</div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>

        <!-- 反馈按钮 -->
        <div class="feedback">
          <span class="feedback-label">这个回答有帮助吗？</span>
          <el-button-group>
            <el-button
              size="small"
              :type="message.helpful === true ? 'primary' : ''"
              @click="handleFeedback(true)"
            >
              <el-icon><select /></el-icon>
              有帮助
            </el-button>
            <el-button
              size="small"
              :type="message.helpful === false ? 'danger' : ''"
              @click="handleFeedback(false)"
            >
              <el-icon><close /></el-icon>
              没帮助
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { User, ChatDotRound, Document, Select, Close } from '@element-plus/icons-vue'
import { useQA } from '../composables/useQA'
import type { QARecord } from '../types'

const props = defineProps<{
  message: QARecord
  isQuestion?: boolean
}>()

const { handleFeedback: submitFeedback } = useQA()

const isQuestion = computed(() => props.isQuestion || false)

const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleFeedback = (helpful: boolean) => {
  submitFeedback(props.message.id, helpful)
}
</script>

<style scoped lang="scss">
.message-item {
  margin-bottom: 24px;
  
  .message-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
    
    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      background: #f0f0f0;
      color: #666;
    }
    
    .meta {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .role {
        font-weight: 600;
        color: #303133;
      }
      
      .time {
        font-size: 12px;
        color: #909399;
      }
    }
  }
  
  .message-content {
    margin-left: 48px;
    
    .question-text {
      padding: 12px 16px;
      background: #ecf5ff;
      border-radius: 8px;
      color: #303133;
      line-height: 1.6;
    }
    
    .answer-text {
      .answer-body {
        padding: 12px 16px;
        background: #f5f7fa;
        border-radius: 8px;
        color: #303133;
        line-height: 1.8;
        white-space: pre-wrap;
      }
      
      .sources {
        margin-top: 16px;
        padding: 12px;
        background: #fff;
        border: 1px solid #e4e7ed;
        border-radius: 8px;
        
        .sources-title {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          font-weight: 600;
          color: #606266;
          margin-bottom: 12px;
        }
        
        .source-content {
          padding: 8px;
          background: #f9f9f9;
          border-radius: 4px;
          font-size: 13px;
          color: #606266;
          line-height: 1.6;
        }
      }
      
      .feedback {
        margin-top: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        
        .feedback-label {
          font-size: 13px;
          color: #909399;
        }
      }
    }
  }
  
  &.is-question {
    .avatar {
      background: #409eff;
      color: #fff;
    }
  }
}
</style>



