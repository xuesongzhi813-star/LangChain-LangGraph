import os

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.agents.middleware.tool_selection import DEFAULT_SYSTEM_PROMPT
from langchain_openai import ChatOpenAI
from langchain.tools import tool

#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    profile={"max_input_tokens":200}
)

#定义工具
@tool
def search_for_weather(city:str)->str:
    """这是一个查询天气的工具"""
    return f"{city}总是阳光明媚，晴空万里"

#生成管理上下文的线程
config={"configurable":{"thread_id":"1"}}

agent=create_agent(
    model=model,
    system_prompt="你是一个乐于助人的ai助手",
    tools=[search_for_weather],
    middleware=[
SummarizationMiddleware(
                model=model,
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                trigger=("fraction",0.1),  #摘要生成的标准：按照消息条数
                keep=("messages",2),  #生成摘要后，保留上下文中最新的两条消息
        )

        # SummarizationMiddleware(
        #         model=model,
        #         system_prompt=DEFAULT_SYSTEM_PROMPT,
        #         trigger=("messages",1),  #摘要生成的标准：按照消息条数
        #         keep=("messages",2),  #生成摘要后，保留上下文中最新的两条消息
        # )

        # SummarizationMiddleware(
        #     model=model,
        #     system_prompt=DEFAULT_SYSTEM_PROMPT,
        #     trigger=("tokens",100),  #摘要生成的标准：按照tokens限制（超出限制，则生成摘要）
        #     keep=("messages",2),  #生成摘要后，保留上下文中最新的两条消息
        # )
    ] #使用的中间件集合的定义
)

#按照tokens限制，生成摘要
# response=agent.invoke(
#     {"messages":{"role":"user","content":"现在北京的天气如何"}},
#            config=config,
# )
# print(response)
#
# print(response["messages"])
# [HumanMessage(content='Here is a summary of the conversation to date:\n\n## SESSION INTENT\nThe user asked about the current weather in Beijing, in Chinese: "现在北京的天气如何" ("What\'s the weather in Beijing right now?"). This is an unresolved informational request awaiting an assistant response.\n\n## SUMMARY\nThe conversation history contains a single human message requesting current Beijing weather conditions. No assistant reply has been made, so no conclusions, decisions, or strategies exist yet. The request requires real-time, location-specific meteorological data. An accurate response depends on live data retrieval (web search or weather API); if such tools are unavailable, the assistant should acknowledge the limitation and may offer a general or seasonal answer for Beijing instead.\n\n## ARTIFACTS\nNone.\n\n## NEXT STEPS\nAnswer the user\'s question about current weather in Beijing. If real-time data access is available, retrieve and report Beijing\'s current temperature, conditions, and any relevant details (humidity, wind, air quality, etc.). If not, inform the user that live weather data cannot be fetched and provide an appropriate alternative response.', additional_kwargs={'lc_source': 'summarization'}, response_metadata={}, id='b749b248-2e19-4ad9-a10a-9cfd577db102'),
#  AIMessage(content='我来帮您查询北京当前的天气情况。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 77, 'prompt_tokens': 363, 'total_tokens': 440, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 23, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 0, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 0, 'prompt_cache_miss_tokens': 363}, 'model_provider': 'openai', 'model_name': 'deepseek-v4-flash', 'system_fingerprint': 'a26a7955944dc5c60445bff77fac9c8e', 'id': '3b65e7bd-0c72-468c-85cf-f47d4f86206b', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--01a08059-402b-72b1-8f0a-65ba8fd986b4-0', tool_calls=[{'name': 'search_for_weather', 'args': {'city': '北京'}, 'id': 'call_00_FHVtUBRkoji0Xd3kdFZ63677', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 363, 'output_tokens': 77, 'total_tokens': 440, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 23}}),
#  ToolMessage(content='北京总是阳光明媚，晴空万里', name='search_for_weather', id='17631fbc-2778-4eed-9911-57e6e7769271', tool_call_id='call_00_FHVtUBRkoji0Xd3kdFZ63677'),
#  AIMessage(content='根据查询结果，北京当前的天气情况如下：\n\n🌞 **北京天气：晴空万里，阳光明媚**\n\n看起来今天北京天气非常好，是个阳光灿烂的日子。这样的天气很适合外出活动，不过也提醒您：\n\n- ☀️ 阳光较强，外出记得做好防晒\n- 🧢 可以戴帽子、墨镜遮挡阳光\n- 💧 注意及时补充水分\n\n如果您还需要了解温度、湿度、风力等更详细的气象数据，或者想查询其他城市的天气，随时告诉我哦！', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 145, 'prompt_tokens': 675, 'total_tokens': 820, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 37, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 256, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 256, 'prompt_cache_miss_tokens': 419}, 'model_provider': 'openai', 'model_name': 'deepseek-v4-flash', 'system_fingerprint': 'a26a7955944dc5c60445bff77fac9c8e', 'id': '004c9d0b-f805-426d-897b-0f25aa04000c', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--01a08059-633d-72f0-8a28-5080e6134acf-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 675, 'output_tokens': 145, 'total_tokens': 820, 'input_token_details': {'cache_read': 256}, 'output_token_details': {'reasoning': 37}})]


