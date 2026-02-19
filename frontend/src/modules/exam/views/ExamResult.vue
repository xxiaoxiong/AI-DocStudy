<template>
  <div class="exam-result" v-loading="store.loading">
    <template v-if="result">
      <!-- 顶部成绩横幅 -->
      <div class="result-banner" :class="result.passed ? 'passed' : 'failed'">
        <div class="banner-left">
          <el-icon :size="56">
            <Trophy v-if="result.passed" />
            <CircleClose v-else />
          </el-icon>
          <div class="banner-text">
            <div class="banner-title">{{ result.passed ? '恭喜通过！' : '未通过，继续加油！' }}</div>
            <div class="banner-sub">{{ result.title }}</div>
            <div v-if="result.document_title" class="banner-doc">
              <el-icon><Document /></el-icon>
              {{ result.document_title }}
            </div>
          </div>
        </div>
        <div class="banner-score">
          <div class="score-big">{{ result.total_score.toFixed(0) }}</div>
          <div class="score-max">/ {{ result.max_score.toFixed(0) }} 分</div>
          <div class="score-percent">{{ result.percentage.toFixed(1) }}%</div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon single"><el-icon><List /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ result.single_correct }}/{{ result.single_total }}</div>
            <div class="stat-label">单选题</div>
          </div>
          <el-progress
            type="circle"
            :percentage="result.single_total ? Math.round(result.single_correct / result.single_total * 100) : 0"
            :width="56"
            :stroke-width="5"
            :color="result.single_correct / result.single_total >= 0.6 ? '#67c23a' : '#f56c6c'"
          />
        </div>
        <div class="stat-card">
          <div class="stat-icon judge"><el-icon><Select /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ result.judge_correct }}/{{ result.judge_total }}</div>
            <div class="stat-label">判断题</div>
          </div>
          <el-progress
            type="circle"
            :percentage="result.judge_total ? Math.round(result.judge_correct / result.judge_total * 100) : 0"
            :width="56"
            :stroke-width="5"
            :color="result.judge_correct / result.judge_total >= 0.6 ? '#67c23a' : '#f56c6c'"
          />
        </div>
        <div class="stat-card">
          <div class="stat-icon essay"><el-icon><EditPen /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ result.essay_score.toFixed(0) }}/{{ result.essay_max.toFixed(0) }}</div>
            <div class="stat-label">简答题</div>
          </div>
          <el-progress
            type="circle"
            :percentage="result.essay_max ? Math.round(result.essay_score / result.essay_max * 100) : 0"
            :width="56"
            :stroke-width="5"
            :color="result.essay_score / result.essay_max >= 0.6 ? '#67c23a' : '#f56c6c'"
          />
        </div>
        <div class="stat-card">
          <div class="stat-icon time"><el-icon><Timer /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ formatTime(result.time_spent) }}</div>
            <div class="stat-label">用时</div>
          </div>
        </div>
      </div>

      <!-- 详细答题情况 -->
      <div class="answers-section">
        <div class="section-title">
          <el-icon><Document /></el-icon>
          详细答题情况
        </div>

        <div class="answers-list">
          <div
            v-for="(ans, idx) in result.answers"
            :key="ans.question_id"
            class="answer-item"
            :class="{ correct: ans.is_correct, wrong: !ans.is_correct }"
          >
            <!-- 题目头部 -->
            <div class="answer-header">
              <span class="answer-index">{{ idx + 1 }}</span>
              <el-tag :type="typeTagType(ans.type)" size="small">{{ typeLabel(ans.type) }}</el-tag>
              <el-tag :type="ans.is_correct ? 'success' : 'danger'" size="small">
                <el-icon>
                  <CircleCheck v-if="ans.is_correct" />
                  <CircleClose v-else />
                </el-icon>
                {{ ans.type === 'essay' ? `${ans.score.toFixed(0)}分` : (ans.is_correct ? '正确' : '错误') }}
              </el-tag>
              <span class="answer-score-text">得 {{ ans.score.toFixed(0) }} 分</span>
            </div>

            <!-- 题干 -->
            <div class="answer-question">{{ ans.content }}</div>

            <!-- 选项（单选题） -->
            <div v-if="ans.type === 'single' && ans.options" class="answer-options">
              <div
                v-for="(text, key) in ans.options"
                :key="key"
                class="answer-option"
                :class="{
                  'user-choice': ans.user_answer === key,
                  'correct-choice': ans.correct_answer === key,
                }"
              >
                <span class="opt-key">{{ key }}</span>
                <span class="opt-text">{{ text }}</span>
                <el-icon v-if="ans.correct_answer === key" color="#67c23a"><CircleCheck /></el-icon>
                <el-icon v-else-if="ans.user_answer === key && !ans.is_correct" color="#f56c6c"><CircleClose /></el-icon>
              </div>
            </div>

            <!-- 判断题答案 -->
            <div v-else-if="ans.type === 'judge'" class="answer-judge">
              <span class="judge-label">您的答案：</span>
              <el-tag :type="ans.is_correct ? 'success' : 'danger'" size="small">
                {{ ans.user_answer || '未作答' }}
              </el-tag>
              <span v-if="!ans.is_correct" class="judge-label" style="margin-left:16px">正确答案：</span>
              <el-tag v-if="!ans.is_correct" type="success" size="small">{{ ans.correct_answer }}</el-tag>
            </div>

            <!-- 简答题 -->
            <div v-else-if="ans.type === 'essay'" class="answer-essay">
              <div class="essay-block user-block">
                <div class="block-label">您的回答</div>
                <div class="block-content">{{ ans.user_answer || '（未作答）' }}</div>
              </div>
              <div class="essay-block ref-block">
                <div class="block-label">参考答案</div>
                <div class="block-content">{{ ans.correct_answer }}</div>
              </div>
              <div v-if="ans.ai_feedback" class="essay-block ai-block">
                <div class="block-label">
                  <el-icon><ChatDotRound /></el-icon>
                  AI点评
                </div>
                <div class="block-content">{{ ans.ai_feedback }}</div>
              </div>
            </div>

            <!-- 解析 -->
            <div v-if="ans.explanation && ans.type !== 'essay'" class="answer-explanation">
              <el-icon><InfoFilled /></el-icon>
              {{ ans.explanation }}
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="result-footer">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="retake">
          <el-icon><Refresh /></el-icon>
          重新出题
        </el-button>
      </div>
    </template>

    <el-empty v-else-if="!store.loading" description="考试结果不存在" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Trophy, CircleClose, CircleCheck, Document, List, Select,
  EditPen, Timer, ChatDotRound, InfoFilled, Refresh
} from '@element-plus/icons-vue'
import { useExamStore } from '../stores/examStore'

