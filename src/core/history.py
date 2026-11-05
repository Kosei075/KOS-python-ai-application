"""生成履歴をローカルの JSON ファイルに保存・読み込みする。"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HISTORY_FILE = PROJECT_ROOT / "data" / "history.json"
MAX_HISTORY = 300


def get_history() -> List[dict]:
    """履歴を返す（初回はファイルから読み込んでセッションに保持する）。"""
    if "history" not in st.session_state:
        try:
            st.session_state["history"] = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            st.session_state["history"] = []
    return st.session_state["history"]


def save_history(history: List[dict]) -> None:
    del history[MAX_HISTORY:]
    st.session_state["history"] = history
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(HISTORY_FILE, 0o600)  # 入力内容を含むので本人以外は読めないようにする


def add_history(tool: str, request: str, output: str) -> None:
    history = get_history()
    history.insert(0, {
        "tool": tool,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "request": request,
        "output": output,
    })
    save_history(history)
