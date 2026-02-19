<template>
  <div class="exam-session" v-if="session">
    <!-- 顶部状态栏 -->
    <div class="session-header">
      <div class="header-left">
        <el-icon><EditPen /></el-icon>
        <span class="exam-title">{{ session.title }}</span>
        <el-tag size="small" type="info">{{ session.total_questions }}题</el-tag>
        <el-tag size="small" :type="difficultyType">{{ difficultyLabel }}</el-tag>
      </div>
      <div class="header-right">
        <div class="timer">
          <el-icon><Timer /></el-icon>
          {{ formatTime(elapsed) }}
        </div>
        <el-progress
          :percentage="progressPercent"
          :stroke-width="6"
          style="width:120px"
          :show-text="false"
        />
        <span class="progress-text">{{ answeredCount }}/{{ session.total_questions }}</span>
      </div>
    </div>

    <div class="session-body">
      <!-- 左侧题目导航 -->
      <div class="question-nav">
        <div class="nav-title">答题进度</div>
        <div class="nav-grid">
          <div
            v-for="(q, idx) in session.questions"
            :key="q.id"
            class="nav-dot"
            :class="{
              active: currentIndex === idx,
              answered: answers[q.id] !== undefined && answers[q.id] !== '',
            }"
            @click="currentIndex = idx"
          >
            {{ idx + 1 }}
          </div>
        </div>
        <div class="nav-legend">
          <span class="legend-item"><span class="dot answered"></span>已答</span>
          <span class="legend-item"><span class="dot"></span>未答</span>
        </div>
      </div>

      <!-- 右侧答题区 -->
      <div class="question-area">
        <div class="question-card" v-if="currentQuestion">
          <!-- 题目头部 -->
          <div class="question-header">
            <el-tag :type="typeTagType(currentQuestion.type)" size="small">
              {{ typeLabel(currentQuestion.type) }}
            </el-tag>
            <span class="question-index">第 {{ currentIndex + 1 }} 题 / 共 {{ session.total_questions }} 题</span>
            <span class="question-score">（{{ questionScore(currentQuestion.type) }}分）</span>
          </div>

          <!-- 题干 -->
          <div class="question-content">{{ currentQuestion.content }}</div>

          <!-- 单选题 -->
          <div v-if="currentQuestion.type === 'single'" class="options-list">
            <div
              v-for="(text, key) in currentQuestion.options"
              :key="key"
              class="option-item"
              :class="{ selected: answers[currentQuestion.id] === key }"
              @click="answers[currentQuestion.id] = key"
            >
              <span class="option-key">{{ key }}</span>
              <span class="option-text">{{ text }}</span>
            </div>
          </div>

          <!-- 判断题 -->
          <div v-else-if="currentQuestion.type === 'judge'" class="judge-options">
            <div
              class="judge-btn"
              :class="{ selected: answers[currentQuestion.id] === '正确' }"
              @click="answers[currentQuestion.id] = '正确'"
            >
              <el-icon color="#67c23a"><CircleCheck /></el-icon>
              正确
            </div>
            <div
              class="judge-btn"
              :class="{ selected: answers[currentQuestion.id] === '错误' }"
              @click="answers[currentQuestion.id] = '错误'"
            >
              <el-icon color="#f56c6c"><CircleClose /></el-icon>
              错误
            </div>
          </div>

          <!-- 简答题 -->
          <div v-else-if="currentQuestion.type === 'essay'" class="essay-area">
            <el-input
              v-model="answers[currentQuestion.id]"
              type="textarea"
              :rows="6"
              placeholder="请输入您的回答..."
              resize="none"
            />
            <div class="essay-tip">
              <el-icon><InfoFilled /></el-icon>
              AI将根据参考答案要点对您的回答进行评分和点评
            </div>
          </div>
        </div>

        <!-- 底部导航 -->
        <div class="question-footer">
          <el-button :disabled="currentIndex === 0" @click="currentIndex--">
            <el-icon><ArrowLeft /></el-icon> 上一题
          </el-button>
          <el-button
            v-if="currentIndex < session.total_questions - 1"
            type="primary"
            @click="currentIndex++"
          >
            下一题 <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button
            v-else
            type="success"
            @click="handleSubmit"
            :loading="store.loading"
          >
            <el-icon><Check /></el-icon>
            提交答案
          </el-button>
        </div>
      </div>
    </div>

    <!-- 提交确认 -->
    <el-dialog v-model="showSubmitConfirm" title="确认提交" width="400px">
      <div class="submit-confirm">
        <el-icon :size="48" color="#e6a23c"><Warning /></el-icon>
        <p>您已完成 <strong>{{ answeredCount }}/{{ session.total_questions }}</strong> 道题</p>
        <p v-if="unansweredCount > 0" class="warn-text">
          还有 {{ unansweredCount }} 道题未作答，提交后将计为0分
        </p>
        <p>简答题将由AI进行评阅，请确认提交</p>
      </div>
      <template #footer>
        <el-button @click="showSubmitConfirm = false">继续作答</el-button>
        <el-button type="primary" :loading="store.loading" @click="confirmSubmit">
          确认提交
        </el-button>
      </template>
    </el-dialog>
  </div>

  <!-- 加载中 -->
  <div v-else class="loading-state">
    <el-empty description="考试数据加载中..." />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  EditPen, Timer, CircleCheck, CircleClose, InfoFilled,
  ArrowLeft, ArrowRight, Check, Warning
} from '@element-plus/icons-vue'
import { useExamStore } from '../stores/examStore'
import type { QuestionItem } from '../types'

