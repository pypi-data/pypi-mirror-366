from pydantic import BaseModel
from typing import Awaitable, Callable, Literal
from virt_llm import AsyncVLLMClient as AsyncVLLMClient

def get_chat_stream_channel(user_id: str, chat_id: str, chat_index: int): ...

class RawChatContext(BaseModel):
    user_id: str
    app_id: str
    flow_id: str
    step_name: str
    element_id: str
    prompt: str
    response: str | None
    llm_client: AsyncVLLMClient | None
    class Config:
        arbitrary_types_allowed: bool

class ProcessedChatMessage(BaseModel):
    role: Literal['user', 'system']
    content: str

class ProcessedChatContext(BaseModel):
    messages: list[ProcessedChatMessage]

class ChatInputProcessor(BaseModel):
    func: Callable[[RawChatContext], Awaitable[ProcessedChatMessage]]

class ChatSource(BaseModel):
    title: str
    description: str

class ChatOutput(BaseModel):
    text: str
    sources: list[ChatSource] | None
    def to_dict(self): ...

class ChatOutputProcessor(BaseModel):
    func: Callable[[RawChatContext], Awaitable[ChatOutput]]
    class Config:
        arbitrary_types_allowed: bool
