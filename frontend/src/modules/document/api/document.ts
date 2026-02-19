import { request } from '@/shared/utils/request'
import type { Document, DocumentDetail, DocumentListResponse, UploadResponse, DocumentUpdate } from '../types'

export const documentApi = {
  // 上传文档
  upload(file: File, title?: string): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    
    return request.post('/api/v1/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 获取文档列表
  getList(params: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<DocumentListResponse> {
    return request.get('/api/v1/documents', { params })
  },

  // 获取文档详情
  getDetail(id: number): Promise<DocumentDetail> {
    return request.get(`/api/v1/documents/${id}`)
  },

  // 更新文档
  update(id: number, data: DocumentUpdate): Promise<Document> {
    return request.put(`/api/v1/documents/${id}`, data)
  },

  // 删除文档
  delete(id: number): Promise<{ success: boolean; message: string }> {
    return request.delete(`/api/v1/documents/${id}`)
  }
}



