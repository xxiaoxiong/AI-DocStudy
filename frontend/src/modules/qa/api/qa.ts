import { request } from '@/shared/utils/request'
import type { QACreate, QARecord, QAListResponse, QAFeedback, RelatedQuestionsResponse } from '../types'

export const qaApi = {
  // 提问
  ask(data: QACreate): Promise<QARecord> {
    return request.post('/api/v1/qa/ask', data)
  },

  // 获取问答历史
  getHistory(params: {
    document_id?: number
    page?: number
    page_size?: number
  }): Promise<QAListResponse> {
    return request.get('/api/v1/qa/history', { params })
  },

  // 提交反馈
  submitFeedback(qaId: number, data: QAFeedback): Promise<{ success: boolean; message: string }> {
    return request.post(`/api/v1/qa/${qaId}/feedback`, data)
  },

  // 获取相关问题
  getRelatedQuestions(params: {
    document_id: number
    question: string
    count?: number
  }): Promise<RelatedQuestionsResponse> {
    return request.get('/api/v1/qa/related-questions', { params })
  }
}



