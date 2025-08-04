#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
请假小智 – 最终可直接替换版（SSE 纯文本输入）
"""

import uuid
import logging
from typing import Dict, Any, Optional

from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(".env")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from LeaveForm_GPT_session import LeaveSession, LeaveExtractor

sessions: Dict[str, LeaveSession] = {}
extractor = LeaveExtractor()
mcp = FastMCP("LeaveAssistant")


@mcp.tool()
async def apply_leave(
    text: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    text = text.strip()
    session_id = session_id or str(uuid.uuid4())
    session = sessions.setdefault(session_id, LeaveSession())

    logging.info(">>> apply_leave start, text=%s", text)

    try:
        # 1. 引导
        if not text or text.lower() in {"start", "help"}:
            return {
                "session_id": session_id,
                "status": "guide",
                "reply": (
                    "请假小智已上线，请告诉我：\n"
                    "1. 工号\n2. 请假类型（年假/病假/事假/特休假…）\n"
                    "3. 开始时间（如：明天上午9点）\n"
                    "4. 结束时间（如：明天下午4点）\n"
                    "5. 工作代理人\n6. 请假事由\n\n"
                    "示例：0505809 特休假 明天9点到16点 代理袁帅 去上海看AI展"
                ),
            }

        # 2. 解析并回填
        try:
            info = await extractor.aextract(text)
        except Exception as e:
            logging.exception("aextract error")
            raise

        for k, v in info.items():
            if v and k in (
                "workid", "LeaveType", "start_iso",
                "end_iso", "LeaveProxy", "Leavemark"
            ):
                session.slot[k] = v
        session.history.append(text)

        # 3. 缺失追问
        questions = {
            "workid":      "请提供您的工号：",
            "LeaveType":   "请确认请假类型（年假/病假/事假/特休假等）：",
            "start_iso":   "请提供开始时间（如：明天上午9点）：",
            "end_iso":     "请提供结束时间（如：明天下午4点）：",
            "LeaveProxy":  "请提供工作代理人姓名：",
            "Leavemark":   "请补充请假事由：",
        }
        missing = [k for k in questions if not session.slot.get(k)]

        if missing:
            first = missing[0]
            prompt = questions[first]
            return {
                "session_id": session_id,
                "status": "missing",
                "reply": prompt,
            }

        # 4. 确认
        if text.lower() not in {"ok", "确认"}:
            preview = (
                "请确认以下请假信息：\n"
                f"工号：{session.slot['workid']}\n"
                f"请假类型：{session.slot['LeaveType']}\n"
                f"开始时间：{session.slot['start_iso']}\n"
                f"结束时间：{session.slot['end_iso']}\n"
                f"工作代理人：{session.slot['LeaveProxy']}\n"
                f"请假事由：{session.slot['Leavemark']}\n\n"
                "回复“确认”即可提交，回复“修改”可重新填写。我目前还没有对接HCP，需要公司授权才能对接。"
            )
            return {
                "session_id": session_id,
                "status": "confirm",
                "reply": preview,
            }

        # 5. 提交
        payload = {
            "workid": session.slot["workid"],
            "LeaveType": session.slot["LeaveType"],
            "start_iso": session.slot["start_iso"],
            "end_iso": session.slot["end_iso"],
            "LeaveProxy": session.slot["LeaveProxy"],
            "Leavemark": session.slot["Leavemark"],
        }
        logging.info("提交请假：%s", payload)
        sessions.pop(session_id, None)
        return {
            "session_id": session_id,
            "status": "success",
            "reply": "提交成功！已为您完成请假申请。",
        }

    finally:
        logging.info("<<< apply_leave done, result=%s", locals().get("result", "exception"))


# ---------------- 尾部 ----------------
def main():
    """Console-script 入口：stdio 模式"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    # 直接调试时仍可用 SSE
    import sys
    if "--sse" in sys.argv:
        mcp.run(transport="sse", host="0.0.0.0", port=8001)
    else:
        main()

