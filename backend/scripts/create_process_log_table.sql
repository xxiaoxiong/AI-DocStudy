-- 创建文档处理日志表
CREATE TABLE IF NOT EXISTS document_process_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    
    -- 处理进度
    status ENUM('pending', 'parsing', 'analyzing', 'extracting', 'chunking', 'vectorizing', 'completed', 'failed') 
        DEFAULT 'pending',
    progress FLOAT DEFAULT 0.0 COMMENT '进度百分比 0-100',
    current_step VARCHAR(100) COMMENT '当前步骤描述',
    
    -- 处理详情
    total_steps INT DEFAULT 6 COMMENT '总步骤数',
    completed_steps INT DEFAULT 0 COMMENT '已完成步骤数',
    
    -- 日志信息
    logs JSON COMMENT '详细日志数组',
    
    -- 处理结果统计
    parsed_text_length INT COMMENT '解析文本长度',
    sections_count INT COMMENT '章节数量',
    chunks_count INT COMMENT '分块数量',
    ai_analysis_time FLOAT COMMENT 'AI分析耗时（秒）',
    total_time FLOAT COMMENT '总耗时（秒）',
    
    -- 错误信息
    error_message TEXT COMMENT '错误消息',
    error_traceback TEXT COMMENT '错误堆栈',
    
    -- 时间戳
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    -- 索引
    INDEX idx_document_id (document_id),
    INDEX idx_status (status),
    
    -- 外键
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档处理日志表';

