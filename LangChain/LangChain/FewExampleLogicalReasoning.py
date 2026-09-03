import os

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_openai import ChatOpenAI

'''
通过少样本，实现LLM按照“某个推理逻辑”进行推理问题
'''

#定义模型
model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#定义提示词模板
example_prompt=PromptTemplate.from_template(
    template="Question:{question}\nAnswer:{answer}",
)

#定义样本实例
examples = [
{
"question": "李⽩和杜甫，谁更⻓寿？",
"answer": """
是否需要后续问题：是的。
后续问题：李⽩享年多少岁？
中间答案：李⽩享年61岁。
后续问题：杜甫享年多少岁？
中间答案：杜甫享年58岁。
所以最终答案是：李⽩

"""
},
{
"question": "腾讯的创始⼈什么时候出⽣？",
"answer": """
是否需要后续问题：是的。
后续问题：腾讯的创始⼈是谁？
中间答案：腾讯由⻢化腾创⽴。
后续问题：⻢化腾什么时候出⽣？
中间答案：⻢化腾出⽣于1971年10⽉29⽇。
所以最终答案是：1971年10⽉29⽇
""",
},
{
"question": "孙中⼭的外祖⽗是谁？",
"answer": """
是否需要后续问题：是的。
后续问题：孙中⼭的⺟亲是谁？
中间答案：孙中⼭的⺟亲是杨太夫⼈。
后续问题：杨太夫⼈的⽗亲是谁？
中间答案：杨太夫⼈的⽗亲是杨胜辉。
所以最终答案是：杨胜辉
""",
},
{
"question": "电影《红⾼粱》和《霸王别姬》的导演来⾃同⼀个国家吗？",
"answer": """
是否需要后续问题：是的。
后续问题：《红⾼粱》的导演是谁？
中间答案：《红⾼粱》的导演是张艺谋。
后续问题：张艺来⾃哪⾥？
中间答案：中国。
后续问题：《霸王别姬》的导演是谁？
中间答案：《霸王别姬》的导演是陈凯歌。
后续问题：陈凯歌来⾃哪⾥？
中间答案：中国。
所以最终答案是：是
""",
},
]

#定义少样本提示
few_examples=FewShotPromptTemplate(
    examples=examples,     #设置样本实例
    example_prompt=example_prompt,  #设置提示词模板
    suffix="Question:{input}",  # 设置样本实例，后的后缀信息
    input_variables=["input"]   #设置输入参数
)

#实例化少样本提示词
# print(few_examples.invoke({"input": "《星球大战》的导演和《阿凡达》的导演是同一个人吗"}))

#定义链
chain= few_examples | model
chain.invoke({"input": "《星球大战》的导演和《阿凡达》的导演是同一个人吗"}).pretty_print()


