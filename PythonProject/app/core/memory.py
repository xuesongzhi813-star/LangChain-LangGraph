from langchain_core.messages import BaseMessage, trim_messages


#近似 token 计数:中文约 1 字 ≈ 1 token,英文约 4 字符 ≈ 1 token,再给每条消息留点结构开销。
#只用于裁剪历史的粗略预算,不用于计费。
def count_tokens_approximately(messages: list[BaseMessage]) -> int:
    total = 0
    for m in messages:
        content = m.content if isinstance(m.content, str) else str(m.content)
        cjk = sum(1 for ch in content if '一' <= ch <= '鿿')
        other = len(content) - cjk
        total += 4 + cjk + other // 4
    return total



class SessionStore:
    """内存会话存储,session_id -> 消息列表。本章不做持久化。"""

    def __init__(self) -> None:
        self._sessions: dict[str, list[BaseMessage]] = {}

    def get(self, session_id: str) -> list[BaseMessage]:
        return self._sessions.get(session_id, [])

    def append(self, session_id: str, *messages: BaseMessage) -> None:
        self._sessions.setdefault(session_id, []).extend(messages)

#历史消息的裁剪-->trim
def trim_history(max_tokens:int,messages:list[BaseMessage])->list[BaseMessage]:
    return trim_messages(
        messages=messages,
        max_tokens=max_tokens,
        start_on="human", #起始消息类型
        strategy="last", #裁剪策略，保留最新的消息
        allow_partial=False, #不允许拆分出“不完整的消息内容”
        token_counter=count_tokens_approximately,
    )






