"""数据库连接管理。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import config


# 确保配置已加载
config.load()

DATABASE_URL = config.get("database.url", "sqlite:///./data/cv_table.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI 依赖注入：获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库表。"""
    from ..models.base import Base
    from ..models import sys, ip, case, case_execution, custom_column  # noqa: F401

    Base.metadata.create_all(bind=engine)