const route = useRoute()
const router = useRouter()
const store = useExamStore()

const examId = computed(() => Number(route.params.examId))
const session = computed(() => store.currentSession)
const currentIndex = ref(0)
const answers = ref<Record<number, string>>({})
const showSubmitConfirm = ref(false)
const elapsed = ref(0)
let timer: number | null = null

const currentQuestion = computed<QuestionItem | null>(() =>
  session.value?.questions[currentIndex.value] ?? null
)

const answeredCount = computed(() =>
  Object.values(answers.value).filter(v => v !== '').length
)
const unansweredCount = computed(() =>
  (session.value?.total_questions ?? 0) - answeredCount.value
)
const progressPercent = computed(() =>
  session.value ? Math.round(answeredCount.value / session.value.total_questions * 100) : 0
)

const difficultyLabel = computed(() => {
  const map: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
  return map[session.value?.difficulty ?? 'medium'] ?? '中等'
})
const difficultyType = computed(() => {
  const map: Record<string, any> = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[session.value?.difficulty ?? 'medium'] ?? 'warning'
})

const typeLabel = (type: string) => ({ single: '单选题', judge: '判断题', essay: '简答题' }[type] ?? type)
const typeTagType = (type: string) => ({ single: 'primary', judge: 'warning', essay: 'success' }[type] ?? 'info')
const questionScore = (type: string) => ({ single: 10, judge: 5, essay: 20 }[type] ?? 0)

