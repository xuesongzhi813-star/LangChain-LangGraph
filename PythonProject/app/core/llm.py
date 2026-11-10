from config import settings
from langchain_openai import ChatOpenAI
#第一部分，先定义LLM出来
#采用工厂模式，负责实例化出符合需求的model使用
def get_chat_model(streaming: bool = False, model: str | None = None,
                   temperature: float | None = None,
                   thinking: bool = False) -> ChatOpenAI:
    """直连 DeepSeek 上游(OpenAI 协议)。

    model 显式覆盖模型名,None 时回落 settings.model。
    stream_usage=True:流式也回传 token,统一 usage 统计口径。

    temperature 默认 0.3(答用户的话要有点人味)。**当评委用的链路要显式传 0**:
    同一份证据+同一份答案,0.3 下重放四次给出过 5/6、5/6、6/6、6/6 三种结果,
    量出来的分数里就混进了采样噪声——评估要的是可复现,不是多样性。

    thinking=False 显式关闭思考链。structured() 用它:DeepSeek 的 thinking 和
    tool_choice 指定函数互斥(思考模式下不支持 required 和指定具体 tool),
    结构化输出走 function_calling 必须关。不能只是不传——不传等于跟随上游默认,
    所以 False 时显式发 disabled。"""
    return ChatOpenAI(
        model=model or settings.model, #设置模型名称
        base_url=settings.base_url,
        api_key=settings.deepseek_api_key,
        streaming=streaming,
        stream_usage=True,
        max_tokens=settings.token_budget,   # Y:保险丝,防模型失控输出
        temperature=0.3 if temperature is None else temperature,
        extra_body={"thinking": {"type": "enabled" if thinking else "disabled"}},
    )
