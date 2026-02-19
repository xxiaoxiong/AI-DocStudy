<template>
  <div class="document-detail" v-loading="store.loading">
    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <div class="doc-title">
        <el-icon><Document /></el-icon>
        <h1>{{ store.currentDocument?.title || '文档详情' }}</h1>
        <el-tag v-if="store.currentDocument" :type="getStatusType(store.currentDocument.status)" size="large">
          {{ getStatusText(store.currentDocument.status) }}
        </el-tag>
      </div>
      <div class="actions">
        <el-button type="primary" @click="showQAModeDialog = true" :disabled="store.currentDocument?.status !== 'completed'">
          <el-icon><ChatDotRound /></el-icon>
          智能问答
        </el-button>
        <el-button type="success" @click="showExamModeDialog = true" :disabled="store.currentDocument?.status !== 'completed'">
          <el-icon><Edit /></el-icon>
          生成考题
        </el-button>
        <el-button @click="viewProcessDetail">
          <el-icon><DataAnalysis /></el-icon>
          处理详情
        </el-button>
        <el-dropdown @command="handleMoreAction">
          <el-button>
            更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="edit">
                <el-icon><Edit /></el-icon>
                编辑信息
              </el-dropdown-item>
              <el-dropdown-item command="log">
                <el-icon><Tickets /></el-icon>
                处理日志
              </el-dropdown-item>
              <el-dropdown-item command="download" divided>
                <el-icon><Download /></el-icon>
                下载文档
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div v-if="store.currentDocument" class="content-wrapper">
      <!-- 左侧导航 -->
      <div class="left-sidebar">
        <!-- 文档大纲 -->
        <div class="outline-section">
          <div class="section-title">
            <el-icon><List /></el-icon>
            <span>文档大纲</span>
          </div>
          <el-tree
            v-if="store.currentDocument.sections?.length"
            :data="treeData"
            :props="{ label: 'title', children: 'children' }"
            default-expand-all
            node-key="id"
            highlight-current
            @node-click="handleOutlineClick"
            class="outline-tree"
          >
            <template #default="{ data }">
              <span class="tree-node-label">{{ data.title }}</span>
            </template>
          </el-tree>
          <el-empty v-else description="暂无章节信息" :image-size="60" />
        </div>
      </div>

      <!-- 右侧主内容 -->
      <div class="main-content" ref="mainContentRef">
        <!-- 处理中/失败状态 -->

        <el-card v-if="store.currentDocument.status === 'processing'" class="status-card processing-card">
        <el-result icon="info" title="文档处理中">
          <template #sub-title>
            <div class="processing-info">
              <el-icon class="is-loading"><Loading /></el-icon>
              <p>AI正在分析文档内容，请稍候...</p>
              <p class="tip">这可能需要几分钟时间，您可以先浏览其他内容</p>
            </div>
          </template>
          <template #extra>
            <el-button type="primary" @click="refreshStatus">刷新状态</el-button>
          </template>
        </el-result>
      </el-card>

        <el-card v-else-if="store.currentDocument.status === 'failed'" class="status-card failed-card">
        <el-result icon="error" title="文档处理失败">
          <template #sub-title>
            <p>文档分析过程中出现错误，请重新上传或联系管理员</p>
          </template>
          <template #extra>
            <el-button type="primary" @click="goBack">返回列表</el-button>
          </template>
        </el-result>
      </el-card>

        <!-- AI分析内容 -->
        <template v-else>
          <!-- 一句话总结 -->
          <div v-if="store.currentDocument.one_sentence_summary" class="summary-banner">
            <el-icon class="quote-icon"><ChatDotRound /></el-icon>
            <div class="summary-content">
              <div class="summary-label">AI一句话总结</div>
              <div class="summary-text">{{ store.currentDocument.one_sentence_summary }}</div>
            </div>
          </div>

          <!-- 文档元信息卡片 -->
          <el-card class="meta-card" shadow="never">
            <div class="meta-grid">
              <div class="meta-item" v-if="store.currentDocument.document_type">
                <div class="meta-label">文档类型</div>
                <div class="meta-value">
                  <el-icon><Document /></el-icon>
                  {{ store.currentDocument.document_type }}
                </div>
              </div>
              <div class="meta-item" v-if="store.currentDocument.difficulty_level">
                <div class="meta-label">难度等级</div>
                <div class="meta-value" :class="'difficulty-' + getDifficultyClass(store.currentDocument.difficulty_level)">
                  <el-icon><TrendCharts /></el-icon>
                  {{ store.currentDocument.difficulty_level }}
                </div>
              </div>
              <div class="meta-item" v-if="store.currentDocument.estimated_reading_time">
                <div class="meta-label">预计阅读</div>
                <div class="meta-value">
                  <el-icon><Clock /></el-icon>
                  {{ store.currentDocument.estimated_reading_time }}
                </div>
              </div>
              <div class="meta-item" v-if="store.currentDocument.target_audience">
                <div class="meta-label">目标读者</div>
                <div class="meta-value">
                  <el-icon><User /></el-icon>
                  {{ store.currentDocument.target_audience }}
                </div>
              </div>
              <div class="meta-item">
                <div class="meta-label">文件大小</div>
                <div class="meta-value">
                  <el-icon><Folder /></el-icon>
                  {{ formatFileSize(store.currentDocument.file_size) }}
                </div>
              </div>
              <div class="meta-item">
                <div class="meta-label">上传时间</div>
                <div class="meta-value">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(store.currentDocument.uploaded_at) }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- 标签页内容 -->
          <el-tabs v-model="activeTab" class="content-tabs">
            <!-- 文档摘要 -->
            <el-tab-pane label="文档摘要" name="summary">
              <div id="summary" class="tab-content">
                <div v-if="store.currentDocument.summary" class="summary-section">
                  <p class="summary-text">{{ store.currentDocument.summary }}</p>
                </div>
                <el-empty v-else description="暂无摘要信息" />
              </div>
            </el-tab-pane>

            <!-- 核心要点 -->
            <el-tab-pane name="keypoints">
              <template #label>
                <span><el-icon><Star /></el-icon> 核心要点</span>
              </template>
              <div id="keypoints" class="tab-content">
                <ul v-if="store.currentDocument.key_points?.length" class="key-points-list">
                  <li v-for="(point, index) in store.currentDocument.key_points" :key="index" class="point-item">
                    <div class="point-number">{{ index + 1 }}</div>
                    <div class="point-text">{{ point }}</div>
                  </li>
                </ul>
                <el-empty v-else description="暂无核心要点" />
              </div>
            </el-tab-pane>

            <!-- 关键概念 -->
            <el-tab-pane name="concepts">
              <template #label>
                <span><el-icon><Collection /></el-icon> 关键概念</span>
              </template>
              <div id="concepts" class="tab-content">
                <div v-if="store.currentDocument.key_concepts?.length" class="concepts-grid">
                  <div 
                    v-for="(concept, index) in store.currentDocument.key_concepts" 
                    :key="index"
                    class="concept-card"
                  >
                    <div class="concept-term">{{ concept.term }}</div>
                    <div class="concept-definition">{{ concept.definition }}</div>
                  </div>
                </div>
                <el-empty v-else description="暂无关键概念" />
              </div>
            </el-tab-pane>

            <!-- 学习建议 -->
            <el-tab-pane name="suggestions">
              <template #label>
                <span><el-icon><Promotion /></el-icon> 学习建议</span>
              </template>
              <div id="suggestions" class="tab-content">
                <el-timeline v-if="store.currentDocument.learning_suggestions?.length">
                  <el-timeline-item
                    v-for="(suggestion, index) in store.currentDocument.learning_suggestions"
                    :key="index"
                    :icon="Checked"
                    type="success"
                    :hollow="true"
                  >
                    {{ suggestion }}
                  </el-timeline-item>
                </el-timeline>
                <el-empty v-else description="暂无学习建议" />
              </div>
            </el-tab-pane>

            <!-- 常见问题 -->
            <el-tab-pane name="questions">
              <template #label>
                <span><el-icon><QuestionFilled /></el-icon> 常见问题</span>
              </template>
              <div id="questions" class="tab-content">
                <div v-if="store.currentDocument.common_questions?.length" class="questions-list">
                  <div
                    v-for="(question, index) in store.currentDocument.common_questions"
                    :key="index"
                    class="question-item"
                  >
                    <div class="question-text">
                      <el-icon class="q-icon"><QuestionFilled /></el-icon>
                      {{ question }}
                    </div>
                    <el-button type="primary" size="small" @click="askQuestion(question)">
                      <el-icon><ChatDotRound /></el-icon>
                      向AI提问
                    </el-button>
                  </div>
                </div>
                <el-empty v-else description="暂无常见问题" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </template>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑文档" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="文档标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 处理日志对话框 -->
    <process-progress-dialog
      v-model="showProcessDialog"
      :document-id="documentId"
    />

    <!-- 处理详情对话框 -->
    <process-detail-dialog
      v-model="showDetailDialog"
      :document-id="documentId"
    />

    <!-- 处理日志对话框 -->
    <process-log-dialog
      v-model="showLogDialog"
      :document-id="documentId"
    />

    <!-- 智能问答模式选择 -->
    <el-dialog
      v-model="showQAModeDialog"
      title="智能问答"
      width="420px"
      :close-on-click-modal="true"
    >
      <div class="mode-dialog-body">
        <p class="mode-desc">请选择问答范围：</p>
        <div class="mode-cards">
          <div class="mode-card" @click="goToQA('doc')">
            <el-icon :size="32" color="#667eea"><Document /></el-icon>
            <div class="mode-title">当前文档</div>
            <div class="mode-sub">仅基于《{{ store.currentDocument?.title }}》回答</div>
          </div>
          <div class="mode-card" @click="goToQA('all')">
            <el-icon :size="32" color="#67c23a"><Collection /></el-icon>
            <div class="mode-title">全库检索</div>
            <div class="mode-sub">跨所有已导入文档检索回答</div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 生成考题模式选择 -->
    <el-dialog
      v-model="showExamModeDialog"
      title="生成考题"
      width="420px"
      :close-on-click-modal="true"
    >
      <div class="mode-dialog-body">
        <p class="mode-desc">请选择出题范围：</p>
        <div class="mode-cards">
          <div class="mode-card" @click="goToExam('doc')">
            <el-icon :size="32" color="#667eea"><Document /></el-icon>
            <div class="mode-title">当前文档</div>
            <div class="mode-sub">仅基于《{{ store.currentDocument?.title }}》出题</div>
          </div>
          <div class="mode-card" @click="goToExam('all')">
            <el-icon :size="32" color="#67c23a"><Collection /></el-icon>
            <div class="mode-title">全库出题</div>
            <div class="mode-sub">跨所有已导入文档综合出题</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ChatDotRound, Document, TrendCharts, Clock, User,
  Reading, Star, Collection, Promotion, QuestionFilled, Edit, Loading,
  List, Checked, Tickets, DataAnalysis, ArrowDown, Download,
  Folder, Calendar
} from '@element-plus/icons-vue'
import { useDocumentStore } from '../stores/documentStore'
import { useDocument } from '../composables/useDocument'
import ProcessProgressDialog from '../components/ProcessProgressDialog.vue'
import ProcessDetailDialog from '../components/ProcessDetailDialog.vue'
import ProcessLogDialog from '../components/ProcessLogDialog.vue'

