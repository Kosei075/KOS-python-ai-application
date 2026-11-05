import json

import streamlit as st

from core.history import MAX_HISTORY, get_history, save_history
from core.ui import page_header, safe_markdown


def render() -> None:
    page_header("🕘 生成履歴", f"生成した結果の一覧です（data/history.json に最新 {MAX_HISTORY} 件まで保存されます）。")

    history = get_history()
    if not history:
        st.info("まだ履歴はありません。")
        return

    col1, col2 = st.columns(2)
    col1.download_button(
        "⬇️ 履歴をJSONで保存",
        json.dumps(history, ensure_ascii=False, indent=2),
        file_name="writing_history.json",
        mime="application/json",
        use_container_width=True,
    )
    with col2.popover("🗑️ 履歴をすべて削除", use_container_width=True):
        st.write("すべての履歴を削除します。元に戻せません。")
        if st.button("削除する", type="primary"):
            save_history([])
            st.rerun()

    tools = sorted({h["tool"] for h in history})
    selected = st.multiselect("ツールで絞り込み", tools)
    query = st.text_input("キーワード検索")

    for i, h in enumerate(history):
        if selected and h["tool"] not in selected:
            continue
        if query and query not in h["output"] and query not in h["request"]:
            continue
        with st.expander(f"{h['time']}｜{h['tool']}｜{h['output'][:40].replace(chr(10), ' ')}…"):
            st.markdown(safe_markdown(h["output"]))
            col1, col2 = st.columns([1, 1])
            with col1.popover("入力内容を見る", use_container_width=True):
                st.text(h["request"])
            if col2.button("この履歴を削除", key=f"del_{i}_{h['time']}", use_container_width=True):
                history.pop(i)
                save_history(history)
                st.rerun()
            st.code(h["output"], language="markdown", wrap_lines=True)
