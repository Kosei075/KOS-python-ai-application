import streamlit as st

from core.ui import page_header, render_output

SYSTEM = """あなたはプロの翻訳者です。
直訳ではなく、翻訳先の言語のネイティブが自然に感じる表現に訳します。"""

LANGUAGES = ["英語", "日本語", "中国語（簡体字）", "韓国語", "スペイン語", "フランス語", "ドイツ語"]
STYLES = ["自然な表現", "ビジネス・フォーマル", "カジュアル", "直訳寄り（正確性重視）"]


def render() -> None:
    page_header("🌐 翻訳", "文脈を踏まえた自然な翻訳を行います。")

    text = st.text_area("翻訳したい文章 *", height=220)
    col1, col2 = st.columns(2)
    target = col1.selectbox("翻訳先の言語", LANGUAGES)
    style = col2.selectbox("スタイル", STYLES)
    explain = st.checkbox("訳のポイント（難しい表現の解説）も表示する")

    prompt = None
    if st.button("✨ 翻訳する", type="primary"):
        if not text.strip():
            st.warning("翻訳したい文章を入力してください。")
        else:
            prompt = f"""以下の文章を{target}に翻訳してください。スタイル: {style}
{"翻訳文の後に「## 訳のポイント」として、意訳した箇所や難しい表現の解説を日本語で箇条書きにしてください。" if explain else "翻訳文のみを出力してください。"}

---
{text}"""

    render_output("translate", "翻訳", SYSTEM, prompt, filename="translation.md")
