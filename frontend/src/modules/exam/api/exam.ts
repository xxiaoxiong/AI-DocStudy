import { request } from '@/shared/utils/request'
import type { ExamConfig, ExamSession, ExamResult, ExamHistoryItem, AnswerSubmitItem } from '../types'

export const examApi = {
  generate(config: ExamConfig): Promise<ExamSession> {
    return request.post('/api/v1/exam/generate', {
      document_id: config.document_id || null,
      single_count: config.single_count,
      judge_count: config.judge_count,
      essay_count: config.essay_count,
      difficulty: config.difficulty,
    })
  },

  submit(examId: number, answers: AnswerSubmitItem[], timeSpent: number): Promise<ExamResult> {
    return request.post('/api/v1/exam/submit', {
      exam_id: examId,
      answers,
      time_spent: timeSpent,
    })
  },

  getHistory(page = 1, pageSize = 10): Promise<{ records: ExamHistoryItem[]; total: number }> {
    return request.get('/api/v1/exam/history', { params: { page, page_size: pageSize } })
  },

  getResult(examId: number): Promise<ExamResult> {
    return request.get(`/api/v1/exam/result/${examId}`)
  },
}
