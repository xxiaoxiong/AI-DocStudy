<template>
  <div class="qa-chat">
    <!-- 顶部标题栏 -->
    <div class="chat-header">
      <div class="header-left">
        <el-icon :size="20"><ChatDotRound /></el-icon>
        <span class="title">智能问答</span>
        <el-tag v-if="documentTitle !== '全部文档'" size="small" type="info">{{ documentTitle }}</el-tag>
        <el-tag v-else size="small" type="success">全库检索</el-tag>
      </div>
      <el-button size="small" text @click="store.clearMessages()">
        <el-icon><Delete /></el-icon>
        清空对话
      </el-button>
    </div>

    <!-- 消息区域 -->
    <div class="messages-wrapper" ref="messagesRef">
      <!-- 空状态 -->
      <div v-if="store.messages.length === 0 && !store.pendingQuestion" class="empty-state">
        <el-icon :size="64" color="#c0c4cc"><ChatDotRound /></el-icon>
        <p class="empty-title">开始智能问答</p>
        <p class="empty-sub">{{ documentTitle === '全部文档' ? '将对所有已导入文档进行检索' : `基于《${documentTitle}》回答问题` }}</p>
      </div>

      <div v-else class="messages-list">
        <!-- 历史消息 -->
        <message-item
          v-for="message in store.messages"
          :key="message.id"
          :message="message"
        />

        <!-- 待回答的用户问题（AI思考中时显示） -->
        <div v-if="store.pendingQuestion" class="bubble-row user-row">
          <div class="bubble user-bubble">{{ store.pendingQuestion }}</div>
          <div class="avatar user-avatar">
            <el-icon><User /></el-icon>
          </div>
        </div>

        <!-- AI思考中 -->
        <div v-if="store.loading" class="bubble-row ai-row">
          <div class="avatar ai-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="bubble ai-bubble thinking">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 相关问题推荐 -->
    <div v-if="store.relatedQuestions.length > 0" class="related-questions">
      <span class="related-label">
        <el-icon><QuestionFilled /></el-icon>
        你可能还想问
      </span>
      <div class="chips">
        <el-tag
          v-for="(q, i) in store.relatedQuestions"
          :key="i"
          class="chip"
          @click="handleQuestionClick(q)"
        >{{ q }}</el-tag>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input
        v-model="question"
        type="textarea"
        :rows="3"
        placeholder="输入问题，按 Enter 发送，Shift+Enter 换行..."
        :disabled="store.loading"
        @keydown="handleKeydown"
        resize="none"
      />
      <div class="input-footer">
        <span class="tip">Enter 发送 · Shift+Enter 换行</span>
        <el-button
          type="primary"
          :loading="store.loading"
          :disabled="!question.trim()"
          @click="handleSubmit"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChatDotRound, QuestionFilled, Promotion, User, Delete } from '@element-plus/icons-vue'
import { useQAStore } from '../stores/qaStore'
import { useDocumentStore } from '@/modules/document/stores/documentStore'
import { useQA } from '../composables/useQA'
import MessageItem from '../components/MessageItem.vue'

const route = useRoute()
const store = useQAStore()
const documentStore = useDocumentStore()
const { handleAsk } = useQA()

const question = ref('')
const messagesRef = ref<HTMLElement>()

const documentId = computed(() => {
  const id = route.params.documentId
  return id ? Number(id) : null
})

const documentTitle = computed(() => {
  if (!documentId.value) return '全部文档'
  return documentStore.currentDocument?.title || '文档'
})

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSubmit()
  }
}

const handleSubmit = async () => {
  if (!question.value.trim() || store.loading) return
  const q = question.value.trim()
  question.value = ''
  scrollToBottom()
  await handleAsk(documentId.value, q)
  scrollToBottom()
}

const handleQuestionClick = (q: string) => {
  question.value = q
  handleSubmit()
}

watch(() => store.messages.length, scrollToBottom)
watch(() => store.loading, scrollToBottom)

onMounted(async () => {
  store.clearMessages()
  if (documentId.value) {
    await documentStore.fetchDocumentDetail(documentId.value)
    await store.fetchHistory(documentId.value)
  } else {
    await store.fetchHistory(null)
  }

  const presetQuestion = route.query.q as string
  if (presetQuestion) {
    question.value = presetQuestion
    await handleSubmit()
  }

  scrollToBottom()
})
</script>

<style scoped lang="scss">
.qa-chat {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;

  // 顶部标题栏
  .chat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 20px;
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    flex-shrink: 0;

    .header-left {
      display: flex;
      align-items: center;
      gap: 10px;
      color: #303133;

      .title {
        font-size: 16px;
        font-weight: 600;
      }
    }
  }

  // 消息区域
  .messages-wrapper {
    flex: 1;
    overflow-y: auto;
    padding: 24px 20px;
    scroll-behavior: smooth;

    .empty-state {
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
      color: #909399;

      .empty-title {
        font-size: 18px;
        font-weight: 600;
        color: #606266;
        margin: 0;
      }

      .empty-sub {
        font-size: 14px;
        margin: 0;
      }
    }

    .messages-list {
      max-width: 1100px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
  }

  // 气泡行
  .bubble-row {
    display: flex;
    align-items: flex-end;
    gap: 10px;

    &.user-row {
      flex-direction: row-reverse;
    }

    &.ai-row {
      flex-direction: row;
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
    }
  }

  .bubble {
    max-width: 70%;
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
      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    }

    &.thinking {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 14px 20px;

      .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #c0c4cc;
        animation: bounce 1.2s infinite;

        &:nth-child(2) { animation-delay: 0.2s; }
        &:nth-child(3) { animation-delay: 0.4s; }
      }
    }
  }

  // 相关问题
  .related-questions {
    padding: 10px 20px;
    background: #fff;
    border-top: 1px solid #f0f0f0;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    flex-shrink: 0;

    .related-label {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      color: #909399;
      white-space: nowrap;
    }

    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .chip {
      cursor: pointer;
      transition: all 0.2s;
      &:hover { transform: translateY(-1px); }
    }
  }

  // 输入区域
  .input-area {
    padding: 12px 20px 16px;
    background: #fff;
    border-top: 1px solid #e4e7ed;
    flex-shrink: 0;

    :deep(.el-textarea__inner) {
      border-radius: 8px;
      font-size: 14px;
      resize: none;
    }

    .input-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;

      .tip {
        font-size: 12px;
        color: #c0c4cc;
      }
    }
  }
}

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}

// 滚动条
.messages-wrapper::-webkit-scrollbar {
  width: 6px;
}
.messages-wrapper::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}
</style>



