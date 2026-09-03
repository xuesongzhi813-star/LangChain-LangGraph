import os

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_openai import ChatOpenAI

#定义模型
model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

#定义少样本样例
examples=[
    {"input":"4<5","output":"20"},
    {"input":"5<6","output":"30"},
]

#定义提示词模板
example_prompt=PromptTemplate(
    template="表达式:{input},结果:{output}",
)

#定义少样本实例提示词模板
#FewShotPromptTemplate不支持“对话式提示词模板”
the_prompt=FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="输入表达式:{input}",
    input_variables=["input"],
)

#实例化少样本实例模板
# print(the_prompt.invoke({"input": "8<5"}))


#执行链
chain=the_prompt | model
chain.invoke({"input":"8<9"}).pretty_print()