# 按照消息总数限制，生成摘要
# response=agent.invoke(
#     {"messages":{"role":"user","content":"现在北京的天气如何"}},
#            config=config,
# )
# print(response)
# print(response["messages"])
# [HumanMessage(content='Here is a summary of the conversation to date:\n\n## SESSION INTENT\n\nThe user\'s primary request is a real-time information query: they want to know the current weather in Beijing (Chinese: "现在北京的天气如何" = "How is the weather in Beijing right now?"). No assistant response has been given yet, so the session intent is simply to answer this weather query.\n\n## SUMMARY\n\n- The conversation history contains only one user message, written in Simplified Chinese, asking for Beijing\'s current weather conditions.\n- No additional context, constraints, or specific parameters (e.g., no requested time frame, units, or weather details beyond "current") were provided by the user.\n- The query is time-sensitive: weather conditions change frequently, so the answer must be based on the most up-to-date data available at the moment the assistant responds.\n- No response has been generated yet in this session. The user has not specified a preferred language for the reply, but since they wrote in Chinese, replying in Chinese would be appropriate.\n- No alternative approaches were discussed or rejected; no prior conclusions or decisions exist beyond the pending weather lookup.\n\n## ARTIFACTS\n\nNone. No files, resources, or artifacts were created, modified, or accessed during this conversation.\n\n## NEXT STEPS\n\n- Obtain current weather data for Beijing (via a weather API, web search, or similar real-time tool) and report the relevant conditions back to the user in Chinese, matching their language.\n- Include the most useful weather details in the response: current temperature, general conditions (e.g., sunny/cloudy/rainy), and ideally humidity, wind speed/direction, and possibly AQI if available.\n- Ensure the data is current at the time of responding, since the user asked specifically about "now" / "current" weather.', additional_kwargs={'lc_source': 'summarization'}, response_metadata={}, id='c505f819-0540-4452-9e11-f282aeb84c79'),
#  AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 63, 'prompt_tokens': 363, 'total_tokens': 426, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 17, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 256, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 256, 'prompt_cache_miss_tokens': 107}, 'model_provider': 'openai', 'model_name': 'deepseek-v4-flash', 'system_fingerprint': 'a26a7955944dc5c60445bff77fac9c8e', 'id': 'cc7d5698-044d-4575-940c-94c1d48fca6d', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--01a08061-0ee2-76d3-892b-dd38ecfd2e04-0', tool_calls=[{'name': 'search_for_weather', 'args': {'city': '北京'}, 'id': 'call_00_lz5rEIZb1geIrRHwsaYc9175', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 363, 'output_tokens': 63, 'total_tokens': 426, 'input_token_details': {'cache_read': 256}, 'output_token_details': {'reasoning': 17}}),
#  ToolMessage(content='北京总是阳光明媚，晴空万里', name='search_for_weather', id='7bcb8826-8d35-4142-b9dc-2fbda536beb1', tool_call_id='call_00_lz5rEIZb1geIrRHwsaYc9175'),
#  AIMessage(content='北京现在的天气是晴朗的，阳光明媚，晴空万里 ☀️\n\n如果您想了解更具体的温度、湿度或风力等信息，请告诉我，我会尽力帮您查询。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 52, 'prompt_tokens': 812, 'total_tokens': 864, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 13, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 256, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 256, 'prompt_cache_miss_tokens': 556}, 'model_provider': 'openai', 'model_name': 'deepseek-v4-flash', 'system_fingerprint': 'a26a7955944dc5c60445bff77fac9c8e', 'id': '33684c95-a390-4689-9568-888b4a492857', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--01a08061-3fe3-7870-9d08-51fd22723db7-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 812, 'output_tokens': 52, 'total_tokens': 864, 'input_token_details': {'cache_read': 256}, 'output_token_details': {'reasoning': 13}})]