const route = useRoute()
const router = useRouter()
const store = useDocumentStore()
const { handleUpdate } = useDocument()

const showEditDialog = ref(false)
const showProcessDialog = ref(false)
const showDetailDialog = ref(false)
const showLogDialog = ref(false)
const showQAModeDialog = ref(false)
const showExamModeDialog = ref(false)
const activeTab = ref('summary')
const mainContentRef = ref<HTMLElement>()
const editForm = ref({
  title: ''
})

const documentId = computed(() => Number(route.params.id))

const goToQA = (mode: 'doc' | 'all') => {
  showQAModeDialog.value = false
  if (mode === 'doc') {
    router.push(`/qa/${documentId.value}`)
  } else {
    router.push('/qa')
  }
}

const goToExam = (mode: 'doc' | 'all') => {
  showExamModeDialog.value = false
  if (mode === 'doc') {
    router.push({
      path: `/exam/doc/${documentId.value}`,
      query: { title: store.currentDocument?.title }
    })
  } else {
    router.push('/exam')
  }
}

const askQuestion = (question: string) => {
  router.push({
    path: `/qa/${documentId.value}`,
    query: { q: question }
  })
}

const treeData = computed(() => {
  if (!store.currentDocument?.sections) return []
  
  const sections = store.currentDocument.sections
  const map = new Map<number, any>()
  const roots: any[] = []

  sections.forEach(section => {
    map.set(section.id, { ...section, children: [] })
  })

  sections.forEach(section => {
    const node = map.get(section.id)
    if (section.parent_id) {
      const parent = map.get(section.parent_id)
      if (parent) {
        parent.children.push(node)
      }
    } else {
      roots.push(node)
    }
  })

  return roots
})

