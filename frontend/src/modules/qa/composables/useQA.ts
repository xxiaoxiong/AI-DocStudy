import { ref } from 'vue'
import { useQAStore } from '../stores/qaStore'
import { ElMessage } from 'element-plus'

export function useQA() {
  const store = useQAStore()
  const asking = ref(false)

  const handleAsk = async (documentId: number | null, question: string) => {
    if (!question.trim()) {
      ElMessage.warning('请输入问题')
      return null
    }

    asking.value = true
    try {
      const response = await store.askQuestion(documentId, question)
      return response
    } catch (error: any) {
      ElMessage.error(error.message || '提问失败')
      throw error
    } finally {
      asking.value = false
    }
  }

  const handleFeedback = async (qaId: number, helpful: boolean) => {
    try {
      await store.submitFeedback(qaId, helpful)
      ElMessage.success('反馈提交成功')
    } catch (error: any) {
      ElMessage.error(error.message || '反馈提交失败')
      throw error
    }
  }

  return {
    asking,
    handleAsk,
    handleFeedback
  }
}



