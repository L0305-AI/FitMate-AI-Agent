# 🏋️ FitMate - 智能健身与饮食助理 

## 📖 项目简介
**FitMate** 是一个基于大语言模型（LLM）与 LangGraph 构建的智能健康管理助手。本项目不仅实现了自然流畅的多轮对话，更通过 **RAG 检索增强**、**长短期记忆持久化**、**外部工具调用**，实现了从“健康咨询”到“饮食自动打卡”的全链路数据闭环。

---

## 🛠️ 技术栈
- **前端**：Vue 3 + Vite + Axios + ECharts + Marked (Markdown 渲染)
- **后端**：FastAPI + Uvicorn + SQLAlchemy
- **Agent 编排**：LangChain + LangGraph
- **向量数据库**：Qdrant (用于 RAG 知识库检索)
- **关系型数据库**：MySQL (用于用户画像、饮食打卡、体重历史记录)
- **大语言模型**：阿里通义千问 (qwen3.8-flash) / 向量模型 (qwen3.7-text-embedding-flash)

---

## 📂 项目目录结构

```text
FitMate-Agent/
│
├── backend/                       # 后端服务 (FastAPI + LangGraph + MySQL + Qdrant)
│   ├── app/
│   │   ├── main.py                # FastAPI 全局入口：路由注册、鉴权、大模型流式对接
│   │   ├── agent/                 # Agent 智能体核心编排层
│   │   │   ├── graph.py           # LangGraph 状态图 (定义 Node 与 条件路由)
│   │   │   ├── memory.py          # 记忆管理模块 (预留/封装)
│   │   │   └── prompts.py         # 系统提示词 (人设、隐藏 JSON 规则)
│   │   ├── core/                  # 核心配置与数据库连接
│   │   │   ├── config.py          # 环境变量读取
│   │   │   └── database.py        # SQLAlchemy 数据库连接池 (含保活机制)
│   │   ├── tools/                 # 核心工具层
│   │   │   ├── diet_calc.py       # 工具1：饮食热量计算 (带异常捕获)
│   │   │   ├── exercise_calc.py   # 工具2：健康指标计算 (BMI/BMR)
│   │   │   └── reminder.py        # 工具3：健康提醒生成
│   │   ├── rag/                   # 检索增强生成 (RAG) 模块
│   │   │   ├── ingest.py          # 知识库向量化灌入脚本
│   │   │   └── retriever.py       # 向量检索封装
│   │   └── models/                # 数据库 ORM 模型
│   │       ├── user_profile.py    # 用户画像表
│   │       ├── chat_history.py    # 聊天记录表
│   │       ├── diet_log.py        # 饮食打卡记录表
│   │       ├── weight_log.py      # 体重历史变化表
│   │       └── recipe.py          # 食谱库表
│   ├── data/                      # 本地知识库数据源
│   │   ├── fitness_guide.txt      # 健身指导文本
│   │   └── nutrition_guide.txt    # 营养学指导文本
│   ├── requirements.txt           # Python 依赖清单
│   ├── users.json                 # 本地注册用户库 
│   └── .env                       # 环境变量配置 (需自行配置 API Key)
│
├── frontend/                      # 前端界面 (Vue 3 + Vite + ECharts)
│   ├── src/
│   │   ├── main.js                # Vue 应用入口
│   │   ├── App.vue                # 根组件：全局路由、登录拦截、布局
│   │   └── components/            # 业务组件库
│   │       ├── ChatView.vue       # 智能对话组件：流式输出、隐藏 JSON 提取
│   │       ├── DashboardView.vue  # 健康看板组件：ECharts 真实体重折线图
│   │       ├── DietView.vue       # 饮食计划组件：食谱增删、四宫格打卡
│   │       ├── ProfileView.vue    # 个人档案组件：长期记忆增删改查
│   │       └── DietModal.vue      # 饮食打卡弹窗组件
│   ├── package.json
│   └── vite.config.js
│
└── README.md                      # 项目说明文档
```

---

## 🚀 快速启动指南

### 1. 启动后端 (FastAPI)

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# ⚠️ 配置环境变量：在 .env 文件中填入你的通义千问 API Key 和 MySQL 密码
# (请编辑 .env)

# 初始化向量库 (如果首次运行或数据被清空)
python app/rag/ingest.py

# 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. 启动前端 (Vue 3)

```bash
# 新开一个终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
