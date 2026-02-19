<template>
  <el-dialog
    v-model="visible"
    title="文档处理详情"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
    class="process-detail-dialog"
  >
    <div v-loading="loading" class="detail-container">
      <!-- 概览统计 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-statistic title="章节数量" :value="detail?.sections_count || 0" suffix="个">
            <template #prefix>
              <el-icon><List /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="分块数量" :value="detail?.chunks_count || 0" suffix="块">
            <template #prefix>
              <el-icon><Grid /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="文本总长度" :value="detail?.total_text_length || 0" suffix="字">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="向量数量" :value="detail?.vector_count || 0" suffix="个">
            <template #prefix>
              <el-icon><DataAnalysis /></el-icon>
            </template>
          </el-statistic>
        </el-col>
      </el-row>

      <!-- 标签页 -->
      <el-tabs v-model="activeTab" class="detail-tabs">
        <!-- 章节详情 -->
        <el-tab-pane label="章节详情" name="sections">
          <template #label>
            <span class="tab-label">
              <el-icon><List /></el-icon>
              章节详情 ({{ detail?.sections_count || 0 }})
            </span>
          </template>
          
          <div class="sections-container">
            <el-empty v-if="!detail?.sections?.length" description="暂无章节数据" />
            
            <el-collapse v-else accordion>
              <el-collapse-item
                v-for="section in detail.sections"
                :key="section.id"
                :name="section.id"
              >
                <template #title>
                  <div class="section-title">
                    <el-tag :type="getLevelType(section.level)" size="small">
                      {{ getLevelText(section.level) }}
                    </el-tag>
                    <span class="title-text">{{ section.title }}</span>
                    <el-tag v-if="section.content" type="info" size="small">
                      {{ section.content.length }} 字
                    </el-tag>
                  </div>
                </template>
                
                <div class="section-content">
                  <el-descriptions :column="2" border size="small">
                    <el-descriptions-item label="章节ID">{{ section.id }}</el-descriptions-item>
                    <el-descriptions-item label="排序">{{ section.order_index }}</el-descriptions-item>
                    <el-descriptions-item label="层级">{{ section.level }}</el-descriptions-item>
                    <el-descriptions-item label="父章节ID">
                      {{ section.parent_id || '无' }}
                    </el-descriptions-item>
                  </el-descriptions>
                  
                  <div v-if="section.content" class="content-text">
                    <h4>章节内容：</h4>
                    <pre>{{ section.content }}</pre>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-tab-pane>

        <!-- 分块详情 -->
        <el-tab-pane label="分块详情" name="chunks">
          <template #label>
            <span class="tab-label">
              <el-icon><Grid /></el-icon>
              分块详情 ({{ detail?.chunks_count || 0 }})
            </span>
          </template>
          
          <div class="chunks-container">
            <el-empty v-if="!detail?.chunks?.length" description="暂无分块数据" />
            
            <div v-else class="chunks-list">
              <el-card
                v-for="chunk in detail.chunks"
                :key="chunk.id"
                class="chunk-card"
                shadow="hover"
              >
                <template #header>
                  <div class="chunk-header">
                    <span class="chunk-index">
                      <el-icon><Document /></el-icon>
                      分块 #{{ chunk.chunk_index + 1 }}
                    </span>
                    <div class="chunk-meta">
                      <el-tag size="small" type="info">
                        {{ chunk.content.length }} 字
                      </el-tag>
                      <el-tag v-if="chunk.section_id" size="small" type="success">
                        章节 #{{ chunk.section_id }}
                      </el-tag>
                    </div>
                  </div>
                </template>
                
                <div class="chunk-content">
                  <pre>{{ chunk.content }}</pre>
                </div>
                
                <div class="chunk-footer">
                  <el-text size="small" type="info">
                    Hash: {{ chunk.chunk_hash.substring(0, 16) }}...
                  </el-text>
                  <el-button size="small" text @click="copyText(chunk.content)">
                    <el-icon><CopyDocument /></el-icon>
                    复制
                  </el-button>
                </div>
              </el-card>
            </div>
          </div>
        </el-tab-pane>

        <!-- 向量化信息 -->
        <el-tab-pane label="向量化信息" name="vectors">
          <template #label>
            <span class="tab-label">
              <el-icon><DataAnalysis /></el-icon>
              向量化信息
            </span>
          </template>
          
          <div class="vectors-container">
            <el-result
              v-if="!detail?.has_vectors"
              icon="warning"
              title="未进行向量化"
              sub-title="该文档尚未进行向量化处理"
            />
            
            <div v-else class="vectors-info">
              <el-alert
                type="success"
                title="向量化已完成"
                :description="`已生成 ${detail.vector_count} 个向量，存储在向量数据库中`"
                show-icon
                :closable="false"
              />
              
              <el-descriptions :column="2" border class="vector-stats">
                <el-descriptions-item label="向量数量">
                  {{ detail.vector_count }}
                </el-descriptions-item>
                <el-descriptions-item label="向量维度">
                  1024 (bge-large-zh)
                </el-descriptions-item>
                <el-descriptions-item label="向量数据库">
                  Chroma
                </el-descriptions-item>
                <el-descriptions-item label="Embedding模型">
                  BAAI/bge-large-zh-v1.5
                </el-descriptions-item>
              </el-descriptions>
              
              <div class="vector-usage">
                <h4>向量用途：</h4>
                <ul>
                  <li>✅ 智能问答（RAG）- 语义检索相关文档片段</li>
                  <li>✅ 相似度搜索 - 查找相似内容</li>
                  <li>✅ 文档推荐 - 基于内容相似度推荐</li>
                </ul>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 原始数据 -->
        <el-tab-pane label="原始数据" name="raw">
          <template #label>
            <span class="tab-label">
              <el-icon><Tickets /></el-icon>
              原始数据 (JSON)
            </span>
          </template>
          
          <div class="raw-data-container">
            <el-button type="primary" size="small" @click="copyRawData">
              <el-icon><CopyDocument /></el-icon>
              复制JSON
            </el-button>
            
            <pre class="raw-data">{{ JSON.stringify(detail, null, 2) }}</pre>
          </div>
        </el-tab-pane>
      </el-tabs>
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
import { ref, watch } from 'vue'
import {
  List, Grid, Document, DataAnalysis, Tickets, CopyDocument, Refresh
} from '@element-plus/icons-vue'
import { detailApi, type ProcessDetail } from '../api/detail'
import { ElMessage } from 'element-plus'

