import streamlit as st

from core.ui import TONES, page_header, render_output

SYSTEM = """あなたはSNSマーケティングに詳しいコピーライターです。
各プラットフォームの特性（文字数・文化・ハッシュタグの使い方）を踏まえ、反応が得られる投稿文を作ります。"""

PLATFORMS = {
    "X (Twitter)": "140字以内（全角）",
    "Instagram": "キャプションとして読みやすい改行を入れ、最後にハッシュタグ",
    "Threads": "500字以内で会話的に",
    "LinkedIn": "ビジネス向けで、学びや気づきが伝わる構成",
    "Facebook": "親しみやすく、適度な長さ",
    "note / ブログ告知": "記事を読みたくなる告知文",
}


def render() -> None:
    page_header("📣 SNS投稿作成", "伝えたい内容から、各SNS向けの投稿文を作ります。")

    content = st.text_area("投稿したい内容 *", height=150,
                           placeholder="例: 新しいブログ記事「在宅ワークで集中力を保つコツ」を公開した")
    col1, col2, col3 = st.columns(3)
    platform = col1.selectbox("プラットフォーム", list(PLATFORMS))
    tone = col2.selectbox("トーン", TONES)
    count = col3.number_input("案の数", 1, 5, 3)

    col1, col2 = st.columns(2)
    hashtags = col1.checkbox("ハッシュタグを付ける", value=True)
    emoji = col2.checkbox("絵文字を使う", value=True)

    prompt = None
    if st.button("✨ 投稿文を作成", type="primary"):
        if not content.strip():
            st.warning("投稿したい内容を入力してください。")
        else:
            prompt = f"""以下の内容で {platform} 向けの投稿文を{count}案作成してください。

## 内容
{content}

## 条件
- プラットフォームの特性: {PLATFORMS[platform]}
- トーン: {tone}
- ハッシュタグ: {"付ける" if hashtags else "付けない"}
- 絵文字: {"適度に使う" if emoji else "使わない"}
- 案ごとに「### 案N」の見出しを付け、切り口（共感型・数字型・問いかけ型など）を変えてください。"""

    render_output("sns", "SNS投稿作成", SYSTEM, prompt, filename="sns.md")
