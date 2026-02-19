export interface QASource {
  chunk_id: string
  content: string
  metadata: Record<string, any>
  relevance_score: number
}

export interface QARecord {
  id: number
  document_id: number
  question: string
  answer: string
  sources: QASource[]
  has_answer: boolean
  helpful?: boolean
  user_id: number
  created_at: string
}

export interface QACreate {
  document_id: number
  question: string
}

export interface QAListResponse {
  records: QARecord[]
  total: number
  page: number
  page_size: number
}

export interface QAFeedback {
  helpful: boolean
}

export interface RelatedQuestionsResponse {
  questions: string[]
}



