import { request } from '@/shared/utils/request'

export interface ChunkInfo {
  id: number
  chunk_index: number
  content: string
  chunk_hash: string
  section_id?: number
}

export interface SectionDetail {
  id: number
  title: string
  content?: string
  level: number
  order_index: number
  parent_id?: number
}

export interface ProcessDetail {
  document_id: number
  sections: SectionDetail[]
  sections_count: number
  chunks: ChunkInfo[]
  chunks_count: number
  total_text_length: number
  has_vectors: boolean
  vector_count: number
}

export const detailApi = {
  // 获取文档处理详情
  getProcessDetail(documentId: number): Promise<ProcessDetail> {
    return request.get(`/api/v1/documents/${documentId}/process-detail`)
  }
}



