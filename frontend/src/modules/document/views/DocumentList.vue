<template>
  <div class="document-list">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文档标题..."
          clearable
          style="width: 300px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-radio-group v-model="statusFilter" @change="handleFilterChange" size="default">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="completed">已完成</el-radio-button>
          <el-radio-button label="processing">处理中</el-radio-button>
          <el-radio-button label="failed">失败</el-radio-button>
        </el-radio-group>
      </div>

      <div class="toolbar-right">
        <el-button @click="loadDocuments">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><upload-filled /></el-icon>
          上传文档
        </el-button>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="content">
      <el-table 
        :data="store.documents" 
        v-loading="store.loading"
        style="width: 100%"
        :row-class-name="getRowClassName"
        @row-click="handleRowClick"
        stripe
      >
        <el-table-column prop="title" label="文档标题" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="title-cell">
              <el-icon class="doc-icon"><Document /></el-icon>
              <span class="title-text">{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="file_type" label="文件类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getFileTypeColor(row.file_type)">
              {{ row.file_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="file_size" label="文件大小" width="120" align="center">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark">
              <el-icon v-if="row.status === 'processing'" class="is-loading"><Loading /></el-icon>
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="uploaded_at" label="上传时间" width="180" align="center">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              {{ formatDate(row.uploaded_at) }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                v-if="row.status === 'processing'"
                size="small"
                type="primary"
                @click.stop="viewProgress(row.id)"
              >
                <el-icon><View /></el-icon>
                查看进度
              </el-button>
              <template v-else>
                <el-button 
                  size="small" 
                  type="primary"
                  @click.stop="viewDetail(row.id)"
                  :disabled="row.status !== 'completed'"
                >
                  <el-icon><View /></el-icon>
                  查看详情
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click.stop="handleDeleteClick(row)"
                  :icon="Delete"
                />
              </template>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="store.currentPage"
          v-model:page-size="store.pageSize"
          :total="store.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
          background
        />
      </div>
    </div>

    <upload-dialog 
      v-model="showUploadDialog" 
      @success="handleUploadSuccess"
    />

    <process-progress-dialog
      v-model="showProgressDialog"
      :document-id="selectedDocumentId"
      @completed="handleProcessCompleted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { 
  UploadFilled, View, Delete, Search, Refresh, 
  Document, Clock, Loading 
} from '@element-plus/icons-vue'
import { useDocumentStore } from '../stores/documentStore'
import { useDocument } from '../composables/useDocument'
import UploadDialog from '../components/UploadDialog.vue'
import ProcessProgressDialog from '../components/ProcessProgressDialog.vue'
import type { Document as DocumentType } from '../types'

const router = useRouter()
const store = useDocumentStore()
const { handleDelete } = useDocument()

const showUploadDialog = ref(false)
const showProgressDialog = ref(false)
const selectedDocumentId = ref<number>(0)
const statusFilter = ref('')
const searchKeyword = ref('')

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
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getFileTypeColor = (fileType: string) => {
  const map: Record<string, string> = {
    pdf: 'danger',
    docx: 'primary',
    doc: 'primary',
    txt: 'info',
    md: 'success'
  }
  return map[fileType.toLowerCase()] || 'info'
}

const getRowClassName = ({ row }: { row: DocumentType }) => {
  if (row.status === 'completed') return 'row-completed'
  if (row.status === 'processing') return 'row-processing'
  if (row.status === 'failed') return 'row-failed'
  return ''
}

const handleRowClick = (row: DocumentType) => {
  if (row.status === 'completed') {
    viewDetail(row.id)
  } else if (row.status === 'processing') {
    viewProgress(row.id)
  }
}

const handleSearch = () => {
  store.setPage(1)
  loadDocuments()
}

const viewDetail = (id: number) => {
  router.push(`/document/${id}`)
}

const viewProgress = (id: number) => {
  selectedDocumentId.value = id
  showProgressDialog.value = true
}

const handleDeleteClick = async (row: DocumentType) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档"${row.title}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    await handleDelete(row.id)
    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    // 用户取消或删除失败
  }
}

const handleFilterChange = () => {
  store.setPage(1)
  loadDocuments()
}

const handlePageChange = () => {
  loadDocuments()
}

const handleSizeChange = () => {
  store.setPage(1)
  loadDocuments()
}

const handleUploadSuccess = (documentId: number) => {
  showUploadDialog.value = false
  store.setPage(1)
  loadDocuments()
  
  // 自动打开进度查看对话框
  ElMessage.success('文档上传成功，正在处理中...')
  setTimeout(() => {
    selectedDocumentId.value = documentId
    showProgressDialog.value = true
  }, 500)
}

const handleProcessCompleted = () => {
  ElMessage.success('文档处理完成！')
  loadDocuments()
}

const loadDocuments = () => {
  const params: any = {}
  if (statusFilter.value) {
    params.status = statusFilter.value
  }
  if (searchKeyword.value.trim()) {
    params.keyword = searchKeyword.value.trim()
  }
  store.fetchDocuments(params)
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped lang="scss">
.document-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;

  // 工具栏
  .toolbar {
    background: #fff;
    padding: 16px 24px;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
    gap: 16px;

    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 16px;
      flex: 1;
    }

    .toolbar-right {
      display: flex;
      gap: 12px;
    }
  }

  // 内容区
  .content {
    flex: 1;
    padding: 16px 24px 24px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 16px;

    :deep(.el-table) {
      flex: 1;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

      .el-table__header {
        th {
          background: #f5f7fa;
          color: #606266;
          font-weight: 600;
        }
      }

      .el-table__body {
        tr {
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            background: #f5f7fa;
          }

          &.row-completed {
            .title-cell {
              .doc-icon {
                color: #67c23a;
              }
            }
          }

          &.row-processing {
            .title-cell {
              .doc-icon {
                color: #e6a23c;
              }
            }
          }

          &.row-failed {
            .title-cell {
              .doc-icon {
                color: #f56c6c;
              }
            }
          }
        }
      }
    }
  }

  // 标题单元格
  .title-cell {
    display: flex;
    align-items: center;
    gap: 10px;

    .doc-icon {
      font-size: 18px;
      color: #909399;
      flex-shrink: 0;
    }

    .title-text {
      font-weight: 500;
      color: #303133;
    }
  }

  // 时间单元格
  .time-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    color: #606266;
    font-size: 13px;

    .el-icon {
      color: #909399;
    }
  }

  // 操作按钮
  .action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
  }

  // 分页
  .pagination {
    display: flex;
    justify-content: flex-end;
    padding: 16px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
}
</style>
