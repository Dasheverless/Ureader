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
**AI接口**: 支持多后端配置（OpenAI、Claude等）

**开发环境**:
- Node.js 20+
- Android SDK 34
- Java 17+

## 3. 功能列表

### 3.1 对话主页
- [ ] 聊天界面（气泡式对话）
- [ ] 文本输入框（支持粘贴和手动输入）
- [ ] 快捷功能悬浮球
- [ ] 多轮对话支持
- [ ] 时间戳显示
- [ ] 消息发送动画

### 3.2 快捷功能菜单
- [ ] 网格布局展示功能选项
- [ ] 总结功能（Summary）
- [ ] 翻译功能（Translation）
- [ ] 解读功能（Interpretation）
- [ ] 概念图谱（Concept Map）
- [ ] 知识扩展（Knowledge Extension）
- [ ] 动画展开效果

### 3.3 历史记录
- [ ] 查看过往对话分析
- [ ] 搜索功能
- [ ] 筛选功能
- [ ] 删除历史记录
- [ ] 按时间分组展示

### 3.4 设置页面
- [ ] AI后端配置
  - [ ] 选择AI助手类型（OpenAI/Claude/自定义）
  - [ ] 配置API密钥
  - [ ] API端点配置
- [ ] 个性化设置
  - [ ] 回复风格（简洁/详细）
  - [ ] 详细程度控制
  - [ ] 快捷指令管理
- [ ] 数据管理
  - [ ] 导出数据
  - [ ] 清除历史
  - [ ] 应用信息

### 3.5 阅读进度
- [ ] 阅读统计看板
  - [ ] 阅读时长统计
  - [ ] 阅读速度计算
  - [ ] 进度可视化
- [ ] 目标追踪
  - [ ] 设置每日目标
  - [ ] 进度条展示
- [ ] 数据可视化（图表展示）

### 3.6 概念图谱可视化
- [ ] 力导向图展示概念关系
- [ ] 节点大小表示重要程度
- [ ] 连线粗细表示关联强度
- [ ] 缩放交互
- [ ] 拖拽交互
- [ ] 悬停显示详细信息

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
  type?: 'text' | 'summary' | 'translation' | 'interpretation' | 'concept';
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
  aiProvider: 'openai' | 'claude' | 'custom';
  apiKey?: string;
  apiEndpoint?: string;
  responseStyle: 'concise' | 'detailed';
  detailLevel: 'low' | 'medium' | 'high';
  dailyGoal: number;
}
```

## 7. 核心流程

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

## 8. 验收标准

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
