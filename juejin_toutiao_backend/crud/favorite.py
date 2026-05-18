from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from models.favorite import Favorite
from models.news import News
from models.users import User
from achemas.users import UserRequest,UserUpdateRequest,UserUpdatePassword
from achemas.favorite import AddFavoriteRequest

# 检查新闻收藏状态
async def check_news_favorite(db:AsyncSession,news_id:int,current_user:User):
    # 根据新闻id和用户id查找收藏数据
    sql = select(Favorite).where(Favorite.news_id==news_id,Favorite.user_id==current_user.id)
    result = await db.execute(sql)
    return result.scalar_one_or_none() is not None # 空值返回None


# 添加收藏
async def add_news_favorite(db:AsyncSession,current_user:User,news_id:int):
    # 判断是否已经收藏 -> 将收藏数据添加到数据库
    sql = select(Favorite).where(
        Favorite.news_id == news_id,
        Favorite.user_id == current_user.id
    )
    result = await db.execute(sql)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='该新闻已收藏')

    favorite_data = Favorite(user_id=current_user.id,news_id=news_id)
    db.add(favorite_data)
    await db.commit()
    # 重新获取添加的数据
    await db.refresh(favorite_data)
    return favorite_data


# 取消收藏
async def remove_news_favorite(db:AsyncSession,current_user:User,news_id:int):
    # 获取用户收藏的orm数据对象
    sql = select(Favorite).where(
        Favorite.news_id == news_id,
        Favorite.user_id == current_user.id
    )
    result = await db.execute(sql)
    favorite_data = result.scalar_one_or_none()
    if not favorite_data:
        return False
    await db.delete(favorite_data)
    await db.commit()
    return True


# 获取收藏列表
async def get_favorite_list(
        db:AsyncSession,
        current_user:User,
        page:int=1,
        page_size:int=10
):
    # 获取收藏数量 + 收藏列表

    # 获取收藏数量
    count_sql = select(func.count(Favorite.id)).where(Favorite.user_id == current_user.id)
    count_result = await db.execute(count_sql)
    total = count_result.scalar_one_or_none()

    # 获取 收藏列表
    skip = (page-1)*page_size
    # list_sql = (select(News,Favorite.created_at.label('favorite_time'),Favorite.id.label('favorite_id'))
    #        .join(Favorite,News.id == Favorite.news_id)
    #        .where(Favorite.user_id == current_user.id)
    #        .order_by(Favorite.created_at.desc())
    #        .offset(skip)
    #        .limit(page_size))
    # 以Favorite为主表
    list_sql = (select(Favorite.created_at.label('favorite_time'), Favorite.id.label('favorite_id'), News)
                .join(News, Favorite.news_id == News.id)
                .where(Favorite.user_id == current_user.id)
                .order_by(Favorite.created_at.desc())
                .offset(skip)
                .limit(page_size))
    list_result = await db.execute(list_sql)
    rows = list_result.all() # 获取多表查询的数据（row对象列表）没有获取到数据返回 []

    return rows,total


# 清空所有收藏
async def clear_favorite_list(db:AsyncSession,current_user:User):
    sql = delete(Favorite).where(Favorite.user_id == current_user.id)
    result = await db.execute(sql)
    # 获取清除的收藏记录数量
    clear_total = result.rowcount
    if not clear_total:
        return None
    return clear_total