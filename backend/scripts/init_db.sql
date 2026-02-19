-- AI培训教学系统数据库初始化脚本

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 1. 用户表
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
  `email` VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `role` ENUM('student', 'teacher', 'admin') DEFAULT 'student' COMMENT '角色',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_login` TIMESTAMP NULL COMMENT '最后登录时间',
  INDEX `idx_username` (`username`),
  INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ----------------------------
-- 2. 文档表
-- ----------------------------
DROP TABLE IF EXISTS `documents`;
CREATE TABLE `documents` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(255) NOT NULL COMMENT '文档标题',
  `file_path` VARCHAR(500) NOT NULL COMMENT '文件路径',
  `file_type` VARCHAR(20) NOT NULL COMMENT '文件类型',
  `file_size` INT COMMENT '文件大小(字节)',
  `status` ENUM('processing', 'completed', 'failed') DEFAULT 'processing' COMMENT '处理状态',
  `summary` TEXT COMMENT '文档摘要',
  `key_points` JSON COMMENT '核心要点',
  `uploaded_by` INT COMMENT '上传者ID',
  `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `processed_at` TIMESTAMP NULL COMMENT '处理完成时间',
  FOREIGN KEY (`uploaded_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX `idx_status` (`status`),
  INDEX `idx_uploaded_by` (`uploaded_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档表';

-- ----------------------------
-- 3. 文档章节表
-- ----------------------------
DROP TABLE IF EXISTS `document_sections`;
CREATE TABLE `document_sections` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL COMMENT '文档ID',
  `title` VARCHAR(255) NOT NULL COMMENT '章节标题',
  `content` TEXT COMMENT '章节内容',
  `level` INT DEFAULT 1 COMMENT '章节层级',
  `parent_id` INT NULL COMMENT '父章节ID',
  `order_index` INT DEFAULT 0 COMMENT '排序索引',
  FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`parent_id`) REFERENCES `document_sections`(`id`) ON DELETE CASCADE,
  INDEX `idx_document` (`document_id`),
  INDEX `idx_parent` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档章节表';

-- ----------------------------
-- 4. 文档分块表(用于向量检索)
-- ----------------------------
DROP TABLE IF EXISTS `document_chunks`;
CREATE TABLE `document_chunks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL COMMENT '文档ID',
  `section_id` INT NULL COMMENT '章节ID',
  `chunk_index` INT NOT NULL COMMENT '分块索引',
  `content` TEXT NOT NULL COMMENT '分块内容',
  `chunk_hash` VARCHAR(64) COMMENT '内容哈希',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`section_id`) REFERENCES `document_sections`(`id`) ON DELETE SET NULL,
  INDEX `idx_document` (`document_id`),
  INDEX `idx_hash` (`chunk_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档分块表';

-- ----------------------------
-- 5. 题目表
-- ----------------------------
DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL COMMENT '文档ID',
  `section_id` INT NULL COMMENT '章节ID',
  `type` ENUM('single', 'judge', 'essay') NOT NULL COMMENT '题目类型',
  `difficulty` ENUM('easy', 'medium', 'hard') DEFAULT 'medium' COMMENT '难度',
  `content` TEXT NOT NULL COMMENT '题目内容',
  `options` JSON NULL COMMENT '选项(选择题)',
  `answer` TEXT NOT NULL COMMENT '答案',
  `explanation` TEXT COMMENT '解析',
  `source_reference` VARCHAR(255) COMMENT '来源章节',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`section_id`) REFERENCES `document_sections`(`id`) ON DELETE SET NULL,
  INDEX `idx_document` (`document_id`),
  INDEX `idx_type_difficulty` (`type`, `difficulty`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题目表';

-- ----------------------------
-- 6. 考试表
-- ----------------------------
DROP TABLE IF EXISTS `exams`;
CREATE TABLE `exams` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `document_id` INT NOT NULL COMMENT '文档ID',
  `title` VARCHAR(255) NOT NULL COMMENT '考试标题',
  `description` TEXT COMMENT '考试描述',
  `duration` INT DEFAULT 60 COMMENT '考试时长(分钟)',
  `total_score` INT DEFAULT 100 COMMENT '总分',
  `pass_score` INT DEFAULT 60 COMMENT '及格分',
  `created_by` INT COMMENT '创建者ID',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX `idx_document` (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试表';

-- ----------------------------
-- 7. 考试题目关联表
-- ----------------------------
DROP TABLE IF EXISTS `exam_questions`;
CREATE TABLE `exam_questions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `exam_id` INT NOT NULL COMMENT '考试ID',
  `question_id` INT NOT NULL COMMENT '题目ID',
  `score` INT DEFAULT 10 COMMENT '该题分值',
  `order_index` INT DEFAULT 0 COMMENT '排序索引',
  FOREIGN KEY (`exam_id`) REFERENCES `exams`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE,
  INDEX `idx_exam` (`exam_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试题目关联表';

-- ----------------------------
-- 8. 答题记录表
-- ----------------------------
DROP TABLE IF EXISTS `answer_records`;
CREATE TABLE `answer_records` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL COMMENT '用户ID',
  `exam_id` INT NULL COMMENT '考试ID',
  `question_id` INT NOT NULL COMMENT '题目ID',
  `user_answer` TEXT COMMENT '用户答案',
  `is_correct` TINYINT(1) DEFAULT 0 COMMENT '是否正确',
  `score` DECIMAL(5,2) DEFAULT 0 COMMENT '得分',
  `ai_feedback` TEXT COMMENT 'AI评分反馈',
  `time_spent` INT DEFAULT 0 COMMENT '答题时长(秒)',
  `answered_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`exam_id`) REFERENCES `exams`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_question` (`user_id`, `question_id`),
  INDEX `idx_exam` (`exam_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='答题记录表';

-- ----------------------------
-- 9. 问答记录表
-- ----------------------------
DROP TABLE IF EXISTS `qa_records`;
CREATE TABLE `qa_records` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL COMMENT '用户ID',
  `document_id` INT NOT NULL COMMENT '文档ID',
  `question` TEXT NOT NULL COMMENT '问题',
  `answer` TEXT NOT NULL COMMENT '答案',
  `sources` JSON COMMENT '引用来源',
  `helpful` TINYINT(1) NULL COMMENT '是否有帮助',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON DELETE CASCADE,
  INDEX `idx_user` (`user_id`),
  INDEX `idx_document` (`document_id`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问答记录表';

-- ----------------------------
-- 插入测试数据
-- ----------------------------
-- 插入管理员用户 (密码: admin123)
INSERT INTO `users` (`username`, `email`, `password_hash`, `role`) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jrPK', 'admin');

SET FOREIGN_KEY_CHECKS = 1;

