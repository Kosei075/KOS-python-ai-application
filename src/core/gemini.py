"""Gemini API へのアクセスをまとめたモジュール。"""
from __future__ import annotations

import os
from typing import Iterator, List, Optional, Union

import streamlit as st
from google import genai
from google.genai import types

DEFAULT_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
]

# 1 回の生成の上限（思考トークンを含む）。暴走や大量消費を防ぐ
MAX_OUTPUT_TOKENS = 32768

# {"role": "user" | "model", "text": str} のリスト、または単一のプロンプト文字列
Contents = Union[str, List[dict]]


def get_env_api_key() -> str:
    """環境変数 / .env / st.secrets から API キーを取得する。"""
    key = os.getenv("GEMINI_API_KEY", "")
    if key and key != "your-api-key-here":
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _to_contents(contents: Contents) -> Union[str, List[types.Content]]:
    if isinstance(contents, str):
        return contents
    return [
        types.Content(role=m["role"], parts=[types.Part(text=m["text"])])
        for m in contents
    ]


def stream_text(contents: Contents, system: Optional[str] = None) -> Iterator[str]:
    """サイドバーの設定を使って Gemini からテキストをストリーミング取得する。"""
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        raise RuntimeError("Gemini API キーが設定されていません。サイドバーで入力してください。")

    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=st.session_state.get("temperature", 0.7),
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )
    response = get_client(api_key).models.generate_content_stream(
        model=st.session_state.get("model", DEFAULT_MODELS[0]),
        contents=_to_contents(contents),
        config=config,
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text
