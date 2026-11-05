"""各ツールで共通して使う UI 部品。"""
from __future__ import annotations

import re
from typing import List, Optional

import streamlit as st

from core.gemini import stream_text
from core.history import add_history

TONES = ["丁寧", "フレンドリー", "カジュアル", "ビジネス", "論理的", "熱意のある", "ユーモアのある"]

REFINE_SYSTEM_SUFFIX = (
    "\n\nユーザーから修正指示があった場合は、直前の出力に指示を反映した完成版のみを出力してください。"
    "前置きや説明は不要です。"
)


# マークダウンの外部画像 ![...](https://...)。表示すると URL へ自動で通信が発生する
_EXTERNAL_IMAGE = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)[^)]*\)")


def safe_markdown(text: str) -> str:
    """外部画像を読み込まずにリンクとして表示できる形に置き換える。

    入力文に仕込まれた指示で、会話の内容を画像 URL に埋め込んで外部へ送らせる攻撃への対策。
    """
    return _EXTERNAL_IMAGE.sub(r"[画像: \1](\2)", text)


def _stream_markdown(chunks) -> str:
    """ストリーミングしながら safe_markdown を通して表示し、全文を返す。"""
    placeholder = st.empty()
    text = ""
    for chunk in chunks:
        text += chunk
        placeholder.markdown(safe_markdown(text))
    return text


def page_header(title: str, description: str) -> None:
    st.title(title)
    st.caption(description)


def _state(key: str) -> dict:
    return st.session_state.setdefault(f"tool_{key}", {"messages": [], "output": ""})


def _generate(key: str, tool: str, messages: List[dict], system: str, request: str) -> bool:
    state = _state(key)
    try:
        with st.container(border=True):
            output = _stream_markdown(stream_text(messages, system + REFINE_SYSTEM_SUFFIX))
    except Exception as e:  # API エラーは画面に表示して処理を続ける
        msg = str(e)
        if "503" in msg or "504" in msg:
            hint = "モデルが混雑しています。少し待つか、サイドバーで別のモデルに切り替えてください。"
        elif "429" in msg:
            hint = "このモデルの利用上限に達しました。別のモデルに切り替えるか、時間をおいてください。"
        elif "404" in msg:
            hint = "このモデルは利用できません。サイドバーで別のモデルを選んでください。"
        else:
            hint = ""
        st.error(f"生成に失敗しました。{hint}\n\n詳細: {msg[:300]}")
        return False
    state["messages"] = messages + [{"role": "model", "text": output}]
    state["output"] = output
    add_history(tool, request, output)
    return True


def render_output(
    key: str,
    tool: str,
    system: str,
    prompt: Optional[str] = None,
    filename: str = "output.md",
) -> None:
    """生成結果エリア。prompt が渡されたら新規生成し、それ以外は直近の結果を表示する。

    結果の下には修正指示フォーム・コピー・ダウンロードを表示する。
    """
    state = _state(key)
    pending_refine = st.session_state.pop(f"refine_{key}", None)

    st.divider()
    generated = False
    if prompt:
        generated = _generate(key, tool, [{"role": "user", "text": prompt}], system, prompt)
    elif pending_refine:
        messages = state["messages"] + [{"role": "user", "text": pending_refine}]
        generated = _generate(key, tool, messages, system, f"[修正指示] {pending_refine}")
    if not generated and state["output"]:
        with st.container(border=True):
            st.markdown(safe_markdown(state["output"]))

    output = state["output"]
    if not output:
        return

    st.caption(f"文字数: {len(output):,} 字")
    with st.expander("📋 コピー用テキスト"):
        st.code(output, language="markdown", wrap_lines=True)

    col1, col2 = st.columns([1, 1])
    col1.download_button(
        "⬇️ ダウンロード", output, file_name=filename, mime="text/markdown",
        key=f"dl_{key}", use_container_width=True,
    )
    if col2.button("🗑️ 結果をクリア", key=f"clear_{key}", use_container_width=True):
        st.session_state[f"tool_{key}"] = {"messages": [], "output": ""}
        st.rerun()

    with st.form(f"refine_form_{key}", clear_on_submit=True, border=False):
        instruction = st.text_input(
            "✏️ 修正指示（結果を元にブラッシュアップします）",
            placeholder="例: もう少し短く / 具体例を追加して / もっとカジュアルに",
        )
        if st.form_submit_button("修正する") and instruction.strip():
            st.session_state[f"refine_{key}"] = instruction.strip()
            st.rerun()


def text_or_file_input(label: str, key: str, height: int = 250, placeholder: str = "") -> str:
    """テキスト入力 + テキストファイルのアップロードを受け付ける。"""
    uploaded = st.file_uploader(
        "またはファイルをアップロード（.txt / .md）", type=["txt", "md"], key=f"file_{key}"
    )
    if uploaded is not None:
        text = uploaded.getvalue().decode("utf-8", errors="ignore")
        st.text_area(label, text, height=height, disabled=True, key=f"preview_{key}")
        return text
    return st.text_area(label, height=height, placeholder=placeholder, key=f"text_{key}")
