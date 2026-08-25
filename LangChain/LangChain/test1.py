from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
import os

#1.定义OpenAI模型
#langchain_openai默认只认OPENAI_API_KEY环境变量，这里显式从DEEPSEEK_API_KEY传入
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"))

#2.定义消息
#用户消息：HumanMessage
#系统提示消息：SyetemMessage 通常作为第一条消息传入
messages = [
    SystemMessage(content="请帮我进行翻译，由中文翻译成英文"),
    HumanMessage(content="大风起兮云飞扬")
]

#3.调用大模型
# result=model.invoke(messages)
# print(result)

#4.定义输出解析
parser=StrOutputParser()
# print(parser.invoke(result))

#5.定义链
#上面其实就是定义“组件”+“消息”，组件（调用模型+输出解析），最终只需要执行“串通组件”的链即可
#执行链，链打印只会打印context内容部分
chain=model | parser
#chain本质RunnableSequence
# chain=RunnableSequence(first=model,last=parser)

#仅当直接运行本文件时才执行调用，被其他文件import时不会触发
if __name__ == "__main__":
    print(chain.invoke(messages))