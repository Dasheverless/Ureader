# AI阅读助手 - 产品规范

## 1. 项目概述

**项目名称**: AI阅读助手 (AI Reading Assistant)
**项目类型**: Android移动应用
**核心功能**: 一款对话驱动的AI阅读助手，帮助用户深入理解阅读内容，提供智能分析和个性化建议

**目标用户**:
- 深度阅读者
- 学生
- 研究人员
- 需要提升阅读效率和理解深度的用户

**核心价值**: 通过AI赋能提升阅读效率和理解深度，打造极简操作的阅读伴侣

## 2. 技术栈选择

**前端框架**: React 18 + TypeScript
**移动框架**: Capacitor 5 (跨平台Android/iOS)
**状态管理**: React Context + useReducer
**路由**: React Router v6
**样式**: Tailwind CSS
**图表**: Recharts
**概念图谱**: React Force Graph
**存储**: Capacitor Storage (本地存储)
**AI接口**: Hermes（默认），支持多后端配置

**开发环境**:
- Node.js 20+
- Android SDK 34
- Java 17+

## 3. 功能列表

### 3.1 核心基础功能
- [ ] 多AI后端兼容 - 支持主流AI助手，默认Hermes
- [ ] 对话历史管理 - 有效利用上下文记忆
- [ ] 文本输入接口 - 用户可粘贴或输入要分析的文字

### 3.2 被动功能（用户触发）

当用户发送一段文字后，主动弹出快捷选项：

- [ ] 内容总结 - 生成段落/章节摘要
- [ ] 多语言翻译 - 支持多种语言互译
- [ ] 深度解读 - 分析文本含义、背景、隐喻
- [ ] 词汇提取 - 提取关键词、专业术语并解释
- [ ] 概念图谱 - 快速分析相关、同类概念的关系与总体结构
- [ ] 主题识别 - 识别文本核心主题
- [ ] 情感分析 - 分析文本情感基调
- [ ] 问答模式 - 用户针对文本提问，AI解答
- [ ] 关键点梳理 - 列出核心要点

### 3.3 主动功能（AI驱动）

通过Skill后台收集信息，主动提供分析：

- [ ] 微信阅读集成 - 同步阅读进度、标注
- [ ] 阅读进度分析 - 分析阅读速度、习惯
- [ ] 内容连贯性建议 - 提醒遗忘的前文要点
- [ ] 相关知识扩展 - 主动提供背景资料
- [ ] 阅读建议 - 基于阅读行为给出改进建议
- [ ] 主题关联 - 连接不同章节的相关概念
- [ ] 后续内容预测 - 基于前文推测后续发展
- [ ] 阅读提醒 - 根据目标提醒继续阅读
- [ ] AI问答互动 - 根据对话历史和阅读划线，提出3-5个精选问题询问用户

### 3.4 对话增强功能
- [ ] 上下文回顾 - 快速回顾之前的对话和分析
- [ ] 多轮对话 - 针对同一文本深入探讨
- [ ] 对话导出 - 导出分析记录和对话历史
- [ ] 个性化设置 - 调整AI回复风格、详细程度
- [ ] 快捷指令 - 自定义快捷短语触发常用功能
- [ ] 历史记录 - 保存所有分析对话

### 3.5 数据与统计
- [ ] 阅读统计 - 阅读时长、进度、速度
- [ ] 分析历史 - 所有AI分析的记录归档
- [ ] 词汇本 - 积累学习的新词汇
- [ ] 主题追踪 - 追踪阅读过的主题领域

### 3.6 UI组件
- [ ] 聊天界面（气泡式对话）
- [ ] 快捷功能悬浮球
- [ ] 网格布局快捷功能菜单
- [ ] 阅读统计看板
- [ ] 概念图谱可视化（力导向图）

## 4. UI/UX设计方向