#按照“当前上下文”占据“模型支持的上下文”比例
response=agent.invoke(
    {"messages":{"role":"user","content":"现在北京的天气如何"}},
           config=config,
)
print(response)
print(response["messages"])
# [HumanMessage(content='Here is a summary of the conversation to date:\n\n## SESSION INTENT\n\nThe user asked: "现在北京的天气如何" (What is the weather in Beijing right now?). Their goal is to obtain current weather conditions for Beijing.\n\n## SUMMARY\n\n- The entire conversation history consists of a single user message requesting Beijing\'s current weather.\n- No response has yet been provided by the assistant.\n- The user did not specify a date/time preference beyond "now," or any particular weather data source/metrics (temperature, conditions, wind, etc.).\n- No prior actions, conclusions, or rejected options exist in this session.\n\n## ARTIFACTS\n\nNone.\n\n## NEXT STEPS\n\n- Obtain and provide the current weather for Beijing. Since no weather data was yet gathered or presented, this likely requires querying a weather API/live source (or informing the user if live data access is unavailable).\n- Present a concise answer that directly addresses Beijing\'s current conditions.', additional_kwargs={'lc_source': 'summarization'}, response_metadata={}, id='9fc3e048-105d-4199-98ea-602d9babd379'),
#  AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 65, 'prompt_tokens': 363, 'total_tokens': 428, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 19, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 256, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 256, 'prompt_cache_miss_tokens': 107}, 'model_provider': 'openai', 'model_name': 'deepseek-v4-flash', 'system_fingerprint': 'a26a7955944dc5c60445bff77fac9c8e', 'id': 'cee96735-8271-4818-8da7-006797cdb76a', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--01a08066-2d7f-7a62-8aa0-fdb60d8c885c-0', tool_calls=[{'name': 'search_for_weather', 'args': {'city': '北京'}, 'id': 'call_00_ZF96p4haWcI1Gr8W8ZC87837', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 363, 'output_tokens': 65, 'total_tokens': 428, 'input_token_details': {'cache_read': 256}, 'output_token_details': {'reasoning': 19}}),
#  ToolMessage(content='北京总是阳光明媚，晴空万里', name='search_for_weather', id='6e6ae441-fbb3-4854-a0ee-2f7de5f9097e', tool_call_id='call_00_ZF96p4haWcI1Gr8W8ZC87837'),
#  AIMessage(content='北京目前阳光明媚，晴空万里。☀️ 是个好天气！\n\n如果你需要了解更详细的信息，比如气温、湿度或未来几天的预报，也可以告诉我。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 637, 'total_tokens': 675, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': None, 'reasoning_tokens': 0, 'rejected_prediction_tokens': None, 'text_tokens': None}, 'prompt_tokens_details': {'audio_tokens': None, 'cache_write_tokens': None, 'cached_tokens': 256, 'image_tokens': None, 'text_tokens': None}, 'prompt_cache_hit_tokens': 256, 'prompt_cache_miss_tokens': 381}, 'model_provider': 'openai', 'model_name': 'deepseek-v4-flash', 'system_fingerprint': 'a26a7955944dc5c60445bff77fac9c8e', 'id': '19beb13e-6a73-4c89-9241-1305b6c2828b', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--01a08066-4546-7913-be81-fcc4ce23aa29-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 637, 'output_tokens': 38, 'total_tokens': 675, 'input_token_details': {'cache_read': 256}, 'output_token_details': {'reasoning': 0}})]




