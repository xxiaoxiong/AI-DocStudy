export type QuestionType = 'single' | 'judge' | 'essay'
export type Difficulty = 'easy' | 'medium' | 'hard'

export interface QuestionItem {
  id: number
  type: QuestionType
  content: string
  options?: Record<string, string> | null
}

export interface ExamConfig {
  document_id?: number | null
  document_title?: string | null
  single_count: number
  judge_count: number
  essay_count: number
  difficulty: Difficulty
}

export interface ExamSession {
  exam_id: number
  title: string
  document_id?: number | null
  document_title?: string | null
  total_questions: number
  single_count: number
  judge_count: number
  essay_count: number
  difficulty: Difficulty
  questions: QuestionItem[]
  created_at: string
}

export interface AnswerSubmitItem {
  question_id: number
  user_answer: string
}

export interface AnswerResultItem {
  question_id: number
  type: QuestionType
  content: string
  options?: Record<string, string> | null
  user_answer: string
  correct_answer: string
  is_correct: boolean
  score: number
  ai_feedback?: string | null
  explanation?: string | null
}

export interface ExamResult {
  exam_id: number
  title: string
  document_title?: string | null
  total_score: number
  max_score: number
  percentage: number
  passed: boolean
  single_correct: number
  single_total: number
  judge_correct: number
  judge_total: number
  essay_score: number
  essay_max: number
  answers: AnswerResultItem[]
  time_spent: number
  completed_at: string
}

export interface ExamHistoryItem {
  exam_id: number
  title: string
  document_title?: string | null
  total_score: number
  max_score: number
  percentage: number
  passed: boolean
  total_questions: number
  created_at: string
}
