import logging

from app.core.llm import get_chat_model
from app.core.prompts import EXTRACT_PROMPT
from app.schemas.structural import AfterSaleTickets, ExtractRequest
from fastapi import APIRouter, Depends, HTTPException
from langchain_core.runnables import Runnable

logger=logging.getLogger(__name__)
router=APIRouter() #使用FastAPI来实现接口调用

def get_structural()->Runnable:
    '''售后信息的提取，采用“链式结构”，因为步骤功能单一固定，无需使用agent'''
    model=get_chat_model()
    return EXTRACT_PROMPT | model.with_structured_output(AfterSaleTickets,method="function_calling")


#根据fastapi的标准，将结构化的方法，写成可以访问的接口
@router.post("/api/structural", response_model=AfterSaleTickets)
async def extract(
        req:ExtractRequest,extractor:Runnable=Depends(get_structural)
)->AfterSaleTickets:
    try:
        return await extractor.ainvoke({"text":req.text})
    except Exception as exc:
        logger.exception("结构化提取工单信息失败")
        raise HTTPException(status_code=502, detail="上游模型暂时不可用，请稍后重试") from exc






















