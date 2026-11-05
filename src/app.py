"""AI ライティングツール（Streamlit + Gemini API）"""
import hmac
import os
import socket
import time
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from dotenv import load_dotenv

from core.gemini import DEFAULT_MODELS, get_env_api_key
from tools import blog, free, headline, history, mail, minutes, proofread, sns, summarize, translate

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

st.set_page_config(page_title="AI ライティングツール", page_icon="✍️", layout="wide")

MIN_PASSWORD_LENGTH = 8


def is_this_mac() -> bool:
    """この Mac 自身（127.0.0.1 / ::1）からのアクセスかどうか。

    st.context.ip_address は WebSocket の接続元ソケットの IP で、ループバックなら None になる。
    Streamlit が使う uvicorn は X-Forwarded-For を 127.0.0.1 / ::1 からしか信用しないため、
    LAN の端末がヘッダーで「この Mac から来た」と偽ることはできない。
    """
    return st.context.ip_address is None


def phone_url(password: str) -> str:
    """同じ Wi-Fi の端末用の、合言葉入り URL（ブックマーク用）。"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("192.0.2.1", 80))  # 実際には送信しない。外向きのインターフェースの IP を知るため
        ip = s.getsockname()[0]
    return f"http://{ip}:{st.get_option('server.port')}/?key={quote(password)}"


def require_login() -> None:
    """この Mac 以外からのアクセスにだけ、.env の APP_PASSWORD（合言葉）を求める。

    スマホでは合言葉入りの URL（?key=...）をブックマークしておけば、開くだけで入れる。
    通るまではサイドバーも含めて何も表示しない。
    """
    if st.session_state.get("authenticated") or is_this_mac():
        return

    password = os.getenv("APP_PASSWORD", "")
    if len(password) < MIN_PASSWORD_LENGTH:
        st.title("✍️ AI ライティングツール")
        st.error(
            f"この Mac 以外から使うには、.env の APP_PASSWORD に {MIN_PASSWORD_LENGTH} 文字以上の合言葉を設定してください。",
            icon="🔒",
        )
        st.stop()

    key = st.query_params.get("key", "")
    if key and hmac.compare_digest(key.encode(), password.encode()):
        st.session_state["authenticated"] = True
        return

    st.title("✍️ AI ライティングツール")
    if key:
        time.sleep(1)  # 総当たりを遅くする
        st.error("URL の合言葉が違います。")
    st.info("Mac のサイドバー「📱 スマホで開く」の URL をブックマークすると、パスワード入力なしで開けます。", icon="📱")
    with st.form("login"):
        entered = st.text_input("パスワード", type="password")
        submitted = st.form_submit_button("ログイン", type="primary")
    if submitted:
        if hmac.compare_digest(entered.encode(), password.encode()):
            st.session_state["authenticated"] = True
            st.rerun()
        time.sleep(1)
        st.error("パスワードが違います。")
    st.stop()


require_login()


def sidebar_settings() -> None:
    with st.sidebar:
        st.header("⚙️ 設定")

        env_key = get_env_api_key()
        if env_key:
            st.session_state["api_key"] = env_key
            st.success("API キー: .env から読み込み済み", icon="🔑")
        else:
            st.session_state["api_key"] = st.text_input(
                "Gemini API キー", type="password",
                help="https://aistudio.google.com/apikey で取得できます。.env に GEMINI_API_KEY を書いておくと入力不要になります。",
            )

        options = DEFAULT_MODELS + ["カスタム"]
        model = st.selectbox("モデル", options)
        if model == "カスタム":
            model = st.text_input("モデル名", placeholder="例: gemini-2.5-flash")
        st.session_state["model"] = model or DEFAULT_MODELS[0]

        st.session_state["temperature"] = st.slider(
            "創造性 (temperature)", 0.0, 2.0, 0.7, 0.1,
            help="低いほど安定した出力、高いほど多様で独創的な出力になります。",
        )

        password = os.getenv("APP_PASSWORD", "")
        if is_this_mac() and len(password) >= MIN_PASSWORD_LENGTH:
            with st.expander("📱 スマホで開く"):
                st.caption("同じ Wi-Fi のスマホでこの URL を開き、ブックマークしてください。合言葉入りなので他人には見せないこと。")
                try:
                    st.code(phone_url(password), language=None, wrap_lines=True)
                except OSError:
                    st.warning("Wi-Fi につながっていないため URL を作れません。")


def page(module, title: str, icon: str, url: str, default: bool = False) -> st.Page:
    return st.Page(module.render, title=title, icon=icon, url_path=url, default=default)


sidebar_settings()

pg = st.navigation({
    "作成": [
        page(blog, "ブログ記事作成", "📝", "blog", default=True),
        page(mail, "メール作成・返信", "✉️", "email"),
        page(sns, "SNS投稿作成", "📣", "sns"),
        page(headline, "タイトル・キャッチコピー", "💡", "headline"),
    ],
    "編集・整理": [
        page(summarize, "要約", "📚", "summarize"),
        page(proofread, "校正・リライト", "🔍", "proofread"),
        page(translate, "翻訳", "🌐", "translate"),
        page(minutes, "メモ整形・議事録", "🗒️", "minutes"),
    ],
    "その他": [
        page(free, "フリープロンプト", "🧩", "free"),
        page(history, "生成履歴", "🕘", "history"),
    ],
})

if not st.session_state.get("api_key"):
    st.warning("サイドバーで Gemini API キーを設定してください。", icon="🔑")

pg.run()
