from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud import news

# 配置路由
# prefix 路由前缀,配置前置路径
# tags 分组标签
router = APIRouter(prefix='/api/news',tags=['news'])


# 获取新闻分类列表
@router.get('/categories')
async def get_categories(skip:int = 0, limit:int = 100, db:AsyncSession=Depends(get_database)):
    # 从数据库中查询数据
    result = await news.get_categories(db,skip,limit)
    return {'code': 200,
            'message':'success',
            'data':result
            }



#获取新闻列表
@router.get('/list')
async def get_news_list(
        # 形参不能使用驼峰命名，使用alias属性给形参起别名
        category_id:int=Query(...,alias='categoryId'),
        page:int=1,
        page_size:int=Query(10,le=100,alias="pageSize"),
        db:AsyncSession=Depends(get_database)
):
    # 调用接口函数获取新闻列表
    # 思路:处理分页逻辑 -> 查询新闻列表 ->计算总和(total) -> 计算更多(hasMore)
    # 计算跳过的新闻数量
    skip = (page - 1) * page_size
    # 获取当前页面的新闻列表
    news_list = await news.get_news_list(db,category_id,skip,page_size)
    total = await news.get_news_total(db,category_id)
    # 计算是否还有更多新闻 (跳过的新闻数量+当前页面的新闻数量) < total
    has_more = (skip + len(news_list)) < total
    return {
        "code":200,
        "message":"success",
        "data":{
            "list":news_list, # 新闻数据列表
            "total": total, #计算总和
            "hasMore": has_more # 计算更多
        }
    }


# 获取新闻详情
# 思路: 获取新闻详情->更新浏览量(数据库)->推荐同类型的其他新闻(搜索数据库数据)
@router.get('/detail')
async def get_news_detail(
        news_id:int=Query(...,alias='id'),
        db:AsyncSession=Depends(get_database)
):
    # 获取新闻详情
    news_detail = await news.get_news_detail(db,news_id)
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")

    # 更新新闻的浏览量
    result = await news.increase_news_views(db,news_id)
    if not result:
        raise HTTPException(status_code=404, detail="更新浏览量失败")

    # 获取相关新闻列表
    related_news_list = await news.get_other_news(db,news_detail.category_id,news_detail.id)
    if not related_news_list:
        raise HTTPException(status_code=404, detail="未获取到相关新闻")


    return {
       "code": 200,
       "message": "success",
       "data": {
         "id": news_detail.id,
         "title": news_detail.title,
         "content": news_detail.content,
         "image": news_detail.image,
         "author": news_detail.author,
         "publishTime": news_detail.publish_time,
         "categoryId": news_detail.category_id,
         "views": news_detail.views,  # 浏览量
         "relatedNews": related_news_list # 同类的新闻列表
     }
  }