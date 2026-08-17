"""LLM 调用通用工具（从被移除的旧版 test_run 服务中提取）。

保留给 prompt_test_engine 等新引擎复用的纯函数与常量，
避免新引擎依赖已废弃的旧版单次测试服务。
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

# 单 Provider 默认并发上限（与 llm_models.concurrency_limit 默认值一致）
DEFAULT_CONCURRENCY_LIMIT = 5

# 请求间隔（秒），用于温和限速，避免触发供应商限流
REQUEST_SLEEP_RANGE = (0.05, 0.2)


def _format_error_detail(payload: Any) -> str:
    """从 LLM 错误响应中提取人类可读的错误详情。"""

    if isinstance(payload, Mapping):
        error_obj = payload.get("error")
        if isinstance(error_obj, Mapping):
            message_parts: list[str] = []
            code = error_obj.get("code")
            if isinstance(code, str) and code.strip():
                message_parts.append(code.strip())
            error_type = error_obj.get("type")
            if isinstance(error_type, str) and error_type.strip():
                message_parts.append(error_type.strip())
            message = error_obj.get("message")
            if isinstance(message, str) and message.strip():
                prefix = " | ".join(message_parts)
                return f"{prefix}: {message.strip()}" if prefix else message.strip()
        message = payload.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
        try:
            return json.dumps(payload, ensure_ascii=False)
        except Exception:  # pragma: no cover - 容错
            return str(payload)
    return str(payload)


def _try_parse_json(text: str) -> Any:
    """尝试将文本解析为 JSON，失败返回 None。"""

    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None


__all__ = [
    "DEFAULT_CONCURRENCY_LIMIT",
    "REQUEST_SLEEP_RANGE",
    "_format_error_detail",
    "_try_parse_json",
]
