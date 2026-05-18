from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# 请求数据模型文件(pydantic)

# 用户注册数据模型
class UserRequest(BaseModel):
    username:str
    password:str


# 用户信息模型
class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


# 用户响应数据类
class UserInfoResponse(UserInfoBase):
    id:int
    username:str
    # 模型配置
    model_config = ConfigDict(
        from_attributes=True  # 允许从orm对象中读取数据
    )



# data数据类
class UserAutoResponse(BaseModel):
    token:str
    user_info: UserInfoResponse = Field(...,alias='userInfo')

    # 模型配置
    model_config = ConfigDict(
        populate_by_name=True, # alias /字段兼容
        from_attributes=True # 允许从orm对象中读取数据
    )

# 用户信息更新模型类
class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None

# 用户密码更新模型类
class UserUpdatePassword(BaseModel):
    old_password: str = Field(..., alias='oldPassword',description='旧密码')
    new_password: str = Field(..., min_length=6,alias='newPassword',description='新密码')
