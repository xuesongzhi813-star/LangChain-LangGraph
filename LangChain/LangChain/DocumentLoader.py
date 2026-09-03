from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document

#手动定义一个“文档列表”，每一个对象都是一个Document类
# Documents=[
#     Document(
#         page_content="Hello World",
#         metadata={"source":"the_hello.doc"}
#     ),
#     Document(
#         page_content="See you again",
#         metadata={"source":"the_say.doc"}
#     )
# ]


#构造一个PDF文档加载器
# loader=PyPDFLoader(
#     file_path="../Docs/PDF/2607943.pdf"
# )
# #生成“文档列表”
# Documents=loader.load()
# #打印查看PDF文档加载器中构建出的“内容”+“原数据属性”
# # PDF文档加载器按照“页数”进行拆分
# print(f"PDF文档的总页数是：{len(Documents)}")
# #打印PDF文档列表的第一页
# print(f"文档列表的第一页内容（前200字）：{Documents[0].page_content[:200]}")
# print(f"文档列表的第一页属性：{Documents[0].metadata}")
# #打印PDF文档列表的第三页
# print(f"文档列表的第三页内容（前200字）：{Documents[2].page_content[:200]}")
# print(f"文档列表的第三页属性：{Documents[2].metadata}")


#构造一个md文档加载器
loader=UnstructuredMarkdownLoader(
    file_path="../Docs/MarkDown/脚手架级微服务租房平台Q&A.md",
    mode="elements"
)
Documents=loader.load()
#打印查看mode=single拆分方式的文档加载器，直接将“整个文档”看成一个整体
#打印查看mode=elements拆分方式的文档加载器，按照category类型分块
print(f"md文档列表的总页数是:{len(Documents)}")
print(f"md文档列表第一块的内容是:{Documents[0].page_content[:300]}")
print(f"md文档列表第一块的属性是:{Documents[0].metadata}")