const formatTime = (secs: number) => {
  const m = Math.floor(secs / 60).toString().padStart(2, '0')
  const s = (secs % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

const handleSubmit = () => {
  showSubmitConfirm.value = true
}

const confirmSubmit = async () => {
  if (!session.value) return
  showSubmitConfirm.value = false
  try {
    const answerList = session.value.questions.map(q => ({
      question_id: q.id,
      user_answer: answers.value[q.id] ?? '',
    }))
    await store.submitExam(session.value.exam_id, answerList, elapsed.value)
    router.push(`/exam/result/${session.value.exam_id}`)
  } catch (e: any) {
    ElMessage.error(e?.message || '提交失败，请重试')
  }
}

onMounted(() => {
  if (!store.currentSession || store.currentSession.exam_id !== examId.value) {
    ElMessage.warning('考试数据丢失，请重新生成')
    router.push('/exam')
    return
  }
  timer = window.setInterval(() => { elapsed.value++ }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped lang="scss">
.exam-session {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;

  .session-header {
    background: #fff;
    padding: 14px 24px;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;

    .header-left {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      .el-icon { font-size: 20px; color: #667eea; }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 14px;

      .timer {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 18px;
        font-weight: 700;
        color: #667eea;
        font-variant-numeric: tabular-nums;
      }

      .progress-text {
        font-size: 13px;
        color: #606266;
      }
    }
  }

  .session-body {
    flex: 1;
    display: flex;
    overflow: hidden;
    gap: 0;
  }

  .question-nav {
    width: 200px;
    flex-shrink: 0;
    background: #fff;
    border-right: 1px solid #e4e7ed;
    padding: 20px 16px;
    overflow-y: auto;

    .nav-title {
      font-size: 13px;
      font-weight: 600;
      color: #606266;
      margin-bottom: 14px;
    }

    .nav-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
      margin-bottom: 16px;

      .nav-dot {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        background: #f0f2f5;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 500;
        color: #606266;
        cursor: pointer;
        transition: all 0.2s;

        &:hover { background: #e4e7ed; }

        &.answered {
          background: #ecf5ff;
          color: #409eff;
          border: 1px solid #b3d8ff;
        }

        &.active {
          background: #667eea;
          color: #fff;
          border: none;
        }
      }
    }

    .nav-legend {
      display: flex;
      flex-direction: column;
      gap: 6px;

      .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #909399;

        .dot {
          width: 14px;
          height: 14px;
          border-radius: 3px;
          background: #f0f2f5;

          &.answered {
            background: #ecf5ff;
            border: 1px solid #b3d8ff;
          }
        }
      }
    }
  }

  .question-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 24px;
    gap: 16px;

    .question-card {
      flex: 1;
      background: #fff;
      border-radius: 12px;
      padding: 28px 32px;
      overflow-y: auto;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

      .question-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;

        .question-index {
          font-size: 14px;
          color: #606266;
          margin-left: auto;
        }

        .question-score {
          font-size: 13px;
          color: #909399;
        }
      }

      .question-content {
        font-size: 16px;
        line-height: 1.8;
        color: #1a1a2e;
        font-weight: 500;
        margin-bottom: 28px;
        padding: 16px 20px;
        background: #f9fafb;
        border-radius: 8px;
        border-left: 4px solid #667eea;
      }

      .options-list {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .option-item {
          display: flex;
          align-items: flex-start;
          gap: 14px;
          padding: 14px 18px;
          border: 2px solid #e4e7ed;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.2s;

          &:hover {
            border-color: #667eea;
            background: #f5f7ff;
          }

          &.selected {
            border-color: #667eea;
            background: #f0f2ff;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.12);
          }

          .option-key {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #f0f2f5;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 13px;
            color: #606266;
            flex-shrink: 0;
          }

          &.selected .option-key {
            background: #667eea;
            color: #fff;
          }

          .option-text {
            font-size: 15px;
            line-height: 1.6;
            color: #303133;
            padding-top: 2px;
          }
        }
      }

      .judge-options {
        display: flex;
        gap: 20px;

        .judge-btn {
          flex: 1;
          max-width: 180px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          padding: 20px;
          border: 2px solid #e4e7ed;
          border-radius: 12px;
          cursor: pointer;
          font-size: 18px;
          font-weight: 600;
          transition: all 0.2s;

          &:hover { background: #f5f7fa; }

          &.selected {
            border-color: #667eea;
            background: #f0f2ff;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.12);
          }
        }
      }

      .essay-area {
        .essay-tip {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-top: 10px;
          font-size: 13px;
          color: #909399;
        }
      }
    }

    .question-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #fff;
      padding: 14px 20px;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
  }
}

.loading-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-confirm {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
  text-align: center;

  p { margin: 0; font-size: 15px; color: #303133; }
  .warn-text { color: #e6a23c; }
}
</style>
