-- 为documents表添加AI分析字段
ALTER TABLE documents 
ADD COLUMN one_sentence_summary VARCHAR(500) COMMENT '一句话总结',
ADD COLUMN document_type VARCHAR(100) COMMENT '文档类型',
ADD COLUMN difficulty_level VARCHAR(50) COMMENT '难度等级',
ADD COLUMN target_audience VARCHAR(200) COMMENT '目标读者',
ADD COLUMN estimated_reading_time VARCHAR(50) COMMENT '预计阅读时间',
ADD COLUMN key_concepts JSON COMMENT '关键概念',
ADD COLUMN learning_suggestions JSON COMMENT '学习建议',
ADD COLUMN common_questions JSON COMMENT '常见问题';

-- 修改summary字段类型为TEXT（如果还不是的话）
ALTER TABLE documents MODIFY COLUMN summary TEXT COMMENT '详细摘要';

-- 修改key_points字段类型为JSON（如果还不是的话）
ALTER TABLE documents MODIFY COLUMN key_points JSON COMMENT '核心要点';



