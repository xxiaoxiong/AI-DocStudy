<template>
  <div class="qa-chat">
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/documents' }">文档管理</el-breadcrumb-item>
        <el-breadcrumb-item>智能问答 - {{ documentTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="chat-container">
      <!-- 消息列表 -->
      <div class="messages-wrapper" ref="messagesRef">
        <div v-if="store.messages.length === 0" class="empty-state">
          <el-empty description="还没有对话记录，开始提问吧！">
            <template #image>
              <el-icon :size="100" color="#909399"><chat-dot-round /></el-icon>
            </template>
          </el-empty>
        </div>

        <div v-else class="messages-list">
          <message-item
            v-for="message in store.messages"
            :key="message.id"
            :message="message"
          />
        </div>

        <!-- 加载中 -->
        <div v-if="store.loading" class="loading-message">
          <div class="loading-avatar">
            <el-icon class="is-loading"><loading /></el-icon>
          </div>
          <div class="loading-text">AI正在思考中...</div>
        </div>
      </div>

      <!-- 相关问题推荐 -->
      <div v-if="store.relatedQuestions.length > 0" class="related-questions">
        <div class="related-title">
          <el-icon><question-filled /></el-icon>
          你可能还想问
        </div>
        <div class="question-chips">
          <el-tag
            v-for="(q, index) in store.relatedQuestions"
            :key="index"
            class="question-chip"
            @click="handleQuestionClick(q)"
          >
            {{ q }}
          </el-tag>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题..."
          :disabled="store.loading"
          @keydown.enter.ctrl="handleSubmit"
        />
        <div class="input-actions">
          <span class="tip">Ctrl + Enter 发送</span>
          <el-button
            type="primary"
            :loading="store.loading"
            :disabled="!question.trim()"
            @click="handleSubmit"
          >
            <el-icon><promotion /></el-icon>
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChatDotRound, Loading, QuestionFilled, Promotion } from '@element-plus/icons-vue'
import { useQAStore } from '../stores/qaStore'
import { useDocumentStore } from '@/modules/document/stores/documentStore'
import { useQA } from '../composables/useQA'
import MessageItem from '../components/MessageItem.vue'

const route = useRoute()
const router = useRouter()
const store = useQAStore()
const documentStore = useDocumentStore()
const { handleAsk } = useQA()

const question = ref('')
const messagesRef = ref<HTMLElement>()

const documentId = computed(() => Number(route.params.documentId))
const documentTitle = computed(() => documentStore.currentDocument?.title || '文档')

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const handleSubmit = async () => {
  if (!question.value.trim() || store.loading) return

  const q = question.value
  question.value = ''

  await handleAsk(documentId.value, q)
  scrollToBottom()
}

const handleQuestionClick = (q: string) => {
  question.value = q
  handleSubmit()
}

const goBack = () => {
  router.push('/documents')
}

// 监听消息变化，自动滚动到底部
watch(() => store.messages.length, () => {
  scrollToBottom()
})

onMounted(async () => {
  // 获取文档信息
  await documentStore.fetchDocumentDetail(documentId.value)
  
  // 加载历史记录
  await store.fetchHistory(documentId.value)
  
  scrollToBottom()
})
</script>

<style scoped lang="scss">
.qa-chat {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;

  .page-header {
    padding: 16px 24px;
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    margin-bottom: 16px;
  }

  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 0 24px 24px;
    overflow: hidden;

    .messages-wrapper {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      background: #fff;
      border-radius: 8px;
      margin-bottom: 16px;

      .empty-state {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .messages-list {
        max-width: 900px;
        margin: 0 auto;
      }

      .loading-message {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        margin-left: 48px;

        .loading-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: #f0f0f0;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          color: #409eff;
        }

        .loading-text {
          color: #909399;
          font-size: 14px;
        }
      }
    }

    .related-questions {
      padding: 16px 20px;
      background: #fff;
      border-radius: 8px;
      margin-bottom: 16px;

      .related-title {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        font-weight: 600;
        color: #606266;
        margin-bottom: 12px;
      }

      .question-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .question-chip {
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          }
        }
      }
    }

    .input-area {
      background: #fff;
      border-radius: 8px;
      padding: 16px;

      .input-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;

        .tip {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}
</style>



