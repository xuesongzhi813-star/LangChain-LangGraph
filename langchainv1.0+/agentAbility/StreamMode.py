import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.config import get_stream_writer


@tool
def search_for_weather(city:str)->str:
    '''这是查询天气的工具'''
    #通过get_stream_writer()在custom模式下，发送自定义更新信息
    writer=get_stream_writer()
    writer(f"正在为你查询{city}的天气情况……")
    writer(f"查询到{city}的天气情况万里无云")
    #{'type': 'custom', 'ns': (), 'data': '正在为你查询南京的天气情况……'}
    #{'type': 'custom', 'ns': (), 'data': '查询到南京的天气情况万里无云'}
    return f"{city}的天气总是晴空万里"

model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

agent=create_agent(
    model=model,
    tools=[search_for_weather],
    system_prompt="你是一个乐于助人的助手，解决任务时，尽量调用工具解决"
)

for chunk in agent.stream(
    {"messages":[{"role":"user","content":"今天南京的天气如何"}]},
    # stream_mode="updates", updates模式下，观察各个阶段过程结果
    # stream_mode="messages", messages模式下，流式输出结果
    stream_mode="custom",
    version="v2"
):
    print(chunk)
    #messages模式下的输出打印
    # if chunk["type"] == "messages":
    #     token, metadata = chunk["data"]
    #     print(f"节点: {metadata['langgraph_node']}")
    #     print(f"内容块: {token.content_blocks}\n")

'''
直接进行流式输出的结果：
可以看到在哪个阶段
'model': {'messages': [AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 61, 'prompt_tokens': 309, 'total_tokens': 370, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 21, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 0, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 0, 'prompt_cache_miss_tokens': 309}, 'model_provider': 'openai', 'model_name': 'deepseek-flash', 'system_fingerprint': 'aeb56401ca74e127821c4f9126dcb669', 'id': 'f345044d-4535-4726-9eb5-795a20056f01', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--01a0a984-2817-7223-83c5-5cd4c779459a-0', tool_calls=[{'name': 'search_for_weather', 'args': {'city': '南京'}, 'id': 'call_00_VwFcn3BNtlK6Ubj3erwP2685', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 309, 'output_tokens': 61, 'total_tokens': 370, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 21}})]}}
{'tools': {'messages': [ToolMessage(content='南京的天气总是晴空万里', name='search_for_weather', id='6d13f828-d12f-42f0-bb31-66e1f4a7600e', tool_call_id='call_00_VwFcn3BNtlK6Ubj3erwP2685')]}}
{'model': {'messages': [AIMessage(content='根据查询，今天南京的天气是**晴空万里**，天气非常好，适合外出活动。☀️\n\n需要我帮您查询其他城市的天气吗？', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 90, 'prompt_tokens': 389, 'total_tokens': 479, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 54, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 128, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 261}, 'model_provider': 'openai', 'model_name': 'deepseek-flash', 'system_fingerprint': 'aeb56401ca74e127821c4f9126dcb669', 'id': 'f85fe87c-924c-43cc-a9ab-0aaae83746a2', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--01a0a984-2cfd-75b0-8c9c-69c13ab16002-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 389, 'output_tokens': 90, 'total_tokens': 479, 'input_token_details': {'cache_read': 128}, 'output_token_details': {'reasoning': 54}})]}}
'''

'''
updates模式下的输出结果：
一般用于：想观察阶段性结果
{'type': 'updates', 'ns': (), 'data': {'model': {'messages': [AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 58, 'prompt_tokens': 309, 'total_tokens': 367, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 18, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 128, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 181}, 'model_provider': 'openai', 'model_name': 'deepseek-flash', 'system_fingerprint': 'aeb56401ca74e127821c4f9126dcb669', 'id': 'b833fb28-92d9-4077-bf7a-0cd94a410681', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--01a0a986-e4c1-7de3-9999-b2e839b6fb03-0', tool_calls=[{'name': 'search_for_weather', 'args': {'city': '南京'}, 'id': 'call_00_yzolnMMGqTIB0M1bzyEA7567', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 309, 'output_tokens': 58, 'total_tokens': 367, 'input_token_details': {'cache_read': 128}, 'output_token_details': {'reasoning': 18}})]}}}
{'type': 'updates', 'ns': (), 'data': {'tools': {'messages': [ToolMessage(content='南京的天气总是晴空万里', name='search_for_weather', id='df341a68-e23c-4568-971d-bbaa38082a08', tool_call_id='call_00_yzolnMMGqTIB0M1bzyEA7567')]}}}
{'type': 'updates', 'ns': (), 'data': {'model': {'messages': [AIMessage(content='今天南京的天气是**晴空万里** ☀️，是个出门的好天气！\n\n不过这个结果比较简单，没有温度、湿度、风力等详细信息。如果你需要更具体的天气数据（如气温范围、紫外线强度、穿衣建议等），建议再查一下专业天气应用哦。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 75, 'prompt_tokens': 386, 'total_tokens': 461, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 14, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 128, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 128, 'prompt_cache_miss_tokens': 258}, 'model_provider': 'openai', 'model_name': 'deepseek-flash', 'system_fingerprint': 'aeb56401ca74e127821c4f9126dcb669', 'id': '5897ed5b-f67e-4f80-9713-f574cf7038c1', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--01a0a986-ea3f-7852-a2fd-65470c9e99c4-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 386, 'output_tokens': 75, 'total_tokens': 461, 'input_token_details': {'cache_read': 128}, 'output_token_details': {'reasoning': 14}})]}}}
F
'''





