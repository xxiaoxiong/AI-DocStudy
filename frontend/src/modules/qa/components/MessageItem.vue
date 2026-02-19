<template>
  <div class="message-wrapper">
  <!-- 用户问题气泡（右侧） -->
  <div class="bubble-row user-row">
    <div class="bubble user-bubble">{{ message.question }}</div>
    <div class="avatar user-avatar">
      <el-icon><User /></el-icon>
    </div>
  </div>

  <!-- AI回答气泡（左侧） -->
  <div class="bubble-row ai-row">
    <div class="avatar ai-avatar">
      <el-icon><ChatDotRound /></el-icon>
    </div>
    <div class="ai-answer">
      <div class="bubble ai-bubble markdown-body" v-html="renderedAnswer"></div>

      <!-- 参考来源（折叠） -->
      <div v-if="message.sources && message.sources.length > 0" class="sources">
        <el-collapse>
          <el-collapse-item>
            <template #title>
              <span class="sources-title">
                <el-icon><Document /></el-icon>
                参考来源 ({{ message.sources.length }} 条)
              </span>
            </template>
            <div
              v-for="(source, i) in message.sources"
              :key="i"
              class="source-item"
            >
              <div class="source-meta">
                <el-tag size="small" type="info">来源 {{ i + 1 }}</el-tag>
                <el-tag size="small" :type="getRelevanceType(source.relevance_score)">
                  相关度 {{ (source.relevance_score * 100).toFixed(0) }}%
                </el-tag>
                <el-tag v-if="source.document_title" size="small" type="warning">
                  <el-icon><Document /></el-icon>
                  {{ source.document_title }}
                </el-tag>
              </div>
              <div class="source-content">{{ source.content }}</div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <div class="msg-time">{{ formatTime(message.created_at) }}</div>
    </div>
  </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import { User, ChatDotRound, Document } from '@element-plus/icons-vue'
import type { QARecord } from '../types'

const props = defineProps<{ message: QARecord }>()

const renderedAnswer = computed(() => {
  if (!props.message.answer) return ''
  return marked.parse(props.message.answer) as string
})

const getRelevanceType = (score: number) => {
  if (score >= 0.7) return 'success'
  if (score >= 0.4) return 'warning'
  return 'info'
}

const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped lang="scss">
.message-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

// 气泡行
.bubble-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;

  &.user-row {
    flex-direction: row-reverse;
    margin-bottom: 8px;
  }

  &.ai-row {
    flex-direction: row;
    align-items: flex-start;
  }
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;

  &.user-avatar {
    background: #667eea;
    color: #fff;
  }

  &.ai-avatar {
    background: #f0f2f5;
    color: #667eea;
    margin-top: 2px;
  }
}

.bubble {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;

  &.user-bubble {
    background: #667eea;
    color: #fff;
    border-bottom-right-radius: 4px;
  }

  &.ai-bubble {
    background: #fff;
    color: #303133;
    border-top-left-radius: 4px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  }
}

.ai-answer {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 85%;
}

// Markdown 渲染样式
.markdown-body {
  :deep(h1), :deep(h2), :deep(h3), :deep(h4) {
    font-weight: 600;
    margin: 12px 0 6px;
    color: #1a1a2e;
    line-height: 1.4;
  }
  :deep(h1) { font-size: 18px; }
  :deep(h2) { font-size: 16px; }
  :deep(h3) { font-size: 15px; }

  :deep(p) {
    margin: 6px 0;
    line-height: 1.7;
  }

  :deep(ul), :deep(ol) {
    padding-left: 20px;
    margin: 6px 0;

    li {
      margin: 4px 0;
      line-height: 1.6;
    }
  }

  :deep(strong) {
    font-weight: 600;
    color: #1a1a2e;
  }

  :deep(em) {
    font-style: italic;
    color: #555;
  }

  :deep(code) {
    background: #f0f2f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #e83e8c;
  }

  :deep(pre) {
    background: #1e1e2e;
    color: #cdd6f4;
    padding: 12px 16px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 10px 0;

    code {
      background: none;
      color: inherit;
      padding: 0;
      font-size: 13px;
    }
  }

  :deep(blockquote) {
    border-left: 3px solid #667eea;
    padding: 4px 12px;
    margin: 8px 0;
    color: #606266;
    background: #f5f7ff;
    border-radius: 0 4px 4px 0;
  }

  :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 13px;

    th, td {
      border: 1px solid #e4e7ed;
      padding: 6px 10px;
      text-align: left;
    }

    th {
      background: #f5f7fa;
      font-weight: 600;
    }
  }

  :deep(hr) {
    border: none;
    border-top: 1px solid #e4e7ed;
    margin: 12px 0;
  }
}

// 参考来源
.sources {
  :deep(.el-collapse) {
    border: none;
    background: transparent;
  }
  :deep(.el-collapse-item__header) {
    background: transparent;
    border: none;
    font-size: 13px;
    height: 32px;
    padding: 0 4px;
  }
  :deep(.el-collapse-item__wrap) {
    border: none;
    background: transparent;
  }
  :deep(.el-collapse-item__content) {
    padding: 0;
  }

  .sources-title {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #909399;
    font-size: 13px;
  }

  .source-item {
    padding: 8px 10px;
    background: #f9fafb;
    border-radius: 6px;
    margin-bottom: 6px;
    border: 1px solid #f0f0f0;

    .source-meta {
      display: flex;
      gap: 6px;
      margin-bottom: 6px;
    }

    .source-content {
      font-size: 13px;
      color: #606266;
      line-height: 1.6;
    }
  }
}

.msg-time {
  font-size: 11px;
  color: #c0c4cc;
  padding-left: 4px;
}
</style>



