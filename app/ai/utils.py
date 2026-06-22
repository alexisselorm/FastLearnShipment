from langchain_core.messages import HumanMessage, SystemMessage
from app.database.models import ChatMessage
from sqlalchemy import select
from app.database.session import get_session
from uuid import UUID
SYSTEM_PROMPT = """You are a helpful shipment assistant for FastShip. You can look up shipments, sellers, and delivery partners using the available tools. Answer concisely and accurately."""


async def load_session(session_id: str) -> list:
    """Load existing conversation from DB as LangChain message list."""
    async for s in get_session():
        result = await s.execute(
            select(ChatMessage).where(
                ChatMessage.session_id == UUID(session_id))
            .order_by(ChatMessage.created_at)
        )
        db_messages = result.scalars().all()
        lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for m in db_messages:
            if m.role == "user":
                lc_messages.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                from langchain_core.messages import AIMessage
                lc_messages.append(AIMessage(content=m.content))
        return lc_messages


async def save_messages(session_id: str, *msgs: tuple[str, str]):
    """Persist (role, content) pairs to DB."""
    async for s in get_session():
        for role, content in msgs:
            s.add(ChatMessage(
                session_id=UUID(session_id),
                role=role,
                content=content,
            ))
        await s.commit()
