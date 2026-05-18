from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_config import get_database
from crud.users import get_user_by_token

# 根据token获取用户数据
async def get_current_user(
        authorization: str = Header(...,alias="Authorization"), # 去 HTTP 请求头里找 Authorization 字段，字段中存放token
        db:AsyncSession = Depends(get_database)
):
    token = authorization.replace("Bearer ","") # 去除掉token值前的 ‘Bearer’ 字段获取完整的token
    # 调用crud 根据token获取用户数据
    user = await get_user_by_token(db,token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效的令牌或已过期")

    return user
