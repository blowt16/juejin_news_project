from fastapi import FastAPI
from routers import news
app = FastAPI()

# 挂载路由
app.include_router(news.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
