import asyncio
import json
import os
import sqlite3
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 配置
APP_NAME = "Ureader"
APP_VERSION = "2.0.0"
DB_PATH = "data/ureader.db"
DATA_DIR = "data"

# 全局缓存
_CACHE: Dict[str, Any] = {}
_CACHE_TTL: Dict[str, float] = {}

# 数据库锁
db_lock = asyncio.Lock()

# 创建 FastAPI 应用
app = FastAPI(title=APP_NAME, version=APP_VERSION)

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)


# ==================== 数据库层 ====================
@contextmanager
def get_db():
    db = sqlite3.connect(DB_PATH, timeout=5.0)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.execute("PRAGMA foreign_keys=ON")
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
                content TEXT NOT NULL,
                action_type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS quick_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                icon TEXT NOT NULL,
                prompt TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT,
                context TEXT,
                source_book TEXT,
                source_chapter TEXT,
                source_book_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                review_count INTEGER DEFAULT 0
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS vocab_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vocab_id INTEGER NOT NULL REFERENCES vocabulary(id) ON DELETE CASCADE,
                field TEXT NOT NULL DEFAULT 'meaning',
                old_value TEXT,
                new_value TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS reading_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL CHECK(goal_type IN ('daily_minutes','books_per_month','pages_per_day')),
                target_value INTEGER NOT NULL,
                current_value INTEGER DEFAULT 0,
                period_start TEXT,
                period_end TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS topic_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                book_title TEXT,
                book_id TEXT,
                read_time_sec INTEGER DEFAULT 0,
                note_count INTEGER DEFAULT 0,
                last_read_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id, created_at)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_content ON chat_history(content)
        """)
        db.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_vocab_word_book ON vocabulary(word, COALESCE(source_book_id, ''))
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_vocab_hist ON vocab_history(vocab_id, changed_at)
        """)
        
        # 初始化默认数据
        cursor = db.execute("SELECT COUNT(*) FROM quick_actions")
        if cursor.fetchone()[0] == 0:
            default_actions = [
                (1, "内容总结", "📝", "请简洁总结以下内容的核心要点：\n\n{message}", 0, 1),
                (2, "古文翻译", "📜", "请将以下古文翻译成现代汉语：\n\n{message}", 1, 1),
                (3, "深度解读", "🔍", "请深入解读以下内容的含义、背景和隐喻：\n\n{message}", 2, 1),
                (4, "词汇提取", "📚", "请提取以下内容中的关键词和专业术语，逐一解释：\n\n{message}", 3, 1),
                (5, "概念图谱", "🕸️", "请分析以下内容的概念关系，严格返回JSON格式：{{\"nodes\":[{{\"id\":\"概念\",\"group\":1}}],\"edges\":[{{\"source\":\"A\",\"target\":\"B\",\"label\":\"关系\"}}]}}", 4, 1),
                (6, "主题识别", "🎯", "请识别以下内容的核心主题和子主题：\n\n{message}", 5, 1),
                (7, "情感分析", "💭", "请分析以下内容的情感基调：\n\n{message}", 6, 1),
                (8, "问答模式", "❓", "请使用费曼技巧，针对以下内容提出3-5个层层递进的问题：\n\n{message}", 7, 1),
                (9, "关键点梳理", "⭐", "请梳理以下内容的核心要点，用结构化列表呈现：\n\n{message}", 8, 1),
            ]
            db.executemany("""
                INSERT INTO quick_actions (id, name, icon, prompt, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, default_actions)
        
        # 初始化默认设置
        default_settings = [
            ("ai_provider", "hermes"),
            ("ai_model", "hermes-agent"),
            ("api_key", "change-me-local-dev"),
            ("api_base_url", "http://localhost:8642/v1"),
            ("reply_style", "detailed"),
            ("language", "zh-CN"),
            ("theme", "dark"),
        ]
        for key, value in default_settings:
            db.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            """, (key, value))


# ==================== 数据模型 ====================
class MessageRequest(BaseModel):
    message: str
    session_id: str
    action_type: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    session_id: str


class VocabRequest(BaseModel):
    word: str
    meaning: Optional[str] = None
    context: Optional[str] = None
    source_book: Optional[str] = None
    source_chapter: Optional[str] = None
    source_book_id: Optional[str] = None


class VocabUpdateRequest(BaseModel):
    meaning: Optional[str] = None
    context: Optional[str] = None


class GoalRequest(BaseModel):
    goal_type: str
    target_value: int
    current_value: int = 0


