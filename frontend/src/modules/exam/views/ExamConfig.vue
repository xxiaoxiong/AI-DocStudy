<template>
  <div class="exam-config">
    <div class="page-header">
      <div class="header-left">
        <el-icon class="header-icon"><EditPen /></el-icon>
        <div>
          <h1>生成考题</h1>
          <p class="header-sub">
            {{ documentTitle ? `基于《${documentTitle}》出题` : '跨所有已导入文档出题' }}
          </p>
        </div>
      </div>
    </div>

    <div class="config-body">
      <!-- 配置卡片 -->
      <el-card class="config-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>出题配置</span>
          </div>
        </template>

        <el-form :model="config" label-width="100px" size="large">
          <!-- 出题范围 -->
          <el-form-item label="出题范围">
            <div class="scope-selector">
              <div
                class="scope-card"
                :class="{ active: !config.document_id }"
                @click="config.document_id = null"
              >
                <el-icon :size="28" color="#67c23a"><Collection /></el-icon>
                <div class="scope-title">全库出题</div>
                <div class="scope-sub">跨所有已导入文档</div>
              </div>
              <div
                v-if="documentId"
                class="scope-card"
                :class="{ active: !!config.document_id }"
                @click="config.document_id = documentId"
              >
                <el-icon :size="28" color="#667eea"><Document /></el-icon>
                <div class="scope-title">当前文档</div>
                <div class="scope-sub">{{ documentTitle || '指定文档' }}</div>
              </div>
            </div>
          </el-form-item>

          <!-- 难度 -->
          <el-form-item label="难度等级">
            <el-radio-group v-model="config.difficulty" class="difficulty-group">
              <el-radio-button value="easy">
                <el-icon><Sunny /></el-icon> 简单
              </el-radio-button>
              <el-radio-button value="medium">
                <el-icon><Cloudy /></el-icon> 中等
              </el-radio-button>
              <el-radio-button value="hard">
                <el-icon><Lightning /></el-icon> 困难
              </el-radio-button>
            </el-radio-group>
          </el-form-item>

          <!-- 题型数量 -->
          <el-form-item label="单选题">
            <div class="count-row">
              <el-slider v-model="config.single_count" :min="0" :max="10" :step="1" show-stops style="width:260px" />
              <span class="count-label">{{ config.single_count }} 道 × 10分</span>
            </div>
          </el-form-item>

          <el-form-item label="判断题">
            <div class="count-row">
              <el-slider v-model="config.judge_count" :min="0" :max="10" :step="1" show-stops style="width:260px" />
              <span class="count-label">{{ config.judge_count }} 道 × 5分</span>
            </div>
          </el-form-item>

          <el-form-item label="简答题">
            <div class="count-row">
              <el-slider v-model="config.essay_count" :min="0" :max="5" :step="1" show-stops style="width:260px" />
              <span class="count-label">{{ config.essay_count }} 道 × 20分</span>
            </div>
          </el-form-item>

          <!-- 分数预览 -->
          <el-form-item label=" ">
            <el-alert
              :title="`共 ${totalQuestions} 道题，满分 ${totalScore} 分，60分及格`"
              type="info"
              :closable="false"
              show-icon
            />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 历史记录 -->
      <el-card class="history-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><Clock /></el-icon>
            <span>最近考试记录</span>
          </div>
        </template>
        <div v-if="store.loading && !store.history.length" class="history-loading">
          <el-skeleton :rows="3" animated />
        </div>
        <el-empty v-else-if="!store.history.length" description="暂无考试记录" :image-size="60" />
        <div v-else class="history-list">
          <div
            v-for="item in store.history"
            :key="item.exam_id"
            class="history-item"
            @click="viewHistory(item.exam_id)"
          >
            <div class="history-info">
              <div class="history-title">{{ item.title }}</div>
              <div class="history-meta">
                <span>{{ item.total_questions }}题</span>
                <span>{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
            <div class="history-score">
              <el-tag :type="item.passed ? 'success' : 'danger'" size="large">
                {{ item.percentage.toFixed(0) }}%
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 底部操作 -->
    <div class="config-footer">
      <el-button size="large" @click="goBack">返回</el-button>
      <el-button
        type="primary"
        size="large"
        :loading="store.loading"
        :disabled="totalQuestions === 0"
        @click="handleGenerate"
      >
        <el-icon><MagicStick /></el-icon>
        AI生成考题
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  EditPen, Setting, Collection, Document, Clock,
  Sunny, Cloudy, Lightning, MagicStick
} from '@element-plus/icons-vue'
import { useExamStore } from '../stores/examStore'
import type { ExamConfig } from '../types'

