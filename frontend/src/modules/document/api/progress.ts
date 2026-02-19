import { request } from '@/shared/utils/request'

export interface LogEntry {
  time: string
  level: string
  message: string
  details?: any
}

export interface ProcessProgress {
  document_id: number
  status: string
  progress: number
  current_step: string
  completed_steps: number
  total_steps: number
  logs: LogEntry[]
  
  // 统计信息
  parsed_text_length?: number
  sections_count?: number
  chunks_count?: number
  ai_analysis_time?: number
  total_time?: number
  
  // 错误信息
  error_message?: string
  error_traceback?: string
  
  // 时间
  started_at: string
  updated_at: string
  completed_at?: string
}

export const progressApi = {
  // 获取文档处理进度
  getProgress(documentId: number): Promise<ProcessProgress> {
    return request.get(`/api/v1/documents/${documentId}/progress`)
  }
}



