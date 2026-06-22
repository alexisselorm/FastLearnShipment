from langchain_openai import ChatOpenAI
from app.config import app_settings
from app.ai.tools import lookup_shipment, track_shipment

# Model settings
model = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key=app_settings.OPENAI_API_KEY)

tools = [lookup_shipment, track_shipment]

llm_with_tools = model.bind_tools(tools=tools)


# ── Helpers ──
