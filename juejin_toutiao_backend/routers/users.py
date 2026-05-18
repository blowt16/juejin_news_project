from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_database
from crud import users
from fastapi import APIRouter, HTTPException
from achemas.users import UserRequest, UserAutoResponse, UserInfoResponse,UserInfoBase,UserUpdateRequest,UserUpdatePassword
from util.response import success_response
from util.auth import get_current_user
from models.users import User

router = APIRouter(prefix='/api/user',tags=['user'])

# 用户注册
@router.post('/register')
async def user_register(
        user_data:UserRequest,
        db:AsyncSession = Depends(get_database)
):
    # 用户注册逻辑: 检查用户是否存在 -> 添加用户 -> 生成用户token
    # 查找用户
    exist_user = await users.select_user(db,user_data.username)
    if exist_user:
        raise HTTPException(status_code=404 , detail="用户已注册")

    # 创建用户
    user = await users.create_user(db,user_data)
    if not user:
        raise HTTPException(status_code=404 , detail="注册失败")
    # 获取用户token
    token = await users.create_token(db,user.id)
#     return {
#        "code": 200,
#        "message": "注册成功",
#        "data": {
#          "token": token,
#          "userInfo": {
#            "id": user.id,
#            "username": user.username,
#            "bio": user.bio,
#            "avatar": user.avatar
#          }
#        }
# }
#     调用封装类处理数据
    response_data = UserAutoResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message='注册成功',data=response_data)


# 用户登录
@router.post('/login')
async def user_login(user_data:UserRequest,db:AsyncSession=Depends(get_database)):
    # 验证用户是否存在 -> 验证密码 -> 生成token -> 响应
    user = await users.user_login(db,user_data)
    if not user:
        raise HTTPException(status_code=401 ,detail='用户不存在')
    token = await users.create_token(db,user.id)
    # 处理响应数据 UserInfoResponse.model_validate(user) 将数据库中的orm数据转换为pydantic数据
    # orm 为数据库数据类型  pydantic 为接口数据类型
    response_data = UserAutoResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message='登录成功', data=response_data)

# 获取用户信息
@router.get('/info')
async def get_user_info(user:User = Depends(get_current_user)):
    # 获取token -> 根据token查找数据库数据 -> 检查token的期限 -> 否：获取用户的信息
    # 功能封装到了 util/get_current_user 中
    return success_response(message='获取用户信息成功', data=UserInfoResponse.model_validate(user))


# 更新用户信息
@router.put('/update')
async def update_user_info(
        new_user:UserUpdateRequest,
        current_user:User = Depends(get_current_user),
        db:AsyncSession=Depends(get_database)
):
    # 获取current_user当前用户数据 new_user用户输入数据
    update_user = await users.update_user_info(db,current_user,new_user)
    return success_response(message='修改用户信息成功',data=UserInfoResponse.model_validate(update_user))


# 修改用户密码
@router.put('/password')
async def update_user_password(
        user_password:UserUpdatePassword, # 用户输入的密码（新/旧密码）
        current_user:User = Depends(get_current_user), # 当前用户的数据（orm数据）
        db:AsyncSession = Depends(get_database)
):
    result = await users.update_user_password(db,current_user,user_password)
    if not result:
        raise HTTPException(status_code=401, detail='原密码错误')
    return success_response(message='密码修改成功',data='null')
