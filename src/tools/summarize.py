import streamlit as st

from core.ui import page_header, render_output, text_or_file_input

SYSTEM = """あなたは文章要約の専門家です。
原文の重要な情報を正確に保ち、事実を付け加えずに要約します。"""

STYLES = {
    "箇条書き": "重要なポイントを箇条書きで",
    "3行まとめ": "3行（3文）で",
    "段落（文章）": "自然な文章の段落で",
    "見出し付きレポート": "見出しで区切ったレポート形式で",
    "TL;DR + 詳細": "冒頭に1文のTL;DRを置き、その後に詳細を箇条書きで",
}


def render() -> None:
    page_header("📚 要約", "長い文章・記事・議事録などを、目的に合わせて要約します。")

    text = text_or_file_input("要約したい文章 *", "summarize", placeholder="ここに文章を貼り付けてください")
    if text:
        st.caption(f"入力文字数: {len(text):,} 字")

    col1, col2 = st.columns(2)
    style = col1.selectbox("要約スタイル", list(STYLES))
    length = col2.select_slider("要約の長さ", ["とても短く", "短く", "標準", "詳しく"], value="標準")

    col1, col2 = st.columns(2)
    extract_actions = col1.checkbox("アクションアイテム（やること）も抽出する")
    extract_keywords = col2.checkbox("キーワードも抽出する")
    focus = st.text_input("特に注目してほしい観点（任意）", placeholder="例: コスト面 / 結論と根拠")

    prompt = None
    if st.button("✨ 要約する", type="primary"):
        if not text.strip():
            st.warning("要約したい文章を入力してください。")
        else:
            extras = []
            if extract_actions:
                extras.append("最後に「アクションアイテム」として、やるべきことを箇条書きで抽出してください。")
            if extract_keywords:
                extras.append("最後に「キーワード」として重要語を5〜10個挙げてください。")
            prompt = f"""以下の文章を{STYLES[style]}、長さは「{length}」で要約してください。
{f"特に「{focus}」の観点を重視してください。" if focus else ""}
{chr(10).join(extras)}

---
{text}"""

    render_output("summarize", "要約", SYSTEM, prompt, filename="summary.md")
