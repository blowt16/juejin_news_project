from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession


# 异步 MySQL 数据库连接地址
# 格式: mysql+aiomysql://用户名:密码@地址:端口/数据库名?参数
ASYNC_DATABASE_URL = "mysql+aiomysql://root:root123@localhost:3306/news_app?charset=utf8"

# 创建异步数据库引擎（连接池）
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,    # 数据库连接地址
    echo=True,             # 打印 SQL 语句（调试用，生产环境建议设为 False）
    pool_size=10,          # 连接池常驻连接数
    max_overflow=20,       # 连接池最大溢出连接数（临时额外连接）
)



# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,    # 绑定数据库连接引擎
    class_=AsyncSession,    # 指定会话类
    expire_on_commit=False # 提交后会话不会过期
)



# 配置会话对象的依赖
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # 提交事务
        except Exception as e:
            await session.rollback() #事务回滚
            raise
        finally:
            await session.close()  # 关闭会话