"""CV Table — 芯片验证 Case 管理平台 主入口。"""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .core.config import config
from .core.database import init_db
from .core.exceptions import AppError
from .api.v1.systems import router as systems_router
from .api.v1.ips import router as ips_router
from .api.v1.cases import router as cases_router
from .api.v1.stats import router as stats_router
from .api.v1.columns import router as columns_router

# ─── 配置 ────────────────────────────────────
config.load()
log_level = config.get("logging.level", "INFO")

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("cv_table")

# ─── 应用创建 ────────────────────────────────────
app = FastAPI(
    title="CV Table",
    version=config.get("app.version", "1.0.0"),
    description="芯片验证 Case 管理平台",
    docs_url="/docs",
    redoc_url=None,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 启动事件 ────────────────────────────────────

@app.on_event("startup")
def startup():
    """应用启动时初始化数据库。"""
    logger.info("正在初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")


# ─── 全局异常处理 ────────────────────────────────────

@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError):
    """统一处理应用自定义异常。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
            }
        },
    )


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception):
    """处理未预期的异常，避免泄露内部错误信息。"""
    logger.exception("未预期的异常")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "服务器内部错误", "detail": None}},
    )


# ─── API 路由注册 ────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(systems_router, prefix=API_PREFIX)
app.include_router(ips_router, prefix=API_PREFIX)
app.include_router(cases_router, prefix=API_PREFIX)
app.include_router(stats_router, prefix=API_PREFIX)
app.include_router(columns_router, prefix=API_PREFIX)


# ─── 静态文件（前端） ────────────────────────────────────

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    async def serve_frontend():
        """服务前端入口页面。"""
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "CV Table API is running. Frontend not found."}


# ─── 健康检查 ────────────────────────────────────

@app.get("/health")
def health_check():
    """健康检查端点。"""
    return {"status": "ok", "app": config.get("app.name")}
