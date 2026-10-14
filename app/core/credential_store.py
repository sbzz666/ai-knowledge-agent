"""Windows-user-bound storage for the optional DeepSeek configuration."""

from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path


class CredentialStoreError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str
    model: str = "deepseek-chat"


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _config_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return base / "KnowledgeAgent" / "deepseek-config.bin"


def _blob(data: bytes) -> tuple[_DataBlob, ctypes.Array[ctypes.c_char]]:
    buffer = ctypes.create_string_buffer(data)
    return _DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte))), buffer


def _transform(data: bytes, *, protect: bool) -> bytes:
    if os.name != "nt":
        raise CredentialStoreError("软件内安全保存仅支持 Windows。")
    source, source_buffer = _blob(data)
    result = _DataBlob()
    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    if protect:
        ok = crypt32.CryptProtectData(
            ctypes.byref(source), "Knowledge Agent DeepSeek configuration",
            None, None, None, 0, ctypes.byref(result),
        )
    else:
        ok = crypt32.CryptUnprotectData(
            ctypes.byref(source), None, None, None, None, 0, ctypes.byref(result),
        )
    if not ok:
        action = "加密" if protect else "解密"
        raise CredentialStoreError(f"Windows 无法{action} DeepSeek 配置。")
    try:
        return ctypes.string_at(result.pbData, result.cbData)
    finally:
        kernel32.LocalFree(result.pbData)
        del source_buffer


def save_config(api_key: str, model: str) -> None:
    key = api_key.strip()
    if not key:
        raise CredentialStoreError("API Key 不能为空。")
    payload = json.dumps({"api_key": key, "model": model}, ensure_ascii=False).encode()
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(_transform(payload, protect=True))
    temporary.replace(path)


def load_config() -> DeepSeekConfig | None:
    path = _config_path()
    if not path.exists():
        return None
    try:
        value = json.loads(_transform(path.read_bytes(), protect=False).decode())
        key = str(value.get("api_key", "")).strip()
        return DeepSeekConfig(key, str(value.get("model", "deepseek-chat"))) if key else None
    except (OSError, ValueError, UnicodeError, AttributeError) as exc:
        raise CredentialStoreError("本机 DeepSeek 配置已损坏，请删除后重新保存。") from exc


def delete_config() -> None:
    _config_path().unlink(missing_ok=True)
