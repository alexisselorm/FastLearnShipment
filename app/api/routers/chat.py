from fastapi import APIRouter
from app.schemas.chat import ChatResponse, ChatRequest
from uuid import UUID, uuid4
from app.database.models import ChatSession
from app.ai.utils import load_session, save_messages
from app.ai.rag import llm_with_tools, tools
from app.database.session import get_session
from langchain_core.messages import HumanMessage, ToolMessage

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid4())
    if not body.session_id:
        async for s in get_session():
            s.add(ChatSession(id=UUID(session_id)))
            await s.commit()

    messages = await load_session(session_id)
    messages.append(HumanMessage(content=body.message))

    response = llm_with_tools.invoke(messages)

    while response.tool_calls:
        print("Tool calls detected, invoking tools...")
        print(response.tool_calls)
        print(response)
        print(type(response))
        print(
            f"Invoking tool: {response.tool_calls[0].name} with input: {response.tool_calls[0].input}")

        messages.append(response)
        for tc in response.tool_calls:
            tool_fn = next(t for t in tools if t.name == tc["name"])
            result = await tool_fn.ainvoke(tc["args"])
            messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))
        response = await llm_with_tools.invoke(messages)

    messages.append(response)

    await save_messages(session_id, ("user", body.message), ("assistant", response.content))

    return ChatResponse(session_id=session_id, reply=response.content)
