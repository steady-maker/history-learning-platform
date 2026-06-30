# 基于大模型的轻量化历史学习平台

## 项目简介
Django + Vue3 前后端分离架构，接入豆包大模型API，实现AI智能辅导（提示、判题、复盘）的中学历史学习平台。

**采用前后台双端分离设计**：学生端 + 管理端，各自独立前后端

## 技术栈
- **后端**：Python 3.12, Django 5.x, DRF, Celery, JWT, RBAC
- **前端**：Vue3, Element Plus, Axios, Vite
- **数据库**：MySQL 8.0, Redis 6.2
- **搜索**：Elasticsearch 8.14 + IK分词器
- **AI**：豆包大模型API (doubao-seed-2-0-lite-260215), SSE流式输出

## 目录结构

```
history-learning-platform/
├── student/              # 学生端（前台）
│   ├── backend/         # 学生端后端 API - Django + DRF (端口19000)
│   └── frontend/        # 学生端前端 - Vue3 (端口5173)
├── admin/                # 管理端（后台）
│   ├── backend/         # 管理端后端 API - Django (端口18000)
│   └── frontend/        # 管理端前端 - Vue3 (端口5174)
├── sql/
│   └── mysql_init.sql   # 数据库初始化脚本
└── docs/
└── screenshots/     # 项目截图
```

## 核心功能
- **学生端**：题库浏览、在线答题、AI分步提示、AI智能判题、AI错题复盘、错题本、学习记录
- **管理端**：题库管理、提示词管理、标签管理、用户管理、数据统计、RBAC权限控制

## 快速开始

### 环境准备
- Python 3.12
- MySQL 8.0
- Redis 6.0+
- Elasticsearch 8.14.0 + IK分词器
- Node.js 20.x LTS

### 1. 数据库
```bash
# 启动MySQL，执行初始化脚本
mysql -u root -p < sql/mysql_init.sql
```

### 2. 启动基础服务

```
# 启动Redis（默认6379）
redis-server

# 启动Elasticsearch（默认9200）
# 确保IK分词器已安装
```

### 3. 学生端后端（端口19000）

```
cd student/backend
pip install -r requirements.txt

# 配置环境变量：ARK_API_KEY（火山方舟豆包API密钥）
export ARK_API_KEY=your_api_key_here

# 确认数据库配置正确后启动
python manage.py runserver 0.0.0.0:19000
```

### 4. 学生端前端

```
cd student/frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 5. 管理端后端（端口18000）

```
cd admin/backend
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:18000
```

### 6. 管理端前端

```
cd admin/frontend
npm install
npm run dev
# 访问 http://localhost:5174
```

### 7. ES索引初始化（仅执行一次）

```
# 进入学生端后端Django Shell
cd student/backend
python manage.py shell

# 执行初始化和同步
from question.es_utils import init_question_index, sync_questions_to_es
init_question_index()      # 仅执行一次
sync_questions_to_es()     # 数据库数据变更后执行
```

## 项目亮点

- **前缀和算法**优化AI调用频次统计
- **时间区间合并算法**处理复杂题目结构（主表+子题目+选项+答案）
- **SSE流式输出**优化AI交互体验（延迟<10s）
- **JMeter 100并发测试**，核心接口响应<180ms
- **前后台双端分离**，各自独立部署，RBAC权限控制
- **ES+IK分词器**实现全文检索，异常时自动降级数据库查询
- **提示词工程**：题目专属提示词 + 公共提示词（按标签复用）

## 截图

见 `docs/screenshots/` 目录

## 注意

- 本项目为毕业设计，豆包API Key需自行在火山方舟官网申请
- 学生端和管理端共用数据库，但服务独立部署
