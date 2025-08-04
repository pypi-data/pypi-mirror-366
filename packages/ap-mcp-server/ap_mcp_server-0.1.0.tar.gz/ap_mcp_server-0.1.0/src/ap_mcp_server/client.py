#!/usr/bin/env python3
import os, asyncio, json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage
import httpx
from pydantic import BaseModel   # ← 改这里

load_dotenv(".env")

TOKEN   = "tok-Angela-654321"
MCP_URL = "http://localhost:8001/mcp"

class Args(BaseModel):
    text: str

async def apply_leave(text: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            MCP_URL,
            json={"name": "apply_leave", "arguments": {"text": text}},
            headers={"token": TOKEN, "content-type": "application/json"}
        )
        return r.text          # 直接返回原始 JSON 字符串

tools = [StructuredTool.from_function(
    coroutine=apply_leave,
    name="apply_leave",
    description="请假信息提取",
    args_schema=Args
)]

async def main():
    llm = ChatOpenAI(
        base_url=os.getenv("BASE_URL", "https://api.deepseek.com/v1"),
        model=os.getenv("MODEL", "deepseek-chat"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    agent = create_react_agent(llm, tools)
    print("💬 已连接 MCP Server，输入请假信息（exit 退出）\n")
    while True:
        user = input("👉 请假：").strip()
        if user.lower() in {"exit", "quit"}:
            break
        result = await agent.ainvoke({"messages": [HumanMessage(user)]})
        print("🤖", result["messages"][-1].content, "\n")

if __name__ == "__main__":
    asyncio.run(main())