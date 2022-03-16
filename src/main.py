
# from dependency import authenticate_user, get_current_user
from fastapi import FastAPI
from .routers.users import user_router,normal_router,admin_router
from .routers.data import data_router
from .routers.debug import debug_router
from .exceptions import BaseException
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from .settings import Settings
app = FastAPI(docs_url=None, redoc_url=None)

app.include_router(normal_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(data_router)
app.include_router(debug_router)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

"""
DEBUG
"""
@app.exception_handler(BaseException)
async def baseexception_handler(request, exception):
    """包装错误信息
    """
    return JSONResponse({
        "code": exception.error_code,
        "message": exception.detail
    }, status_code = exception.status_code)

"""
初始化
"""
@app.on_event("startup")
async def create_temp_dir():
    import os
    tmp_path = "{}{}".format(os.getcwd(),Settings.TEMPDIR)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    else:
        import glob
        files = glob.glob(f'{tmp_path}/*')
        for f in files:
            os.remove(f)

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info",reload=True)