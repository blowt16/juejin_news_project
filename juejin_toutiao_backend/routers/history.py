from fastapi.params import Depends, Query,Path
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud import users,favorite,history
from fastapi import APIRouter, HTTPException
from achemas.history import AddHistoryRequest, AddHistoryResponse, HistoryListResponse, HistoryItemResponse
from util.response import success_response
from util.auth import get_current_user
from models.users import User

router = APIRouter(prefix='/api/history',tags=['history'])

# 添加浏览记录
@router.post('/add')
async def add_history_record(
        data:AddHistoryRequest,
        current_user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_database)):
    history_data = await history.add_history_record(db,current_user.id,data)
    if not history_data:
        raise HTTPException(status_code=404,detail='添加历史记录失败')
    res_data = AddHistoryResponse.model_validate(history_data)
    return success_response(message='添加成功',data=res_data)


# 获取浏览历史列表
@router.get('/list')
async def get_history_list(
        page:int=Query(1,ge=1),
        page_size:int=Query(10,ge=1,le=100,alias='pageSize'),
        current_user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_database)):
    # 获取历史数据列表和total
    rows,total = await history.get_history_list(db,current_user.id,page,page_size)
    # 定义响应的数据解构
    history_list = [HistoryItemResponse.model_validate({
        **news.__dict__,
        "view_time": view_time,
        "history_id": history_id
    }) for news, history_id, view_time in rows]
    has_more = total > page*page_size
    # 将orm数据转换为pydantic数据
    response_data = HistoryListResponse(list=history_list,total=total,hasMore=has_more)
    return success_response(message='查询成功',data=response_data)


# 删除单条浏览记录
@router.delete('/delete/{history_id}')
async def delete_one_history_record(
        current_user:User=Depends(get_current_user),
        history_id:int=Path(...),
        db:AsyncSession=Depends(get_database)):
    result = await history.delete_one_history_record(db,current_user.id,history_id)
    if not result:
        raise HTTPException(status_code=404,detail='删除失败')
    return success_response(message='删除成功')


# 清空浏览历史
@router.delete('/clear')
async def clear_history(current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_database)):
    result = await history.clear_history(db,current_user.id)
    if not result:
        return success_response(message='暂无历史记录')
    return success_response(message='成功清除历史记录')