class SettingRequest(BaseModel):
    value: str


# ==================== 辅助函数 ====================
def get_settings() -> Dict[str, str]:
    with get_db() as db:
        cursor = db.execute("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in cursor.fetchall()}


def get_setting(key: str, default: str = "") -> str:
    with get_db() as db:
        cursor = db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default


def call_ai(messages: List[Dict[str, str]]) -> str:
    settings = get_settings()
    api_url = settings.get("api_base_url", "http://localhost:8642/v1") + "/chat/completions"
    api_key = settings.get("api_key", "change-me-local-dev")
    model = settings.get("ai_model", "hermes-agent")
    
    try:
        import httpx
        response = httpx.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages},
            timeout=60.0
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        # Mock AI response for development
        return f"[Mock AI 响应] 处理完成：{messages[-1]['content'][:50]}..."


def extract_json_from_text(text: str) -> Optional[Dict]:
    match = re.search(r'(\{[^{}]*\}(?:[^{}]*\{[^{}]*\})*)', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None


def get_action_prompt(action_type: str, message: str) -> str:
    prompts = {
        "summarize": "请简洁总结以下内容的核心要点：\n\n{message}",
        "translate": "请将以下古文翻译成现代汉语：\n\n{message}",
        "interpret": "请深入解读以下内容的含义、背景和隐喻：\n\n{message}",
        "vocabulary": "请提取以下内容中的关键词和专业术语，逐一解释：\n\n{message}",
        "concept_map": '请分析以下内容的概念关系，严格返回JSON格式：{{"nodes":[{"id":"概念","group":1}],"edges":[{"source":"A","target":"B","label":"关系"}]}}',
        "theme": "请识别以下内容的核心主题和子主题：\n\n{message}",
        "sentiment": "请分析以下内容的情感基调：\n\n{message}",
        "qa": "请使用费曼技巧，针对以下内容提出3-5个层层递进的问题：\n\n{message}",
        "keypoints": "请梳理以下内容的核心要点，用结构化列表呈现：\n\n{message}",
    }
    
    if action_type in prompts:
        return prompts[action_type].format(message=message)
    
    # 从数据库查找自定义动作
    with get_db() as db:
        cursor = db.execute("SELECT prompt FROM quick_actions WHERE name LIKE ? LIMIT 1", (f"%{action_type}%",))
        row = cursor.fetchone()
        if row:
            return row["prompt"].format(message=message)
    
    return message


def get_mock_response(action_type: str, message: str) -> str:
    mocks = {
        "summarize": f"[Mock] 这段文字的核心要点是关于{message[:20]}...",
        "translate": f"[Mock] 翻译结果：{message[:30]}...",
        "interpret": f"[Mock] 深度解读：{message[:30]}...",
        "vocabulary": f"[Mock] 关键词提取：1. {message[:10]}...",
        "concept_map": json.dumps({
            "nodes": [{"id": "阅读", "group": 1}, {"id": "AI", "group": 2}],
            "edges": [{"source": "阅读", "target": "AI", "label": "使用"}]
        }),
        "theme": f"[Mock] 核心主题：{message[:20]}...",
        "sentiment": "[Mock] 情感基调：中性偏积极",
        "qa": "[Mock] 1. 什么是...? 2. 为什么...? 3. 如何...?",
        "keypoints": "[Mock] 1. 要点一 2. 要点二 3. 要点三",
    }
    return mocks.get(action_type, f"[Mock] 响应：{message[:30]}")


# ==================== API 端点 ====================

# 健康检查
@app.get("/api/health")
async def health():
    return {"status": "ok", "name": APP_NAME, "version": APP_VERSION}


@app.get("/api/status")
async def status():
    return {
        "ai_ok": True,
        "weread_ok": True,
        "hermes_cli_exists": True,
    }


# 聊天 API
@app.post("/api/chat/send")
async def send_message(
    data: MessageRequest,
    mock_ai: bool = Query(False)
):
    session_id = data.session_id
    user_message = data.message
    action_type = data.action_type or "text"
    
    # 1. 写入用户消息
    async with db_lock:
        with get_db() as db:
            db.execute("""
                INSERT INTO chat_history (session_id, role, content, action_type)
                VALUES (?, ?, ?, ?)
            """, (session_id, "user", user_message, action_type))
    
    # 2. 调用 AI（在锁外）
    if mock_ai:
        ai_response = get_mock_response(action_type, user_message)
    else:
        with get_db() as db:
            cursor = db.execute("""
                SELECT role, content FROM chat_history
                WHERE session_id = ?
                ORDER BY created_at DESC LIMIT 20
            """, (session_id,))
            history = []
            for row in cursor.fetchall():
                history.insert(0, {"role": row["role"], "content": row["content"]})
            
            system_prompt = "你是 Ureader 深度阅读助手。帮助用户理解文本，回答精准有条理，使用中文。概念图谱请求严格返回JSON。"
            user_prompt = get_action_prompt(action_type, user_message)
            messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_prompt}]
            ai_response = call_ai(messages)
    
    # 3. 写入助手回复
    concept_data = None
    if action_type == "concept_map":
        concept_data = extract_json_from_text(ai_response)
    
    async with db_lock:
        with get_db() as db:
            db.execute("""
                INSERT INTO chat_history (session_id, role, content, action_type)
                VALUES (?, ?, ?, ?)
            """, (session_id, "assistant", ai_response, action_type))
    
    return {
        "session_id": session_id,
        "response": ai_response,
        "concept_data": concept_data,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat/ask")
async def ask_question(data: AskRequest):
    async with db_lock:
        with get_db() as db:
            db.execute("""
                INSERT INTO chat_history (session_id, role, content, action_type)
                VALUES (?, ?, ?, ?)
            """, (data.session_id, "assistant", data.question, "qa"))
    return {"session_id": data.session_id, "status": "ok"}


@app.get("/api/chat/history")
async def get_history(
    session_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    with get_db() as db:
        if search:
            cursor = db.execute("""
                SELECT session_id, 
                       MIN(created_at) as first_msg, 
                       MAX(created_at) as last_msg, 
                       COUNT(*) as count
                FROM chat_history
                WHERE content LIKE ? AND role = 'user'
                GROUP BY session_id
                ORDER BY last_msg DESC
                LIMIT ? OFFSET ?
            """, (f"%{search}%", limit, offset))
            results = []
            for row in cursor.fetchall():
                cursor2 = db.execute("""
                    SELECT content FROM chat_history
                    WHERE session_id = ? AND role = 'user'
                    ORDER BY created_at ASC LIMIT 1
                """, (row["session_id"],))
                msg = cursor2.fetchone()
                preview = (msg["content"][:30] + "...") if msg else ""
                results.append({
                    "session_id": row["session_id"],
                    "first_msg": row["first_msg"],
                    "last_msg": row["last_msg"],
                    "preview": preview,
                    "count": row["count"]
                })
            return results
        elif session_id:
            cursor = db.execute("""
                SELECT id, role, content, action_type, created_at
                FROM chat_history
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ? OFFSET ?
            """, (session_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
        else:
            cursor = db.execute("""
                SELECT session_id, 
                       MIN(created_at) as first_msg, 
                       MAX(created_at) as last_msg, 
                       COUNT(*) as count
                FROM chat_history
                GROUP BY session_id
                ORDER BY last_msg DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            results = []
            for row in cursor.fetchall():
                cursor2 = db.execute("""
                    SELECT content FROM chat_history
                    WHERE session_id = ? AND role = 'user'
                    ORDER BY created_at ASC LIMIT 1
                """, (row["session_id"],))
                msg = cursor2.fetchone()
                preview = (msg["content"][:30] + "...") if msg else ""
                results.append({
                    "session_id": row["session_id"],
                    "first_msg": row["first_msg"],
                    "last_msg": row["last_msg"],
                    "preview": preview,
                    "count": row["count"]
                })
            return results


@app.delete("/api/chat/history/{session_id}")
async def delete_session(session_id: str):
    async with db_lock:
        with get_db() as db:
            db.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    return {"status": "ok"}


# 快捷指令 API
@app.get("/api/chat/quick-actions")
async def get_quick_actions():
    with get_db() as db:
        cursor = db.execute("""
            SELECT id, name, icon, prompt, sort_order, is_active
            FROM quick_actions
            WHERE is_active = 1
            ORDER BY sort_order ASC
        """)
        return [dict(row) for row in cursor.fetchall()]


@app.put("/api/chat/quick-actions")
async def update_quick_actions(actions: List[Dict]):
    async with db_lock:
        with get_db() as db:
            for action in actions:
                db.execute("""
                    INSERT OR REPLACE INTO quick_actions 
                    (id, name, icon, prompt, sort_order, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    action["id"], action["name"], action["icon"], 
                    action["prompt"], action["sort_order"], action["is_active"]
                ))
    return {"status": "ok"}


# 词汇本 API
@app.get("/api/vocabulary")
async def get_vocabulary(
    search: Optional[str] = None,
    limit: int = 30,
    offset: int = 0
):
    with get_db() as db:
        if search:
            cursor = db.execute("""
                SELECT * FROM vocabulary
                WHERE word LIKE ? OR meaning LIKE ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """, (f"%{search}%", f"%{search}%", limit, offset))
        else:
            cursor = db.execute("""
                SELECT * FROM vocabulary
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]


@app.post("/api/vocabulary")
async def create_vocab(data: VocabRequest):
    async with db_lock:
        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO vocabulary (word, meaning, context, source_book, source_chapter, source_book_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data.word, data.meaning, data.context, data.source_book, data.source_chapter, data.source_book_id))
            word_id = cursor.lastrowid
            if data.meaning:
                db.execute("""
                    INSERT INTO vocab_history (vocab_id, field, old_value, new_value)
                    VALUES (?, 'meaning', ?, ?)
                """, (word_id, None, data.meaning))
    return {"status": "ok", "id": word_id}


@app.put("/api/vocabulary/{word_id}")
async def update_vocab(word_id: int, data: VocabUpdateRequest):
    async with db_lock:
        with get_db() as db:
            changes = 0
            cursor = db.execute("SELECT meaning, context FROM vocabulary WHERE id = ?", (word_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="词汇不存在")
            
            old_meaning, old_context = row["meaning"], row["context"]
            
            if data.meaning is not None and data.meaning != old_meaning:
                db.execute("""
                    UPDATE vocabulary SET meaning = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """, (data.meaning, word_id))
                db.execute("""
                    INSERT INTO vocab_history (vocab_id, field, old_value, new_value)
                    VALUES (?, 'meaning', ?, ?)
                """, (word_id, old_meaning, data.meaning))
                changes += 1
            
            if data.context is not None and data.context != old_context:
                db.execute("""
                    UPDATE vocabulary SET context = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """, (data.context, word_id))
                db.execute("""
                    INSERT INTO vocab_history (vocab_id, field, old_value, new_value)
                    VALUES (?, 'context', ?, ?)
                """, (word_id, old_context, data.context))
                changes += 1
    
    return {"status": "ok", "changes": changes}


@app.delete("/api/vocabulary/{word_id}")
async def delete_vocab(word_id: int):
    async with db_lock:
        with get_db() as db:
            db.execute("DELETE FROM vocabulary WHERE id = ?", (word_id,))
    return {"status": "ok"}


@app.get("/api/vocabulary/{word_id}/history")
async def get_vocab_history(word_id: int):
    with get_db() as db:
        cursor = db.execute("""
            SELECT * FROM vocab_history
            WHERE vocab_id = ?
            ORDER BY changed_at DESC
            LIMIT 20
        """, (word_id,))
        return [dict(row) for row in cursor.fetchall()]


@app.post("/api/vocabulary/{word_id}/discuss")
async def discuss_vocab(word_id: int, data: Dict):
    with get_db() as db:
        cursor = db.execute("SELECT word, meaning FROM vocabulary WHERE id = ?", (word_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="词汇不存在")
        
        word, meaning = row["word"], row["meaning"]
        question = data.get("question", f"请深入解释这个词：{word}")
        prompt = f"{question}\n\n已知含义：{meaning}"
        response = call_ai([{"role": "user", "content": prompt}])
    
    return {"response": response, "word": word}


@app.get("/api/vocabulary/concept/{word}")
async def get_concept_cross_ref(word: str):
    with get_db() as db:
        cursor = db.execute("""
            SELECT * FROM vocabulary
            WHERE word = ? OR word LIKE ?
            ORDER BY updated_at DESC
        """, (word, f"%{word}%"))
        rows = cursor.fetchall()
        
        books = {}
        for row in rows:
            book = row["source_book"] or "未知书籍"
            if book not in books:
                books[book] = []
            books[book].append(dict(row))
    
    return {"word": word, "total": len(rows), "books": books}


# 阅读目标 API
@app.get("/api/goals")
async def get_goals():
    with get_db() as db:
        cursor = db.execute("""
            SELECT * FROM reading_goals
            WHERE is_active = 1
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


@app.post("/api/goals")
async def create_goal(data: GoalRequest):
    today = datetime.now().strftime("%Y-%m-%d")
    async with db_lock:
        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO reading_goals (goal_type, target_value, current_value, period_start)
                VALUES (?, ?, ?, ?)
            """, (data.goal_type, data.target_value, data.current_value, today))
            goal_id = cursor.lastrowid
    return {"status": "ok", "id": goal_id}


@app.put("/api/goals/{goal_id}")
async def update_goal(goal_id: int, data: GoalRequest):
    async with db_lock:
        with get_db() as db:
            db.execute("""
                UPDATE reading_goals
                SET target_value = ?, current_value = ?
                WHERE id = ?
            """, (data.target_value, data.current_value, goal_id))
    return {"status": "ok"}


# 微信读书 API（Mock）
@app.get("/api/reading/current")
async def get_current_reading():
    return [
        {
            "title": "红楼梦",
            "author": "曹雪芹",
            "cover": "https://example.com/cover1.jpg",
            "bookId": "123456",
            "progress": 35,
            "chapterTitle": "第五回",
            "chapterUid": "ch5",
            "offset": 1234,
            "url": "weread://reading?bId=123456"
        }
    ]


@app.get("/api/reading/stats")
async def get_reading_stats(mode: str = "weekly"):
    return {
        "totalReadTime": 3600,
        "readDays": 5,
        "readBooks": 2,
        "totalBooks": 10,
        "compare": 15.5,
        "preferTime": [0]*24,
        "preferCategoryWord": "小说"
    }


@app.get("/api/reading/habits")
async def get_reading_habits():
    return {
        "凌晨": 10,
        "上午": 20,
        "下午": 15,
        "晚间": 45,
        "深夜": 10
    }


@app.get("/api/notes/recent")
async def get_recent_notes(limit: int = 10):
    return [
        {"text": "这是一段精彩的划线...", "chapter": "第一章", "book": "书名"},
    ]


# 主动智能 API（Mock）
@app.get("/api/proactive/questions")
async def get_proactive_questions():
    cache_key = "proactive_questions"
    if cache_key in _CACHE and datetime.now().timestamp() < _CACHE_TTL.get(cache_key, 0):
        return _CACHE[cache_key]
    
    result = {
        "questions": [
            "这段文字的核心论点是什么？",
            "作者为什么这样说？",
            "这与你之前的阅读有什么联系？"
        ]
    }
    _CACHE[cache_key] = result
    _CACHE_TTL[cache_key] = datetime.now().timestamp() + 1800
    return result


@app.get("/api/proactive/reminders")
async def get_reminders():
    return {"reminders": [{"text": "继续阅读《红楼梦》", "bookId": "123456"}]}


@app.get("/api/proactive/continuity")
async def get_continuity():
    return {"analysis": "当前章节与前文的关联分析..."}


@app.get("/api/proactive/suggestions")
async def get_suggestions():
    return {"suggestions": ["建议增加阅读时间", "尝试不同类型的书籍"]}


@app.get("/api/proactive/music")
async def get_music(mock_ai: bool = False):
    return {"playlist": [{"title": "轻音乐", "ncmId": "12345"}]}


@app.get("/api/proactive/bias")
async def get_bias(mock_ai: bool = False):
    return {
        "insight": "你偏好古典文学",
        "books": [{"title": "推荐书", "author": "作者", "why": "符合你的偏好", "bookId": "123"}]
    }


# 心智回声 API
@app.get("/api/reading/mind-echo")
async def get_mind_echo(month: str):
    return {
        "current_books": ["红楼梦"],
        "new_books": ["红楼梦"],
        "left_books": ["西游记"],
        "current_keywords": ["古典", "爱情"],
        "previous_keywords": ["神话", "冒险"],
        "current_count": 1,
        "previous_count": 1
    }


# 设置 API
@app.get("/api/settings")
async def get_all_settings():
    return get_settings()


@app.put("/api/settings/{key}")
async def update_setting(key: str, data: SettingRequest):
    async with db_lock:
        with get_db() as db:
            db.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, data.value))
    return {"status": "ok"}


@app.get("/api/cache/clear")
async def clear_cache():
    _CACHE.clear()
    _CACHE_TTL.clear()
    return {"status": "ok"}


# ==================== 静态文件 ====================
# 确保 frontend 目录存在
os.makedirs("frontend", exist_ok=True)

# SPA fallback
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    frontend_path = os.path.join("frontend", full_path)
    if os.path.exists(frontend_path) and os.path.isfile(frontend_path):
        return FileResponse(frontend_path)
    
    index_path = "frontend/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # 返回简单的欢迎页面
    return {"status": "ok", "message": "Ureader API 运行中"}


# 初始化数据库
init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)