interface Props {
  documentId: number
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const loading = ref(false)
const detail = ref<ProcessDetail | null>(null)
const activeTab = ref('sections')

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    fetchDetail()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const getLevelType = (level: number) => {
  const map: Record<number, any> = {
    1: 'primary',
    2: 'success',
    3: 'warning'
  }
  return map[level] || 'info'
}

const getLevelText = (level: number) => {
  const map: Record<number, string> = {
    1: '一级',
    2: '二级',
    3: '三级'
  }
  return map[level] || `${level}级`
}

const fetchDetail = async () => {
  try {
    loading.value = true
    detail.value = await detailApi.getProcessDetail(props.documentId)
  } catch (error) {
    ElMessage.error('获取处理详情失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchDetail()
}

const copyText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const copyRawData = async () => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(detail.value, null, 2))
    ElMessage.success('已复制JSON数据')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped lang="scss">
.process-detail-dialog {
  :deep(.el-dialog__body) {
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
  }
}

.detail-container {
  .stats-row {
    margin-bottom: 24px;
    
    .el-statistic {
      text-align: center;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;
    }
  }

  .detail-tabs {
    .tab-label {
      display: flex;
      align-items: center;
      gap: 6px;
    }
  }

  // 章节样式
  .sections-container {
    .section-title {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;

      .title-text {
        flex: 1;
        font-weight: 500;
      }
    }

    .section-content {
      padding: 16px;

      .content-text {
        margin-top: 16px;

        h4 {
          margin-bottom: 8px;
          color: #303133;
        }

        pre {
          background: #f5f7fa;
          padding: 12px;
          border-radius: 4px;
          white-space: pre-wrap;
          word-wrap: break-word;
          line-height: 1.6;
          color: #606266;
        }
      }
    }
  }

  // 分块样式
  .chunks-container {
    .chunks-list {
      display: grid;
      gap: 16px;

      .chunk-card {
        .chunk-header {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .chunk-index {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
            color: #303133;
          }

          .chunk-meta {
            display: flex;
            gap: 8px;
          }
        }

        .chunk-content {
          pre {
            background: #f5f7fa;
            padding: 12px;
            border-radius: 4px;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.6;
            color: #606266;
            max-height: 300px;
            overflow-y: auto;
          }
        }

        .chunk-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #eee;
        }
      }
    }
  }

  // 向量样式
  .vectors-container {
    .vectors-info {
      .el-alert {
        margin-bottom: 20px;
      }

      .vector-stats {
        margin-bottom: 20px;
      }

      .vector-usage {
        h4 {
          margin-bottom: 12px;
          color: #303133;
        }

        ul {
          padding-left: 20px;

          li {
            line-height: 2;
            color: #606266;
          }
        }
      }
    }
  }

  // 原始数据样式
  .raw-data-container {
    .el-button {
      margin-bottom: 12px;
    }

    .raw-data {
      background: #f5f7fa;
      padding: 16px;
      border-radius: 4px;
      max-height: 500px;
      overflow: auto;
      font-size: 12px;
      line-height: 1.6;
      color: #606266;
    }
  }
}
</style>

