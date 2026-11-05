import streamlit as st

from core.ui import page_header, render_output

PRESETS = {
    "汎用アシスタント": "あなたは優秀な日本語ライティングアシスタントです。",
    "プレスリリース": "あなたは広報担当者です。5W1Hを押さえたプレスリリースを作成します。",
    "自己紹介・プロフィール": "あなたはキャリアアドバイザーです。魅力が伝わる自己紹介文を作成します。",
    "スピーチ原稿": "あなたはスピーチライターです。聞き手の心に届く、話し言葉の原稿を作成します。",
    "商品説明文": "あなたはECサイトのコピーライターです。購買意欲を高める商品説明文を作成します。",
}


def render() -> None:
    page_header("🧩 フリープロンプト", "役割（システムプロンプト）と指示を自由に設定して文章を作成します。")

    preset = st.selectbox("役割のプリセット", list(PRESETS))
    system = st.text_area("役割（システムプロンプト）", PRESETS[preset], height=80, key=f"system_{preset}")
    instruction = st.text_area("指示 *", height=200, placeholder="作ってほしい文章の内容や条件を自由に書いてください")

    prompt = None
    if st.button("✨ 生成", type="primary"):
        if not instruction.strip():
            st.warning("指示を入力してください。")
        else:
            prompt = instruction

    render_output("free", "フリープロンプト", system, prompt, filename="output.md")
