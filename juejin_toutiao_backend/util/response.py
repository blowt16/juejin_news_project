from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# 将 fastapi、pydantic、orm 等对象正常响应 -> code、message、data
def success_response(message:str = 'success',data=None):
    content={
        'code':200,
        'message':message,
        'data':data
    }
    # JSONResponse 返回json格式的fastapi数据对象  jsonable_encoder 将content的数据转换成json数据
    return JSONResponse(jsonable_encoder(content))