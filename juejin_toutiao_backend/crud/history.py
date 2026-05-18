from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from models.favorite import Favorite
from models.news import News
from models.users import User
from models.history import History
from achemas.history import AddHistoryRequest
from datetime import datetime

# 添加浏览记录
async def add_history_record(db:AsyncSession,user_id:int,data:AddHistoryRequest):
    # 查询history表记录 -> 有记录：更新view_time字段 -> 没有记录：添加记录
    sql = select(History).where(History.user_id==user_id,History.news_id==data.news_id)
    result = await db.execute(sql)
    history_data = result.scalar_one_or_none()
    if history_data:
        history_data.view_time = datetime.now()
        await db.commit()
        await db.refresh(history_data)
        return history_data
    history_data = History(user_id=user_id,news_id=data.news_id)
    db.add(history_data)
    await db.commit()
    await db.refresh(history_data)
    return history_data


# 获取浏览历史列表
async def get_history_list(db:AsyncSession,user_id:int,page:int=1,page_size:int=10):
    total_sql = select(func.count(History.id)).where(History.user_id==user_id)
    result = await db.execute(total_sql)
    total = result.scalar_one_or_none()
    skip = (page-1)*page_size
    history_sql = (select(News,History.id.label('history_id'),History.view_time.label('view_time'))
                   .join(History, History.news_id == News.id)
                   .where(History.user_id==user_id)
                   .offset(skip)
                   .limit(page_size)
                   .order_by(History.view_time.desc())
                   )
    result = await db.execute(history_sql)
    rows = result.all()
    return rows,total


# 删除单条浏览记录
async def delete_one_history_record(db:AsyncSession,user_id:int,history_id:int):
    sql = delete(History).where(History.user_id==user_id,History.id==history_id)
    result = await db.execute(sql)
    await db.commit()
    return result.rowcount>0

# 清空浏览历史
async def clear_history(db:AsyncSession,user_id:int):
    sql = delete(History).where(History.user_id==user_id)
    result = await db.execute(sql)
    await db.commit()
    return result.rowcount>0