const route = useRoute()
const router = useRouter()
const store = useExamStore()

const examId = computed(() => Number(route.params.examId))
const result = computed(() => store.currentResult)

const typeLabel = (type: string) => ({ single: '单选题', judge: '判断题', essay: '简答题' }[type] ?? type)
const typeTagType = (type: string) => ({ single: 'primary', judge: 'warning', essay: 'success' }[type] ?? 'info')

const formatTime = (secs: number) => {
  if (!secs) return '-'
  const m = Math.floor(secs / 60)
  const s = secs % 60
  return m > 0 ? `${m}分${s}秒` : `${s}秒`
}

const goBack = () => router.push('/exam')
const retake = () => router.push('/exam')

onMounted(async () => {
  if (!store.currentResult || store.currentResult.exam_id !== examId.value) {
    await store.fetchResult(examId.value)
  }
})
</script>

<style scoped lang="scss">
.exam-result {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  overflow-y: auto;

  .result-banner {
    padding: 28px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;

    &.passed {
      background: linear-gradient(135deg, #43a047 0%, #1de9b6 100%);
      color: #fff;
    }

    &.failed {
      background: linear-gradient(135deg, #e53935 0%, #fb8c00 100%);
      color: #fff;
    }

    .banner-left {
      display: flex;
      align-items: center;
      gap: 20px;

      .banner-text {
        .banner-title {
          font-size: 26px;
          font-weight: 700;
          margin-bottom: 6px;
        }

        .banner-sub {
          font-size: 15px;
          opacity: 0.9;
          margin-bottom: 4px;
        }

        .banner-doc {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          opacity: 0.8;
        }
      }
    }

    .banner-score {
      text-align: center;

      .score-big {
        font-size: 64px;
        font-weight: 800;
        line-height: 1;
      }

      .score-max {
        font-size: 16px;
        opacity: 0.8;
        margin: 4px 0;
      }

      .score-percent {
        font-size: 20px;
        font-weight: 600;
        opacity: 0.9;
      }
    }
  }

  .stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 20px 32px 0;
    flex-shrink: 0;

    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 14px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

      .stat-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;

        &.single { background: #ecf5ff; color: #409eff; }
        &.judge  { background: #fdf6ec; color: #e6a23c; }
        &.essay  { background: #f0f9eb; color: #67c23a; }
        &.time   { background: #f5f0ff; color: #667eea; }
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 20px;
          font-weight: 700;
          color: #303133;
        }

        .stat-label {
          font-size: 13px;
          color: #909399;
          margin-top: 2px;
        }
      }
    }
  }

  .answers-section {
    padding: 20px 32px 100px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 16px;
    }

    .answers-list {
      display: flex;
      flex-direction: column;
      gap: 14px;

      .answer-item {
        background: #fff;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #e4e7ed;

        &.correct { border-left-color: #67c23a; }
        &.wrong   { border-left-color: #f56c6c; }

        .answer-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 14px;

          .answer-index {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #f0f2f5;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: 600;
            color: #606266;
            flex-shrink: 0;
          }

          .answer-score-text {
            margin-left: auto;
            font-size: 13px;
            color: #606266;
          }
        }

        .answer-question {
          font-size: 15px;
          font-weight: 500;
          color: #1a1a2e;
          line-height: 1.7;
          margin-bottom: 16px;
          padding: 12px 16px;
          background: #f9fafb;
          border-radius: 8px;
        }

        .answer-options {
          display: flex;
          flex-direction: column;
          gap: 8px;

          .answer-option {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 14px;
            border-radius: 8px;
            background: #f9fafb;
            font-size: 14px;

            &.correct-choice {
              background: #f0f9eb;
              border: 1px solid #b3e19d;
            }

            &.user-choice:not(.correct-choice) {
              background: #fef0f0;
              border: 1px solid #fbc4c4;
            }

            .opt-key {
              width: 24px;
              height: 24px;
              border-radius: 50%;
              background: #e4e7ed;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 12px;
              font-weight: 700;
              flex-shrink: 0;
            }

            .opt-text { flex: 1; color: #303133; }
          }
        }

        .answer-judge {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #606266;
        }

        .answer-essay {
          display: flex;
          flex-direction: column;
          gap: 10px;

          .essay-block {
            border-radius: 8px;
            padding: 12px 16px;

            &.user-block  { background: #f5f7fa; }
            &.ref-block   { background: #f0f9eb; }
            &.ai-block    { background: #f5f0ff; }

            .block-label {
              display: flex;
              align-items: center;
              gap: 6px;
              font-size: 12px;
              font-weight: 600;
              color: #606266;
              margin-bottom: 6px;
              text-transform: uppercase;
              letter-spacing: 0.5px;
            }

            .block-content {
              font-size: 14px;
              line-height: 1.7;
              color: #303133;
              white-space: pre-wrap;
            }
          }
        }

        .answer-explanation {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          margin-top: 12px;
          padding: 10px 14px;
          background: #fdf6ec;
          border-radius: 8px;
          font-size: 13px;
          color: #e6a23c;
          line-height: 1.6;

          .el-icon { flex-shrink: 0; margin-top: 2px; }
        }
      }
    }
  }

  .result-footer {
    position: fixed;
    bottom: 0;
    left: 200px;
    right: 0;
    background: #fff;
    padding: 14px 32px;
    border-top: 1px solid #e4e7ed;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    z-index: 10;
  }
}
</style>
