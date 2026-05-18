from fastapi import FastAPI
from routers import news,users,favorite,history
from fastapi.middleware.cors import CORSMiddleware

from util.exception_handlers import register_exception_handlers

app = FastAPI()

# 挂载全局异常捕获注册器
register_exception_handlers(app)

# 挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)


# 允许访问的来源
origins=[
    "http://localhost",
    "http://localhost:3000",
    "http://your-frontend-domain.com"
]

# 配置 CORS 中间件,解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许访问的源
    allow_credentials=True, # 允许携带cookie
    allow_methods=["*"], # 允许所有访问方法
    allow_headers=["*"], # 允许所有请求头
)



