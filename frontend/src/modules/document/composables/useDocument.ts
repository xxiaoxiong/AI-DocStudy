import { ref } from 'vue'
import { useDocumentStore } from '../stores/documentStore'
import { ElMessage } from 'element-plus'

export function useDocument() {
  const store = useDocumentStore()
  const uploading = ref(false)

  const handleUpload = async (file: File, title?: string) => {
    uploading.value = true
    try {
      const response = await store.uploadDocument(file, title)
      ElMessage.success(response.message)
      return response
    } catch (error: any) {
      ElMessage.error(error.message || '文档上传失败')
      throw error
    } finally {
      uploading.value = false
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await store.deleteDocument(id)
      ElMessage.success('删除成功')
    } catch (error: any) {
      ElMessage.error(error.message || '删除失败')
      throw error
    }
  }

  const handleUpdate = async (id: number, data: any) => {
    try {
      await store.updateDocument(id, data)
      ElMessage.success('更新成功')
    } catch (error: any) {
      ElMessage.error(error.message || '更新失败')
      throw error
    }
  }

  return {
    uploading,
    handleUpload,
    handleDelete,
    handleUpdate
  }
}



