# FastAPI 框架：HTTPException 用于捕获业务层主动抛出的 HTTP 错误
from fastapi import HTTPException
# SQLAlchemy 异常：IntegrityError（唯一约束/外键约束冲突）、SQLAlchemyError（数据库通用错误基类）
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# 从自定义异常模块导入各类型异常的处理器函数
from util.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler, \
    general_exception_handler


def register_exception_handlers(app):
    """
    向 FastAPI 应用注册全局异常处理器

    按异常类型从具体到通用的顺序注册，FastAPI 会匹配最具体的处理器。
    注册顺序即为匹配优先级：HTTPException → IntegrityError → SQLAlchemyError → Exception（兜底）
    """
    app.add_exception_handler(HTTPException, http_exception_handler)       # HTTP 业务异常
    app.add_exception_handler(IntegrityError, integrity_error_handler)     # 数据库约束冲突（如唯一键、外键）
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)  # 数据库操作通用错误
    app.add_exception_handler(Exception, general_exception_handler)        # 兜底：捕获所有未被上述处理器拦截的异常