import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { documentApi } from '../api/document'
import type { Document, DocumentDetail } from '../types'

export const useDocumentStore = defineStore('document', () => {
  // 状态
  const documents = ref<Document[]>([])
  const currentDocument = ref<DocumentDetail | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(10)

  // 计算属性
  const completedDocuments = computed(() => 
    documents.value.filter(doc => doc.status === 'completed')
  )

  const processingDocuments = computed(() =>
    documents.value.filter(doc => doc.status === 'processing')
  )

  // 方法
  async function fetchDocuments(params?: any) {
    loading.value = true
    try {
      const response = await documentApi.getList({
        page: currentPage.value,
        page_size: pageSize.value,
        ...params
      })
      documents.value = response.records
      total.value = response.total
    } finally {
      loading.value = false
    }
  }

  async function fetchDocumentDetail(id: number) {
    loading.value = true
    try {
      currentDocument.value = await documentApi.getDetail(id)
    } finally {
      loading.value = false
    }
  }

  async function uploadDocument(file: File, title?: string) {
    const response = await documentApi.upload(file, title)
    await fetchDocuments()
    return response
  }

  async function updateDocument(id: number, data: any) {
    const updated = await documentApi.update(id, data)
    const index = documents.value.findIndex(doc => doc.id === id)
    if (index !== -1) {
      documents.value[index] = updated
    }
    return updated
  }

  async function deleteDocument(id: number) {
    await documentApi.delete(id)
    documents.value = documents.value.filter(doc => doc.id !== id)
    total.value--
  }

  function setPage(page: number) {
    currentPage.value = page
  }

  function setPageSize(size: number) {
    pageSize.value = size
  }

  return {
    documents,
    currentDocument,
    loading,
    total,
    currentPage,
    pageSize,
    completedDocuments,
    processingDocuments,
    fetchDocuments,
    fetchDocumentDetail,
    uploadDocument,
    updateDocument,
    deleteDocument,
    setPage,
    setPageSize
  }
})



