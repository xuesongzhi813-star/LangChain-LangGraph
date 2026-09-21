#使用“内存级存储”/“三方存储库”完成“跨会话存储”
import uuid

from langgraph.store.memory import InMemoryStore

#定义“内存级存储”
store=InMemoryStore()

#定义隔离
#使用“元组”
user_id="user_123"
namespace1=(user_id,"preference","food")
namespace2=(user_id,"preference","flower")

#定义记忆键
memory_id1="7qdwd5"
memory_id2="9qdwdq"

#定义value-->字典，表示这方面信息是什么，可以存多条
value1={"food":"pizza"}
value2={"flower":"Rose flower"}

#存储
store.put(namespace1,memory_id1,value1)
store.put(namespace2,memory_id2,value2)

#查找
result=store.search((user_id,"preference"),)
for item in result:
    print(item)






