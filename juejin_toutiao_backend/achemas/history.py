from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from achemas.news import NewsItemBase

# 添加历史记录请求类
class AddHistoryRequest(BaseModel):
    news_id:int=Field(...,alias='newsId')


# 添加历史记录响应类
class AddHistoryResponse(BaseModel):
    id:int
    user_id:int=Field(...,alias='userId')
    news_id:int=Field(...,alias='newsId')
    view_time:datetime=Field(alias='viewTime')

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

#
class HistoryItemResponse(NewsItemBase):
    history_id:int=Field(alias='historyId')
    view_time:datetime=Field(alias='viewTime')

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


# 获取浏览历史列表响应类
class HistoryListResponse(BaseModel):
    list:list[HistoryItemResponse]
    total:int
    hasMore:bool=Field(...,alias='hasMore')

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )