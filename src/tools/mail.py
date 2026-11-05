import streamlit as st

from core.ui import TONES, page_header, render_output

SYSTEM = """あなたは日本語のビジネスメールに精通したアシスタントです。
相手との関係性と状況に合った、自然で失礼のないメール文を作成します。
件名と本文を出力し、不明な固有名詞や日時は【　】で囲んだプレースホルダーにしてください。"""


def render() -> None:
    page_header("✉️ メール作成・返信", "受信メールへの返信文や、新規メールの文面を考えます。")

    mode = st.radio("モード", ["返信を作成", "新規メールを作成"], horizontal=True)

    received = ""
    if mode == "返信を作成":
        received = st.text_area("受信したメール *", height=200, placeholder="返信したいメールをここに貼り付けてください")
        points = st.text_area("返信で伝えたいこと", height=100,
                              placeholder="例: 日程はOK。ただし資料の提出は来週金曜にしてほしい")
    else:
        points = st.text_area("メールの目的・伝えたいこと *", height=150,
                              placeholder="例: 取引先に打ち合わせの日程調整をお願いしたい。候補は来週火・水の午後")

    col1, col2, col3 = st.columns(3)
    relation = col1.selectbox("相手との関係", ["社外（取引先・顧客）", "上司・目上", "同僚", "部下・後輩", "友人・知人"])
    tone = col2.selectbox("トーン", TONES)
    variations = col3.number_input("パターン数", 1, 3, 1)
    signature = st.text_input("署名・差出人名（任意）", placeholder="例: 株式会社〇〇 山田")

    prompt = None
    if st.button("✨ メールを作成", type="primary"):
        if mode == "返信を作成" and not received.strip():
            st.warning("受信したメールを入力してください。")
        elif mode == "新規メールを作成" and not points.strip():
            st.warning("メールの目的を入力してください。")
        else:
            body = f"## 受信したメール\n{received}\n\n## 返信で伝えたいこと\n{points or '内容に応じて適切に返信'}" \
                if mode == "返信を作成" else f"## メールの目的・伝えたいこと\n{points}"
            prompt = f"""{"以下のメールへの返信文" if mode == "返信を作成" else "以下の内容でメール"}を作成してください。

{body}

## 条件
- 相手との関係: {relation}
- トーン: {tone}
- 差出人: {signature or "【差出人名】"}
- {variations}パターン作成し、パターンごとに「### パターンN」の見出しを付けてください。"""

    render_output("email", "メール作成・返信", SYSTEM, prompt, filename="email.md")
