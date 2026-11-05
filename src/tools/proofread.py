import streamlit as st

from core.ui import TONES, page_header, render_output

SYSTEM = """あなたは経験豊富な日本語の編集者・校正者です。
原文の意図を尊重しながら、正確で読みやすい文章に整えます。"""

MODES = {
    "校正（誤字脱字・文法チェック）":
        "誤字脱字・文法・表記ゆれ・不自然な表現を修正してください。"
        "まず「## 修正後の文章」を出力し、次に「## 修正箇所」として 修正前 → 修正後（理由）の一覧を表で示してください。",
    "読みやすくリライト":
        "意味を変えずに、一文を短くする・冗長な表現を削る・論理の流れを整えるなどして読みやすくリライトしてください。",
    "トーンを変換":
        "内容を保ったまま、指定したトーンの文章に書き換えてください。",
    "文字数を調整":
        "要点を保ったまま、指定した文字数に近づくよう書き換えてください。",
    "フィードバックのみ":
        "文章は書き換えず、良い点・改善点・具体的な改善案を箇条書きでフィードバックしてください。",
}


def render() -> None:
    page_header("🔍 校正・リライト", "誤字脱字のチェック、読みやすい文章への書き換え、トーン変換などを行います。")

    text = st.text_area("対象の文章 *", height=250, placeholder="ここに文章を貼り付けてください")
    if text:
        st.caption(f"入力文字数: {len(text):,} 字")

    mode = st.selectbox("処理内容", list(MODES))
    extra = ""
    if mode == "トーンを変換":
        tone = st.selectbox("変換後のトーン", TONES + ["だ・である調", "です・ます調"])
        extra = f"変換後のトーン: {tone}"
    elif mode == "文字数を調整":
        target = st.number_input("目標文字数", 50, 10000, max(100, len(text) // 2 // 50 * 50 or 100), step=50)
        extra = f"目標文字数: 約{target}字"

    prompt = None
    if st.button("✨ 実行", type="primary"):
        if not text.strip():
            st.warning("対象の文章を入力してください。")
        else:
            prompt = f"""{MODES[mode]}
{extra}

---
{text}"""

    render_output("proofread", "校正・リライト", SYSTEM, prompt, filename="proofread.md")
