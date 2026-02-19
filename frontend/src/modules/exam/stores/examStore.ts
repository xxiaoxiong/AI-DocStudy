import { defineStore } from 'pinia'
import { ref } from 'vue'
import { examApi } from '../api/exam'
import type { ExamConfig, ExamSession, ExamResult, ExamHistoryItem, AnswerSubmitItem } from '../types'

export const useExamStore = defineStore('exam', () => {
  const loading = ref(false)
  const currentSession = ref<ExamSession | null>(null)
  const currentResult = ref<ExamResult | null>(null)
  const history = ref<ExamHistoryItem[]>([])
  const historyTotal = ref(0)

  async function generateExam(config: ExamConfig): Promise<ExamSession> {
    loading.value = true
    try {
      const session = await examApi.generate(config)
      currentSession.value = session
      currentResult.value = null
      return session
    } finally {
      loading.value = false
    }
  }

  async function submitExam(
    examId: number,
    answers: AnswerSubmitItem[],
    timeSpent: number
  ): Promise<ExamResult> {
    loading.value = true
    try {
      const result = await examApi.submit(examId, answers, timeSpent)
      currentResult.value = result
      return result
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(page = 1, pageSize = 10) {
    loading.value = true
    try {
      const res = await examApi.getHistory(page, pageSize)
      history.value = res.records
      historyTotal.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchResult(examId: number): Promise<ExamResult> {
    const result = await examApi.getResult(examId)
    currentResult.value = result
    return result
  }

  function clearSession() {
    currentSession.value = null
    currentResult.value = null
  }

  return {
    loading,
    currentSession,
    currentResult,
    history,
    historyTotal,
    generateExam,
    submitExam,
    fetchHistory,
    fetchResult,
    clearSession,
  }
})
