# -*- coding: utf-8 -*-
"""
会话式请假单信息提取 & 提交（已适配 DeepSeek）
统一使用北京时间；时间解析全部交给 Time_Ca.py
"""

import os,dotenv
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from uuid import uuid4

from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI            # ← 改这里
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

import Time_Ca   # 旧模块
# from pathlib import Path

# print(">>> 当前工作目录 cwd :", os.getcwd())
# print(">>> 脚本所在目录      :", Path(__file__).resolve().parent)
# print(">>> MODEL 实际值      :", repr(os.getenv("MODEL")))
# print(">>> 找 .env 的顺序    :", [str(p) for p in Path.cwd().rglob(".env")])

# ---------- 日志 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------- FastAPI ----------
app = FastAPI(title="LeaveForm-GPT-Session")

# ---------- 北京时间 ----------
BEIJING_TZ = timezone(timedelta(hours=8))
BASE_NOW = datetime.now(BEIJING_TZ).replace(microsecond=0)

# ---------- Pydantic ----------
class LeaveRequest(BaseModel):
    workid: str = Field(..., description="用户的工号")
    LeaveType: str = Field(..., description="假别类型，如 特休假、病假、事假")
    start_iso: str = Field(..., description="请假开始时间 ISO")
    end_iso: str = Field(..., description="请假结束时间 ISO")
    LeaveProxy: str = Field(..., description="代理人姓名")
    Leavemark: str = Field(..., description="请假原因")

# ---------- 抽取器 ----------
class LeaveExtractor:
    def __init__(self):
        load_dotenv(".env")
        self.parser = PydanticOutputParser(pydantic_object=LeaveRequest)
        fmt = self.parser.get_format_instructions().replace("{", "{{").replace("}", "}}")

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是请假信息提取助手。\n"
             "1. 严格按照 JSON 格式返回。\n"
             "2. 如用户给出中文时间区间，直接把原句填入 start_iso/end_iso，不要改写成 ISO。\n"
             f"{fmt}"),
            ("user", "{input}")
        ])

        # ↓↓↓ DeepSeek 配置（兼容 OpenAI）
        self.model = ChatOpenAI(
            base_url=os.getenv("BASE_URL"),
            model=os.getenv("MODEL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.chain = prompt | self.model | self.parser

    async def aextract(self, text: str) -> Dict[str, Any]:
        try:
            parsed = await self.chain.ainvoke({"input": text})
            data = parsed.model_dump()
        except Exception as e:
            logger.warning("LLM parse error: %s", e)
            data = {}

        # 兜底解析
        raw_start = str(data.get("start_iso", ""))
        raw_end = str(data.get("end_iso", ""))
        if any(k in raw_start + raw_end for k in ("今天", "明天", "月", "点")):
            try:
                segment = (
                    f"{raw_start}到{raw_end}"
                    if "到" not in raw_start + raw_end and "至" not in raw_start + raw_end
                    else raw_start + raw_end
                )
                st, et = Time_Ca.parse_range(segment, BASE_NOW)
                data["start_iso"] = Time_Ca.fmt_iso(st)
                data["end_iso"] = Time_Ca.fmt_iso(et)
            except Exception:
                pass
        return data

# ---------- Session 管理 ----------
sessions: Dict[str, "LeaveSession"] = {}

class LeaveSession:
    def __init__(self):
        self.slot: Dict[str, Any] = {}
        self.history: list = []

    async def ask_missing(self) -> Optional[str]:
        missing = [
            k for k in ("workid", "LeaveType", "start_iso", "end_iso", "LeaveProxy", "Leavemark")
            if not self.slot.get(k)
        ]
        if not missing:
            return None

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"请用口语化一句话追问用户缺失的{','.join(missing)}"),
            MessagesPlaceholder(variable_name="messages")
        ])
        # ↓↓↓ DeepSeek 配置（兼容 OpenAI）
        model = ChatOpenAI(
            base_url=os.getenv("BASE_URL"),
            model=os.getenv("MODEL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        chain = prompt | model | StrOutputParser()
        self.history.append(HumanMessage(content="追问"))
        resp = await chain.ainvoke({"messages": self.history})
        self.history.append(AIMessage(content=resp))
        return resp

# ---------- 请求/响应 ----------
class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    status: str  # missing / confirm / submitted / error
    reply: str
    missing: Optional[list] = None
    result: Optional[Dict] = None

# ---------- 路由 ----------
extractor = LeaveExtractor()

@app.post("/chat/leave", response_model=ChatResponse)
async def chat_leave(req: ChatRequest):
    """
    请提供我具体的请假信息，
    例如：0505809 特休假 8月4号9点至8月4号11点半 去看演唱会 代理人袁帅
    """
    session_id = req.session_id or str(uuid4())
    session = sessions.setdefault(session_id, LeaveSession())

    # 提取
    info = await extractor.aextract(req.text)
    for k, v in info.items():
        if v and k in LeaveRequest.model_fields:
            session.slot[k] = v
    session.history.append(HumanMessage(content=req.text))

    # 检查缺失
    missing = [
        k for k in ("workid", "LeaveType", "start_iso", "end_iso", "LeaveProxy", "Leavemark")
        if not session.slot.get(k)
    ]
    if missing:
        question = await session.ask_missing()
        return ChatResponse(
            session_id=session_id,
            status="missing",
            reply=question,
            missing=missing,
        )

    # 等待确认
    if req.text.strip().lower() != "ok":
        preview = json.dumps(session.slot, ensure_ascii=False, indent=2)
        return ChatResponse(
            session_id=session_id,
            status="confirm",
            reply=f"请确认信息是否正确，这只是个MCP Tool示范，暂不真的提交，等后面会在Azure服务器上发布后再连HCP系统正式提交",
        )



# ---------- 启动检查 ----------
for key in ("BASE_URL", "MODEL", "OPENAI_API_KEY"):
    if not os.getenv(key):
        raise RuntimeError(f"缺少环境变量: {key}")

# ---------- CLI ----------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("LeaveForm_GPT_session:app", host="0.0.0.0", port=port, reload=True)