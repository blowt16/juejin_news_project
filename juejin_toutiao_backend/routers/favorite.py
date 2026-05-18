from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud import users,favorite
from fastapi import APIRouter, HTTPException
from achemas.favorite import FavoriteCheckResponse, AddFavoriteRequest, FavoriteListResponse
from util.response import success_response
from util.auth import get_current_user
from models.users import User

router = APIRouter(prefix='/api/favorite',tags=['favorite'])

# 检查新闻收藏状态
@router.get('/check')
async def check_news_favorite(
        news_id:int=Query(...,alias='newsId'),
        current_user:User = Depends(get_current_user),
        db:AsyncSession=Depends(get_database)):
    result = await favorite.check_news_favorite(db,news_id,current_user)
    return success_response(message='检查新闻收藏状态成功',data=FavoriteCheckResponse(is_favorite=result))


# 添加收藏
@router.post('/add')
async def add_news_favorite(
        data:AddFavoriteRequest,
        current_user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_database)):
    result = await favorite.add_news_favorite(db,current_user,data.news_id)
    return success_response(message='收藏成功',data=result)


# 取消收藏
@router.delete('/remove')
async def remove_news_favorite(
        news_id:int=Query(...,alias='newsId'),
        current_user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_database)):
    result = await favorite.remove_news_favorite(db,current_user,news_id)
    if not result:
        raise HTTPException(status_code=404,detail='收藏记录不存在')
    return success_response(message='取消收藏成功')


# 获取收藏列表
@router.get('/list')
async def get_favorite_list(
        page_size:int=Query(10,alias='pageSize',le=100),
        page:int=Query(1),
        current_user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_database)):
    rows,total = await favorite.get_favorite_list(db,current_user,page,page_size)

    # 定义响应数据结构，并解构orm数据
    favorite_list = [{
        **news.__dict__, # 解构收藏的新闻数据
        'favorite_time':favorite_time,
        'favorite_id':favorite_id
    } for news,favorite_time,favorite_id in rows]

    has_more = total > page*page_size # 判断收藏的总数据量是否大于当前查看的数据量（判断是否还有更多收藏记录）
    # 使用定义的pydantic类将orm数据转换为pydantic数据
    data = FavoriteListResponse(list=favorite_list,total=total,hasMore=has_more)
    return success_response(message='新闻列表获取成功',data=data)



# 清空所有收藏
@router.delete('/clear')
async def clear_favorite_list(current_user:User=Depends(get_current_user),db:AsyncSession=Depends(get_database)):
    clear_total = await favorite.clear_favorite_list(db,current_user)
    if not clear_total:
        raise HTTPException(status_code=404,detail='清除失败')
    return success_response(message=f'成功删除{clear_total}条收藏记录')