### 4.1 整体视觉风格
- **设计理念**: 现代极简主义，专注内容阅读
- **主色调**: 深蓝 (#1e3a5f) + 柔和绿 (#2ecc71)
- **辅助色**:
  - 背景色: #f5f7fa (浅灰)
  - 卡片色: #ffffff
  - 文字色: #333333 (主文字), #666666 (次要文字)
  - 强调色: #3498db (链接等)
- **圆角风格**: 12-16px 圆角
- **阴影效果**: 轻微阴影 (0 2px 8px rgba(0,0,0,0.1))

### 4.2 按钮设计
- 圆角胶囊形按钮
- 轻微阴影
- 悬停/点击上浮效果
- 主按钮: 深蓝背景，白色文字
- 次要按钮: 白色背景，深蓝边框

### 4.3 字体排版
- **主字体**: 思源黑体 (Noto Sans SC) + Roboto
- **标题**: 18-22px, font-weight: 600
- **正文**: 14-16px, font-weight: 400
- **辅助文字**: 12px, font-weight: 400

### 4.4 布局方式
- **底部导航**: 3个主导航项（对话、历史、设置）
- **聊天界面**: 卡片式气泡对话，底部固定输入栏
- **快捷功能**: 悬浮球 + 网格弹出菜单
- **设置页面**: 分组卡片布局
- **统计页面**: 仪表盘风格

### 4.5 交互设计
- **触摸优化**: 按钮最小48dp，适合单手操作
- **手势支持**: 支持横竖屏切换
- **动画效果**:
  - 快捷菜单弹出动画 (300ms ease-out)
  - 消息发送动画
  - 页面切换动画
- **响应式**: 移动优先设计，适配各种安卓屏幕尺寸

### 4.6 图标风格
- 简约线性图标
- lucide-react风格
- 统一 stroke-width: 2px
- 颜色: #666666 (默认), #1e3a5f (激活)

## 5. 应用架构

```
src/
├── components/          # UI组件
│   ├── Chat/           # 聊天相关组件
│   ├── QuickMenu/      # 快捷功能菜单
│   ├── History/        # 历史记录组件
│   ├── Settings/       # 设置页面组件
│   ├── Progress/        # 阅读进度组件
│   └── ConceptMap/     # 概念图谱组件
├── pages/              # 页面组件
├── contexts/           # React Context
├── hooks/              # 自定义Hooks
├── services/           # API服务
├── utils/              # 工具函数
├── types/              # TypeScript类型定义
└── styles/             # 全局样式
```

## 6. 数据模型

### 6.1 对话消息
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  type?: 'text' | 'summary' | 'translation' | 'interpretation' | 'concept' | 'vocabulary' | 'theme' | 'sentiment' | 'qa' | 'keypoints';
  metadata?: {
    originalText?: string;
    sourceLanguage?: string;
    targetLanguage?: string;
  };
}
```

### 6.2 对话会话
```typescript
interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
  tags?: string[];
  sourceText?: string;
  concepts?: ConceptNode[];
}
```

### 6.3 阅读统计
```typescript
interface ReadingStats {
  date: string;
  duration: number;
  wordsRead: number;
  textsAnalyzed: number;
}
```

### 6.4 用户设置
```typescript
interface UserSettings {
  aiProvider: 'hermes' | 'openai' | 'claude' | 'custom';
  apiKey?: string;
  apiEndpoint?: string;
  responseStyle: 'concise' | 'detailed';
  detailLevel: 'low' | 'medium' | 'high';
  dailyGoal: number;
}
```

### 6.5 概念图谱节点
```typescript
interface ConceptNode {
  id: string;
  name: string;
  description?: string;
  importance: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface ConceptLink {
  source: string;
  target: string;
  strength: number;
  relation?: string;
}

interface ConceptGraph {
  nodes: ConceptNode[];
  links: ConceptLink[];
}
```

### 6.6 词汇条目
```typescript
interface VocabularyItem {
  id: string;
  word: string;
  definition: string;
  sourceText: string;
  createdAt: number;
  reviewCount: number;
  lastReviewed?: number;
}
```

### 6.7 主题追踪
```typescript
interface ThemeTrack {
  id: string;
  theme: string;
  count: number;
  firstEncountered: number;
  lastEncountered: number;
  relatedConversations: string[];
}
```

## 8. AI后端 - Hermes

应用默认连接到Hermes AI网关，参考文档：https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/messaging/weixin

Hermes是一个本地运行的AI网关服务，支持通过微信等平台进行消息交互。应用将通过HTTP API与本地运行的Hermes网关进行通信。

### 8.1 集成架构
```
Android应用 <--> Hermes网关 (本地HTTP API) <--> 微信/其他平台
```

### 8.2 配置要求
- Hermes网关本地运行地址配置
- 支持本地存储配置
- 支持自定义API端点

## 9. 核心流程

```
用户打开应用 
  ↓
对话主页 → 输入/粘贴文本
  ↓
弹出快捷功能菜单
  ↓
选择功能: 总结/翻译/解读/概念图谱/知识扩展
  ↓
AI处理并返回结果
  ↓
多轮对话深入探讨
  ↓
保存对话历史
  ↓
查看历史记录/阅读进度统计
```

## 10. 验收标准

1. ✅ 应用可以正常启动并显示主界面
2. ✅ 可以输入文本并发送消息
3. ✅ 快捷功能菜单可以正常弹出和选择
4. ✅ 可以保存和查看对话历史
5. ✅ 设置页面可以配置AI后端
6. ✅ 阅读进度统计正常显示
7. ✅ 概念图谱可视化正常展示
8. ✅ APK可以成功构建并在Android设备上运行
9. ✅ UI设计符合规范要求（颜色、字体、布局）
10. ✅ 触摸交互流畅，无明显卡顿
