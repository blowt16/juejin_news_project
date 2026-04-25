from fastapi import APIRouter

# 配置路由
router = APIRouter(prefix='/api/news',tags=['news'])

@router.get('/categories')
async def get_categories():
    return {'msg':'获取分类成功'}
