import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,update
from models.users import User,UserToken
from achemas.users import UserRequest,UserUpdateRequest,UserUpdatePassword
from util.security import get_hash_password,verify_password

# 根据username查询用户信息
async def select_user(
        db:AsyncSession,
        username:str
):
    sql = select(User).where(User.username == username)
    result = await db.execute(sql)
    return result.scalar_one_or_none()

# 创建用户
async def create_user(db:AsyncSession,user:UserRequest):
    # 密码加密
    user.password = get_hash_password(user.password)
    user_obj = User(**user.model_dump())
    db.add(user_obj) # 将数据写入内存中
    await db.commit() # 提交更改，将数据写入磁盘
    await db.refresh(user_obj) # 重新获取最新的数据对象，将磁盘数据拉取到内存
    return user_obj


# 生成用户token
async def create_token(db:AsyncSession,user_id:int):
    # 生成token -> 设置token的有效期限 -> 查询用户token信息 -> 有：更新token —> 无：添加token到数据库
    token = str(uuid.uuid4()) # 生成token
    expires_at = datetime.now()+timedelta(days=7) # 设置有效期

    sql = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(sql)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
        await db.commit()
    return token


# 用户登录
async def user_login(db:AsyncSession,user_data:UserRequest):
    # 判断用户名是否存在 -> 判断输入的密码是否与加密密码相同
    # 获取用户注册数据
    user = await select_user(db,user_data.username)
    if not user:
        return None
    if not verify_password(user_data.password,user.password):
        return None
    return user

# 通过token获取用户数据
async def get_user_by_token(db:AsyncSession,token:str):
    # 根据token查找user_token表数据 -> 判断token时效 -> 未过期则查找用户信息
    sql = select(UserToken).where(UserToken.token == token)
    result = await db.execute(sql)
    db_token = result.scalar_one_or_none()

    # 判断token时效: token有效期小于当前的时间失效
    if not db_token or db_token.expires_at < datetime.now():
        return None

    # 查找用户信息
    sql = select(User).where(User.id == db_token.user_id)
    result = await db.execute(sql)
    user = result.scalar_one_or_none()
    return user


# 更新用户数据
# 获取当前用户数据和修改后的数据 -> 更新数据库 -> 验证是否成功 -> 重新获取用户数据
async def update_user_info(db:AsyncSession, current_user:User, new_user:UserUpdateRequest):
    # new_user.model_dump() 将pydantic数据转换成orm数据   **new_user.model_dump() 将orm数据结构成键值对
    # exclude_unset=True，exclude_none=True 配置防止空字段覆盖原来的数据
    # .values(键=值) 键：数据表列名  值：orm数据
    sql = update(User).where(User.id == current_user.id).values(**new_user.model_dump(
        exclude_unset=True, # 返回用户赋值的字段
        exclude_none=True   # 删除空字段
    ))
    result = await db.execute(sql)
    await db.commit()

    # 检查是否更新成功
    if result.rowcount == 0:
        raise HTTPException(status_code=404,detail='用户不存在')

    # 重新获取用户数据
    update_user = await select_user(db,current_user.username)
    return update_user


# 修改用户密码
async def update_user_password(db:AsyncSession,current_user:User,user_password:UserUpdatePassword):
    # 判断当前用户的密码是否与用户输入的旧密码相同 -> 密码加密 -> 修改新密码
    if not verify_password(user_password.old_password,current_user.password):
        return False
    # 加密密码并更新
    hash_new_password = get_hash_password(user_password.new_password)
    sql = update(User).where(User.id == current_user.id).values(password = hash_new_password)
    result = await db.execute(sql)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404,detail='修改密码失败')
    return True

