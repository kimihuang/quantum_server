"""配置加载器 — 从 YAML 文件加载配置，支持环境覆盖。"""

import os
import yaml
from pathlib import Path
from typing import Any


def _deep_merge(base: dict, override: dict) -> dict:
    """深度合并两个字典，override 覆盖 base。"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


class Config:
    """应用配置单例。"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self) -> None:
        """加载配置。"""
        if self._loaded:
            return

        config_dir = Path(__file__).resolve().parent.parent / "config"
        self._data: dict = {}

        # 加载默认配置
        default_path = config_dir / "default.yaml"
        if default_path.exists():
            with open(default_path, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or {}

        # 加载环境配置，覆盖默认值
        env = os.getenv("APP_ENV", "development")
        env_path = config_dir / f"{env}.yaml"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                env_data = yaml.safe_load(f) or {}
                _deep_merge(self._data, env_data)

        self._loaded = True

    def get(self, key_path: str, default: Any = None) -> Any:
        """通过点分隔路径获取配置值，例如 config.get('server.port')。"""
        if not self._loaded:
            self.load()

        keys = key_path.split(".")
        value = self._data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def all(self) -> dict:
        """返回所有配置。"""
        if not self._loaded:
            self.load()
        return self._data


# 全局单例
config = Config()
