# Ureader v2.0

AI 深度阅读助手 - 帮助用户理解文本、管理阅读笔记、追踪阅读习惯。

## 功能特性

### 🏗️ 核心基础功能
- 多 AI 后端兼容 - 支持主流 AI 助手，默认 Hermes
- 对话历史管理 - 有效利用上下文记忆
- 文本输入接口 - 用户可粘贴或输入要分析的文字

### 🎭 被动功能（用户触发）
当用户发送一段文字后，主动弹出快捷选项：
- 内容总结 - 生成段落/章节摘要
- 多语言翻译 - 支持多种语言互译
- 深度解读 - 分析文本含义、背景、隐喻
- 词汇提取 - 提取关键词、专业术语并解释
- 概念图谱 - 快速分析相关、同类概念的关系与总体结构
- 主题识别 - 识别文本核心主题
- 情感分析 - 分析文本情感基调
- 问答模式 - 用户针对文本提问，AI 解答
- 关键点梳理 - 列出核心要点

### 🚀 主动功能（AI 驱动）
通过 Skill 后台收集信息，主动提供分析：
- 微信读书集成 - 同步阅读进度、标注
- 阅读进度分析 - 分析阅读速度、习惯
- 内容连贯性建议 - 提醒遗忘的前文要点
- 相关知识扩展 - 主动提供背景资料
- 阅读建议 - 基于阅读行为给出改进建议
- 主题关联 - 连接不同章节的相关概念
- 后续内容预测 - 基于前文推测后续发展
- 阅读提醒 - 根据目标提醒继续阅读
- AI 问答互动 - 根据对话历史和阅读划线，提出 3-5 个精选问题询问用户

### 🛠️ 对话增强功能
- 上下文回顾 - 快速回顾之前的对话和分析
- 多轮对话 - 针对同一文本深入探讨
- 对话导出 - 导出分析记录和对话历史
- 个性化设置 - 调整 AI 回复风格、详细程度
- 快捷指令 - 自定义快捷短语触发常用功能
- 历史记录 - 保存所有分析对话

### 📊 数据与统计
- 阅读统计 - 阅读时长、进度、速度
- 分析历史 - 所有 AI 分析的记录归档
- 词汇本 - 积累学习的新词汇
- 主题追踪 - 追踪阅读过的主题领域

## 技术架构

### 后端
- Python + FastAPI
- SQLite（WAL 模式）
- 全局写锁机制（并发控制）

### 前端
- 纯 HTML/CSS/JavaScript（无框架）
- D3.js（概念图谱）
- PWA 支持（离线可用）
- Service Worker + 本地缓存

## 部署

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
cd ureader
python backend/main.py
```

服务将在 http://0.0.0.0:8080 启动

### Android Termux 部署
1. 安装 Termux
2. 安装 Python: `pkg install python`
3. 克隆项目并安装依赖
4. 启动服务

## API 接口

### 基础路径
`/api`

### 核心接口

#### 聊天
- `POST /api/chat/send` - 发送消息
- `POST /api/chat/ask` - 问答模式
- `GET /api/chat/history` - 获取历史记录
- `DELETE /api/chat/history/{session_id}` - 删除会话
- `GET /api/chat/quick-actions` - 获取快捷指令
- `PUT /api/chat/quick-actions` - 更新快捷指令

#### 词汇本
- `GET /api/vocabulary` - 获取词汇列表
- `POST /api/vocabulary` - 创建词汇
- `PUT /api/vocabulary/{id}` - 更新词汇
- `DELETE /api/vocabulary/{id}` - 删除词汇
- `GET /api/vocabulary/{id}/history` - 词汇历史
- `POST /api/vocabulary/{id}/discuss` - 讨论词汇
- `GET /api/vocabulary/concept/{word}` - 概念关联

#### 阅读目标
- `GET /api/goals` - 获取目标
- `POST /api/goals` - 创建目标
- `PUT /api/goals/{id}` - 更新目标

#### 微信读书
- `GET /api/reading/current` - 当前阅读
- `GET /api/reading/stats` - 阅读统计
- `GET /api/reading/habits` - 阅读习惯
- `GET /api/notes/recent` - 最近笔记

#### 主动智能
- `GET /api/proactive/questions` - 精选问题
- `GET /api/proactive/reminders` - 阅读提醒
- `GET /api/proactive/continuity` - 连贯性分析
- `GET /api/proactive/suggestions` - 阅读建议
- `GET /api/proactive/music` - 音乐推荐
- `GET /api/proactive/bias` - 偏好分析

#### 心智回声
- `GET /api/reading/mind-echo` - 主题变迁对比

#### 设置
- `GET /api/settings` - 获取所有设置
- `PUT /api/settings/{key}` - 更新设置
- `GET /api/cache/clear` - 清除缓存

#### 系统
- `GET /api/health` - 健康检查
- `GET /api/status` - 系统状态

## 数据库

### 表结构
- `chat_history` - 聊天记录
- `quick_actions` - 快捷指令
- `settings` - 设置项
- `vocabulary` - 词汇本
- `vocab_history` - 词汇历史
- `reading_goals` - 阅读目标
- `topic_tracking` - 主题追踪

## 项目结构

```
ureader/
├── backend/
│   └── main.py          # FastAPI 应用
├── frontend/
│   ├── index.html       # 单页应用
│   ├── manifest.json    # PWA 清单
│   └── sw.js            # Service Worker
├── data/                # 数据目录
├── requirements.txt     # Python 依赖
└── README.md
```

## 核心流程

1. 用户输入文本
2. 选择快捷功能
3. AI 分析并返回结果
4. 多轮对话深入
5. 保存记录和统计

## 设计规范

- **主色调**: 深蓝 + 柔和绿
- **交互**: 响应式，触摸优化
- **安全**: 安全区域适配（全面屏）
- **缓存**: 前端 + 服务端双层缓存

## License

MIT