# AI培训教学系统

基于AI的智能文档学习与考试平台

## 功能特性

### ✅ 已完成功能

1. **用户认证模块**
   - 用户注册/登录
   - JWT Token认证
   - 用户信息管理

2. **文档管理模块**
   - 文档上传（支持PDF、Word、TXT、Markdown）
   - 文档列表查看
   - 文档详情展示
   - 文档编辑/删除
   - 自动文档解析
   - 章节结构提取
   - 文档分块处理

### 🚧 开发中功能

3. **智能问答模块（RAG）**
   - 基于文档的智能问答
   - 引用来源标注
   - 问答历史记录

4. **自动出题与考试模块**
   - AI自动生成题目
   - 在线考试
   - 自动批改
   - 成绩分析

## 技术栈

### 后端
- FastAPI - Web框架
- SQLAlchemy - ORM
- MySQL - 数据库
- Redis - 缓存
- PyPDF2 - PDF解析
- python-docx - Word解析

### 前端
- Vue 3 - 前端框架
- TypeScript - 类型支持
- Element Plus - UI组件库
- Pinia - 状态管理
- Vue Router - 路由管理
- Axios - HTTP客户端

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

### 后端启动

1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息
```

3. 初始化数据库
```bash
python scripts/init_db.py
```

4. 启动服务
```bash
# Windows
测试文档上传.bat

# Linux/Mac
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
# Windows
启动前端.bat

# Linux/Mac
npm run dev
```

3. 访问应用
```
http://localhost:5173
```

## 项目结构

```
AI-DocStudy/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模式
│   │   ├── services/          # 业务逻辑
│   │   ├── repositories/      # 数据访问层
│   │   └── utils/             # 工具函数
│   ├── data/                  # 数据目录
│   │   ├── uploads/           # 上传文件
│   │   └── chroma/            # 向量数据库
│   └── requirements.txt       # Python依赖
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── modules/           # 功能模块
│   │   │   ├── auth/          # 认证模块
│   │   │   ├── document/      # 文档模块
│   │   │   ├── qa/            # 问答模块
│   │   │   └── exam/          # 考试模块
│   │   ├── shared/            # 共享资源
│   │   ├── router/            # 路由配置
│   │   └── stores/            # 全局状态
│   └── package.json           # Node依赖
│
└── docs/                       # 文档
```

## API文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发进度

- [x] 项目初始化
- [x] 用户认证模块
- [x] 文档管理模块
  - [x] 文档上传
  - [x] 文档列表
  - [x] 文档详情
  - [x] 文档解析
  - [x] 章节提取
  - [x] 文档分块
- [ ] 智能问答模块（RAG）
- [ ] 自动出题模块
- [ ] 考试管理模块

## 测试账号

```
用户名: admin
密码: admin123
```

## 常见问题

### 1. 数据库连接失败
检查 MySQL 服务是否启动，以及 `.env` 文件中的数据库配置是否正确。

### 2. 文档上传失败
确保 `backend/data/uploads` 目录存在且有写入权限。

### 3. 前端无法连接后端
检查后端服务是否正常运行，以及前端的 API 地址配置是否正确。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
