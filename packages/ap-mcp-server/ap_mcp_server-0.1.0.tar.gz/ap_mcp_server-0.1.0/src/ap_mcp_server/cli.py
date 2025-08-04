# run_leave_agent.py  修改版（保留上下文）
import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_deepseek import ChatDeepSeek

load_dotenv()

SYSTEM_PROMPT = """
你是小智，是明基材料有限公司请假助手，必须遵守以下规则：
1. 严格按照 JSON 格式返回。\n
2. 如用户给出中文时间区间，直接把原句填入 start_iso/end_iso，不要改写成 ISO。\n

用户用口语提供了请假信息后，你要提取这 6 个字段，规则如下：
1. workid：连续 6~8 位数字，优先取句子中第一个出现的数字串。
2. LeaveType：必须是"年假/病假/事假/特休假/调休"之一，原文匹配。
3. start_iso：格式 yyyy-mm-dd HH:MM:SS；若用户说"今天/明天"，先替换为真实日期再补时间（默认09:00:00）。
4. end_iso：同上，若只给"X点到Y点"，则日期与 start_iso 一致。
5. LeaveProxy：人名，原文提取。
6. Leavemark：剩余文字作为请假事由。

如果缺字段，立刻追问"还差 X，请补充"。  
如果全齐了，就可以按 JSON 返回：  
{"workid":"","LeaveType":"","start_iso":"","end_iso":"","LeaveProxy":"","Leavemark":""}
"""


async def async_main():
    """原主逻辑，保持异步"""
    client = MultiServerMCPClient(
        {
            "leave": {
                "command": "python",
                "args": ["mcp_leave_server.py"],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()
    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    agent = create_react_agent(llm, tools, state_modifier=SYSTEM_PROMPT)

    print("""💬 DeepSeek 明基材料请假助手小智已上线，输入 exit 退出
            请提供以下请假信息：
            - workid      : 请提供您的工号：
            - LeaveType   : 请确认请假类型（年假/病假/事假/特休假等）：
            - start_iso   : 请提供开始时间（如：明天上午9点）：
            - end_iso     : 请提供结束时间（如：明天下午4点）：
            - LeaveProxy  : 请提供工作代理人姓名：
            - Leavemark   : 请补充请假事由：

            列如：0505889 特休假 今天上午9点到今天下午3点 去上海看看海啸吹吹风 代理人袁帅
            """)

    messages = []  # 保存完整对话历史
    while True:
        user = input("👉 你：").strip()
        if user.lower() in {"exit", "quit"}:
            break
        messages.append(("human", user))
        result = await agent.ainvoke({"messages": messages})
        ai_reply = result["messages"][-1].content
        messages.append(("ai", ai_reply))
        print("🤖", ai_reply, "\n")


def main():
    """CLI 统一入口（第3步要求）"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()