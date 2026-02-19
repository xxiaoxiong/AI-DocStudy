export interface KeyConcept {
  term: string
  definition: string
}

export interface Document {
  id: number
  title: string
  file_path: string
  file_type: string
  file_size?: number
  status: 'processing' | 'completed' | 'failed'
  
  // AI分析结果
  one_sentence_summary?: string
  summary?: string
  key_points?: string[]
  key_concepts?: KeyConcept[]
  document_type?: string
  difficulty_level?: string
  target_audience?: string
  learning_suggestions?: string[]
  estimated_reading_time?: string
  common_questions?: string[]
  
  uploaded_by?: number
  uploaded_at: string
  processed_at?: string
}

export interface DocumentSection {
  id: number
  document_id: number
  title: string
  content?: string
  level: number
  parent_id?: number
  order_index: number
}

export interface DocumentDetail extends Document {
  sections: DocumentSection[]
  chunk_count?: number
  qa_count?: number
}

export interface DocumentListResponse {
  records: Document[]
  total: number
  page: number
  page_size: number
}

export interface UploadResponse {
  document_id: number
  status: string
  message: string
}

export interface DocumentUpdate {
  title?: string
  summary?: string
  key_points?: string[]
}



