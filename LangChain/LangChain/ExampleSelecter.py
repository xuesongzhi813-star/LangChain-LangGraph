import os

from langchain_chroma import Chroma
from langchain_community.example_selectors import NGramOverlapExampleSelector
from langchain_core.example_selectors import LengthBasedExampleSelector, SemanticSimilarityExampleSelector, \
    MaxMarginalRelevanceExampleSelector
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

#定义模型
model=ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

# 反义词⽰例集合
#长度示例选择器+语义示例选择器+MMR示例选择器，使用的示例集合
# examples = [
# {"input": "happy", "output": "sad"},
# {"input": "tall", "output": "short"},
# {"input": "energetic", "output": "lethargic"},
# {"input": "sunny", "output": "gloomy"},
# {"input": "windy", "output": "calm"},
# ]

#重叠语义示例选择器使用
examples = [
    {"input": "See Spot run.", "output": "看见Spot跑。"},
    {"input": "My dog barks.", "output": "我的狗叫。"},
    {"input": "Spot can run.", "output": "Spot可以跑。"},
]

#定义提示词模板
example_prompt=PromptTemplate.from_template(
   template="intput:{input}\noutput:{output}",
)

#定义示例选择器(按照长度选择)“按长度选择”==>适用于：示例太多+表达含义近似
#如果不能完整打印出一组示例，那么不会打印出“不完整”的那一组
# example_selector=LengthBasedExampleSelector(
#     examples=examples, #示例集合
#     example_prompt=example_prompt, #示例提示词
#     max_length=6 #输出的示例的最大长度
#     #长度函数：一般按照“\n”或者“空格”分隔
# )

# 初始化嵌入模型（硅基流动免费嵌入模型，OpenAI兼容接口）
# 注册 https://siliconflow.cn 获取 SILICONFLOW_API_KEY
embeddings = OpenAIEmbeddings(
    model="BAAI/bge-m3",  # 免费模型，中英文效果都好
    base_url="https://api.siliconflow.cn/v1",
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    check_embedding_ctx_length=False,  # bge-m3不需要token计数，关闭可避免多余请求
)

#定义示例选择器（按照语义相似选择）“按语义相似选择”==>转换成向量，比较特征
#注意：SemanticSimilarityExampleSelector构造函数只接受vectorstore等字段，
#组装“示例+嵌入模型+向量库”要用类方法from_examples()-->配置属性
# example_selector = SemanticSimilarityExampleSelector.from_examples(
#     examples=examples, #示例集合
#     embeddings=embeddings, #嵌入模型
#     vectorstore_cls=Chroma, #向量数据库
#     k=2, #选出最相似的2个示例
# )

#定义MMR示例选择器（原理：根据语义相似度判断结果-->二次排序）-->适用：推荐系统（推广广告）
#属性与语义示例选择器近似
# example_selector=MaxMarginalRelevanceExampleSelector.from_examples(
#     examples=examples, #示例集合
#     embeddings=embeddings, #嵌入模型
#     vectorstore_cls=Chroma, #向量数据库
#     k=2, #选出最相似的2个示例
# )

#定义“重叠示例选择器”（原理：“对连续重复词的数量筛选”+“语义检索”）-->适用：剽窃检查，查重
example_selector=NGramOverlapExampleSelector(
    examples=examples,
    example_prompt=example_prompt,
    threshold=0.0,
)

#定义少样本提示的模板(长度示例选择器+语义示例选择器+MMR示例选择器，使用的模板)
# few_Example_prompt=FewShotPromptTemplate(
#     example_prompt=example_prompt,
#     # examples=examples,
#     example_selector=example_selector,
#     prefix="给出输入词的反义词", #写在示例输出之前
#     suffix="输入词语:{input}\noutput:",
#     input_variables=["input"]
# )

#重叠语义示例选择器使用的“少样本提示模板”
few_Example_prompt=FewShotPromptTemplate(
    # examples=examples,  模板/选择器中一者使用“示例”即可
    example_prompt=example_prompt,
    example_selector=example_selector,
    prefix="对给定的语句翻译成中文",
    suffix="给定需要翻译的英文语句:{input}\noutput:{output}",
    input_variables=["input","output"],
)


#实例化按照长度选择的少样本提示
#invoke返回的是StringPromptValue对象，直接print显示的是repr（换行被转义）
#用to_string()取出真正的字符串，\n才会生效
print(few_Example_prompt.invoke({"input": "Spot can run rapidly","output":"Spot可以跑很快"}).to_string())

#调用测试
# chain=few_Example_prompt | model
# chain.invoke({"input":"worried"})