const route = useRoute()
const router = useRouter()
const store = useExamStore()

const documentId = computed(() => {
  const id = route.params.documentId
  return id ? Number(id) : null
})
const documentTitle = computed(() => route.query.title as string || '')

const config = ref<ExamConfig>({
  document_id: documentId.value,
  single_count: 5,
  judge_count: 3,
  essay_count: 2,
  difficulty: 'medium',
})

const totalQuestions = computed(() =>
  config.value.single_count + config.value.judge_count + config.value.essay_count
)
const totalScore = computed(() =>
  config.value.single_count * 10 + config.value.judge_count * 5 + config.value.essay_count * 20
)

const handleGenerate = async () => {
  if (totalQuestions.value === 0) {
    ElMessage.warning('请至少选择一种题型')
    return
  }
  try {
    const session = await store.generateExam({
      ...config.value,
      document_title: documentTitle.value || undefined,
    })
    router.push(`/exam/session/${session.exam_id}`)
  } catch (e: any) {
    ElMessage.error(e?.message || 'AI生成题目失败，请重试')
  }
}

const viewHistory = (examId: number) => {
  router.push(`/exam/result/${examId}`)
}

const goBack = () => {
  if (documentId.value) {
    router.push(`/document/${documentId.value}`)
  } else {
    router.push('/documents')
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => {
  store.fetchHistory(1, 5)
})
</script>

<style scoped lang="scss">
.exam-config {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;

  .page-header {
    background: #fff;
    padding: 20px 32px;
    border-bottom: 1px solid #e4e7ed;
    flex-shrink: 0;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      .header-icon {
        font-size: 36px;
        color: #667eea;
      }

      h1 {
        margin: 0 0 4px;
        font-size: 22px;
        font-weight: 700;
        color: #1a1a2e;
      }

      .header-sub {
        margin: 0;
        font-size: 14px;
        color: #909399;
      }
    }
  }

  .config-body {
    flex: 1;
    overflow-y: auto;
    padding: 24px 32px;
    display: grid;
    grid-template-columns: 1fr 360px;
    gap: 20px;
    align-items: start;
  }

  .config-card, .history-card {
    border-radius: 12px;
    border: 1px solid #e4e7ed;

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      font-size: 15px;
    }
  }

  .scope-selector {
    display: flex;
    gap: 16px;

    .scope-card {
      flex: 1;
      max-width: 160px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 20px 16px;
      border: 2px solid #e4e7ed;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;
      text-align: center;

      &:hover {
        border-color: #667eea;
        background: #f5f7ff;
      }

      &.active {
        border-color: #667eea;
        background: #f0f2ff;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
      }

      .scope-title {
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }

      .scope-sub {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .difficulty-group {
    :deep(.el-radio-button__inner) {
      display: flex;
      align-items: center;
      gap: 6px;
    }
  }

  .count-row {
    display: flex;
    align-items: center;
    gap: 20px;

    .count-label {
      font-size: 14px;
      color: #606266;
      white-space: nowrap;
      min-width: 100px;
    }
  }

  .history-list {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .history-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 14px;
      border-radius: 8px;
      background: #f9fafb;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #f0f2f5;
      }

      .history-info {
        flex: 1;
        min-width: 0;

        .history-title {
          font-size: 13px;
          font-weight: 500;
          color: #303133;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .history-meta {
          display: flex;
          gap: 12px;
          margin-top: 4px;
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .history-loading {
    padding: 8px 0;
  }

  .config-footer {
    background: #fff;
    padding: 16px 32px;
    border-top: 1px solid #e4e7ed;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    flex-shrink: 0;
  }
}
</style>
