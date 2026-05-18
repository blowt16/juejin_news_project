from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,update
from models.news import Category,News

# 获取新闻分类数据
async def get_categories(db:AsyncSession, skip:int=0, limit:int=100):
    sql = select(Category).offset(skip).limit(limit)
    result = await db.execute(sql)
    return result.scalars().all()


# 获取新闻列表
async def get_news_list(db:AsyncSession,category_id:int,skip:int,page_size:int=10):
    sql = select(News).where(News.category_id==category_id).offset(skip).limit(page_size)
    result = await db.execute(sql)
    return result.scalars().all()


# 查询新闻总量
async def get_news_total(db:AsyncSession,category_id:int):
    sql = select(func.count(News.id)).where(News.category_id==category_id)
    result = await db.execute(sql)
    return result.scalar_one() # 获取一个结果


# 获取新闻详情数据
async def get_news_detail(db:AsyncSession,news_id:int):
    sql = select(News).where(News.id==news_id)
    news_detail = await db.execute(sql)
    return news_detail.scalar_one_or_none()


# 增加浏览量
async def increase_news_views(db:AsyncSession,news_id:int):
    # 更新数据表的数据
    sql = update(News).where(News.id == news_id).values(views = News.views+1)
    result = await db.execute(sql)
    await db.commit()
    # rowcount：数据库真正受影响的行数, 用于检查是否更新成功,成功返回true
    return result.rowcount > 0



# 查询同类型的其他新闻
async def get_other_news(db:AsyncSession,category_id:int,news_id:int,limit:int = 5):
    sql = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(), # 按照浏览量降序
        News.publish_time.desc()  # 按照发布时间降序
    ).limit(limit)
    result = await db.execute(sql)
    related_news = result.scalars().all() # 返回新闻数据对象列表
    return [
        {
           "id": news_detail.id,
           "title": news_detail.title,
           "content": news_detail.content,
           "image": news_detail.image,
           "author": news_detail.author,
           "publishTime": news_detail.publish_time,
           "categoryId": news_detail.category_id,
           "views": news_detail.views,  # 浏览量
        } for news_detail in related_news  # 遍历配置每一个新闻数据对象
    ]