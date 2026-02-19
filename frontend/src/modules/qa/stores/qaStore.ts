import { defineStore } from 'pinia'
import { ref } from 'vue'
import { qaApi } from '../api/qa'
import type { QARecord } from '../types'

export const useQAStore = defineStore('qa', () => {
  // 状态
  const currentDocumentId = ref<number | null>(null)
  const messages = ref<QARecord[]>([])
  const loading = ref(false)
  const relatedQuestions = ref<string[]>([])
  // 本地追踪待显示的用户问题（在AI回答前显示）
  const pendingQuestion = ref<string>('')

  // 方法
  async function askQuestion(documentId: number | null, question: string) {
    loading.value = true
    pendingQuestion.value = question
    try {
      const response = await qaApi.ask({
        document_id: documentId || undefined,
        question
      })
      
      messages.value.push(response)
      pendingQuestion.value = ''
      
      // 获取相关问题（仅单文档模式）
      if (documentId) {
        await fetchRelatedQuestions(documentId, question)
      }
      
      return response
    } finally {
      loading.value = false
      pendingQuestion.value = ''
    }
  }

  async function fetchHistory(documentId: number | null) {
    loading.value = true
    try {
      const response = await qaApi.getHistory({
        document_id: documentId || undefined,
        page: 1,
        page_size: 50
      })
      
      messages.value = response.records
      currentDocumentId.value = documentId
    } finally {
      loading.value = false
    }
  }

  async function submitFeedback(qaId: number, helpful: boolean) {
    await qaApi.submitFeedback(qaId, { helpful })
    
    // 更新本地记录
    const record = messages.value.find(m => m.id === qaId)
    if (record) {
      record.helpful = helpful
    }
  }

  async function fetchRelatedQuestions(documentId: number, question: string) {
    try {
      const response = await qaApi.getRelatedQuestions({
        document_id: documentId,
        question,
        count: 3
      })
      relatedQuestions.value = response.questions
    } catch (error) {
      console.error('获取相关问题失败:', error)
      relatedQuestions.value = []
    }
  }

  function clearMessages() {
    messages.value = []
    relatedQuestions.value = []
    currentDocumentId.value = null
  }

  return {
    currentDocumentId,
    messages,
    loading,
    relatedQuestions,
    pendingQuestion,
    askQuestion,
    fetchHistory,
    submitFeedback,
    fetchRelatedQuestions,
    clearMessages
  }
})



