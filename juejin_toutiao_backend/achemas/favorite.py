from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from achemas.news import NewsItemBase


# 检查收藏信息的响应数据类
class FavoriteCheckResponse(BaseModel):
    is_favorite:bool=Field(...,alias='isFavorite')


# 添加收藏功能请求数据类
class AddFavoriteRequest(BaseModel):
    news_id:int = Field(...,alias='newsId')



# 收藏列表基础类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId")
    favorite_time: datetime = Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


# 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


