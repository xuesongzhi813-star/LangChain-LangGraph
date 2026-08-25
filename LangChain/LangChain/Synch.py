import asyncio

#定义“协程”
async def boil_water():
    print("开始烧水")
    await asyncio.sleep(5)#设置协程的等待时间（相当于wait）
    print("烧水完成")

#定义“协程”
async def send_message():
    print("开始发送消息")
    await asyncio.sleep(2)
    print("发送消息完成")

#定义“协程”
async def main():
    #将定义的协程设置为任务
    task1=asyncio.create_task(boil_water())
    #将定义的协程设置为任务
    task2=asyncio.create_task(send_message())
    await task1
    await task2

#执行main协程，从而完成两个任务的实现
asyncio.run(main())