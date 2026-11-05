import streamlit as st

from core.ui import page_header, render_output

SYSTEM = """あなたはクリック率の高いタイトルや心に残るキャッチコピーを生み出すコピーライターです。
誇張しすぎず、内容を正しく伝えつつ興味を引く言葉を選びます。"""

USES = ["ブログ記事タイトル", "YouTube動画タイトル", "商品・サービスのキャッチコピー",
        "メールの件名", "プレゼン・資料のタイトル", "イベント名・企画名"]


def render() -> None:
    page_header("💡 タイトル・キャッチコピー", "タイトルやキャッチコピーの案をまとめて出します。")

    subject = st.text_area("対象の内容 *", height=130,
                           placeholder="例: 初心者向けにPythonでWebアプリを作る方法を解説する記事")
    col1, col2 = st.columns(2)
    use = col1.selectbox("用途", USES)
    count = col2.slider("案の数", 5, 20, 10)
    target = st.text_input("ターゲット（任意）", placeholder="例: プログラミング未経験の社会人")

    prompt = None
    if st.button("✨ 案を出す", type="primary"):
        if not subject.strip():
            st.warning("対象の内容を入力してください。")
        else:
            prompt = f"""以下の内容について「{use}」の案を{count}個出してください。

- 内容: {subject}
- ターゲット: {target or "指定なし"}

番号付きリストで出力し、各案の後に（ ）で狙い・切り口を短く添えてください。
最後に「## おすすめ」として特に良い3案とその理由を挙げてください。"""

    render_output("headline", "タイトル・キャッチコピー", SYSTEM, prompt, filename="headlines.md")