const getDifficultyClass = (level: string) => {
  const map: Record<string, string> = {
    '入门': 'easy',
    '中级': 'medium',
    '高级': 'hard'
  }
  return map[level] || 'easy'
}

const handleMoreAction = (command: string) => {
  switch (command) {
    case 'edit':
      showEditDialog.value = true
      break
    case 'log':
      viewProcessLog()
      break
    case 'download':
      // TODO: 实现下载功能
      break
  }
}

const viewProcessLog = () => {
  showLogDialog.value = true
}

const viewProcessDetail = () => {
  showDetailDialog.value = true
}

const scrollToSection = (section: string) => {
  activeTab.value = section
  nextTick(() => {
    const element = document.getElementById(section)
    if (element && mainContentRef.value) {
      mainContentRef.value.scrollTo({
        top: element.offsetTop - 20,
        behavior: 'smooth'
      })
    }
  })
}

const handleOutlineClick = (data: any) => {
  // 点击大纲节点，滚动到对应位置
  if (mainContentRef.value) {
    // 切换到摘要标签页（因为章节内容在摘要中）
    activeTab.value = 'summary'
    nextTick(() => {
      // 平滑滚动到顶部，显示摘要内容
      mainContentRef.value?.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    })
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

const formatFileSize = (size?: number) => {
  if (!size) return '-'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
  return `${(size / 1024 / 1024).toFixed(2)} MB`
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const goBack = () => {
  router.push('/documents')
}

const refreshStatus = async () => {
  await store.fetchDocumentDetail(documentId.value)
}

const handleSave = async () => {
  await handleUpdate(documentId.value, editForm.value)
  showEditDialog.value = false
  await store.fetchDocumentDetail(documentId.value)
}

onMounted(async () => {
  await store.fetchDocumentDetail(documentId.value)
  if (store.currentDocument) {
    editForm.value = {
      title: store.currentDocument.title
    }
  }
})
</script>

<style scoped lang="scss">
.document-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;

  // 顶部操作栏
  .top-bar {
    background: #fff;
    padding: 16px 24px;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;

    .doc-title {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;

      .el-icon {
        font-size: 24px;
        color: #667eea;
      }

      h1 {
        margin: 0;
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
    }

    .actions {
      display: flex;
      gap: 12px;
    }
  }

  // 内容包裹器
  .content-wrapper {
    flex: 1;
    display: flex;
    overflow: hidden;
    gap: 16px;
    padding: 16px;
  }

  // 左侧导航
  .left-sidebar {
    width: 280px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      padding: 12px 16px;
      background: #f5f7fa;
      border-radius: 6px;
    }

    .outline-section {
      background: #fff;
      border-radius: 8px;
      padding: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      min-height: 0;

      .outline-tree {
        margin-top: 8px;
        border: none;
        background: transparent;
        overflow-y: auto;
        flex: 1;

        :deep(.el-tree-node__content) {
          padding: 8px 10px;
          border-radius: 4px;
          margin: 2px 0;
          cursor: pointer;

          &:hover {
            background: #f5f7fa;
          }
        }

        :deep(.is-current > .el-tree-node__content) {
          background: #ecf5ff;
          color: #409eff;
        }

        .tree-node-label {
          font-size: 13px;
          line-height: 1.5;
        }
      }
    }
  }

  // 右侧主内容
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow: hidden;
  }

  // 状态卡片
  .status-card {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  // 一句话总结横幅
  .summary-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 12px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    flex-shrink: 0;

    .quote-icon {
      font-size: 32px;
      color: rgba(255, 255, 255, 0.9);
      flex-shrink: 0;
    }

    .summary-content {
      flex: 1;

      .summary-label {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
      }

      .summary-text {
        font-size: 16px;
        line-height: 1.6;
        color: #fff;
        font-weight: 500;
      }
    }
  }

  // 元信息卡片
  .meta-card {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    flex-shrink: 0;

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;

      .meta-item {
        .meta-label {
          font-size: 12px;
          color: #909399;
          margin-bottom: 6px;
        }

        .meta-value {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          font-weight: 500;
          color: #303133;
          line-height: 1.4;
          word-break: break-word;

          .el-icon {
            font-size: 16px;
            color: #909399;
            flex-shrink: 0;
          }

          &.difficulty-easy {
            color: #67c23a;
            .el-icon { color: #67c23a; }
          }

          &.difficulty-medium {
            color: #e6a23c;
            .el-icon { color: #e6a23c; }
          }

          &.difficulty-hard {
            color: #f56c6c;
            .el-icon { color: #f56c6c; }
          }
        }
      }
    }
  }

  // 标签页
  .content-tabs {
    background: #fff;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;

    :deep(.el-tabs__header) {
      margin-bottom: 16px;
      flex-shrink: 0;
    }

    :deep(.el-tabs__item) {
      font-size: 14px;
      padding: 0 20px;
      height: 40px;
      line-height: 40px;
    }

    :deep(.el-tabs__content) {
      flex: 1;
      overflow-y: auto;
    }

    .tab-content {
      padding: 8px 0;
    }

    // 摘要
    .summary-section {
      .summary-text {
        font-size: 15px;
        line-height: 1.8;
        color: #606266;
        text-align: justify;
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;
        border-left: 4px solid #667eea;
      }
    }

    // 核心要点
    .key-points-list {
      list-style: none;
      padding: 0;
      margin: 0;

      .point-item {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        padding: 16px;
        margin-bottom: 12px;
        background: #f9fafb;
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          background: #f0f2f5;
          transform: translateX(4px);
        }

        .point-number {
          width: 32px;
          height: 32px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #fff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          flex-shrink: 0;
        }

        .point-text {
          flex: 1;
          font-size: 14px;
          line-height: 1.6;
          color: #303133;
          padding-top: 4px;
        }
      }
    }

    // 关键概念
    .concepts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;

      .concept-card {
        padding: 20px;
        background: #f9fafb;
        border-radius: 8px;
        border: 2px solid transparent;
        transition: all 0.3s;

        &:hover {
          border-color: #667eea;
          background: #fff;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        }

        .concept-term {
          font-size: 16px;
          font-weight: 600;
          color: #667eea;
          margin-bottom: 12px;
        }

        .concept-definition {
          font-size: 14px;
          line-height: 1.6;
          color: #606266;
        }
      }
    }

    // 常见问题
    .questions-list {
      .question-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        margin-bottom: 12px;
        background: #f9fafb;
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          background: #f0f2f5;
        }

        .question-text {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 14px;
          color: #303133;

          .q-icon {
            color: #667eea;
            font-size: 18px;
          }
        }
      }
    }
  }

  // 处理中/失败状态
  .processing-card, .failed-card {
    .processing-info {
      text-align: center;
      padding: 40px 20px;

      .el-icon {
        font-size: 48px;
        margin-bottom: 16px;
      }

      p {
        margin: 8px 0;
        color: #606266;
        font-size: 14px;
      }

      .tip {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

// 模式选择对话框
.mode-dialog-body {
  padding: 8px 0 16px;

  .mode-desc {
    font-size: 14px;
    color: #606266;
    margin: 0 0 16px;
  }

  .mode-cards {
    display: flex;
    gap: 16px;

    .mode-card {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      padding: 24px 16px;
      border: 2px solid #e4e7ed;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.25s;
      text-align: center;

      &:hover {
        border-color: #667eea;
        background: #f5f7ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
      }

      .mode-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }

      .mode-sub {
        font-size: 12px;
        color: #909399;
        line-height: 1.5;
      }
    }
  }
}
</style>
