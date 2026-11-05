"""全ツールの描画・生成・修正指示・履歴保存を、Gemini をモックして確認するスモークテスト。

実行: .venv/bin/python scripts/smoke_test.py
API キーは不要。実際の履歴ファイル (data/history.json) には書き込まない。
"""
import json
import os
import sys
import tempfile
import warnings
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
os.chdir(ROOT)
warnings.filterwarnings("ignore")

from streamlit.testing.v1 import AppTest  # noqa: E402

TOOLS = ["blog", "mail", "sns", "headline", "summarize", "proofread", "translate", "minutes", "free"]


def fake_stream(contents, system=None):
    turns = len(contents) if isinstance(contents, list) else 1
    yield f"OK(turns={turns})"


def check_tool(name: str, history_file: Path) -> None:
    script = f"""
import sys; sys.path.insert(0, {str(SRC)!r})
from pathlib import Path
import streamlit as st
import core.ui, core.history
core.ui.stream_text = lambda contents, system=None: iter(["OK"])
core.history.HISTORY_FILE = Path({str(history_file)!r})
st.session_state["api_key"] = "dummy"
from tools import {name}
{name}.render()
"""
    at = AppTest.from_string(script, default_timeout=30).run()
    assert not at.exception, at.exception
    for ta in at.text_area:
        if not ta.disabled:
            ta.set_value("テスト入力")
    for ti in at.text_input:
        if "修正指示" not in ti.label:
            ti.set_value("テスト")
    next(b for b in at.button if "✨" in b.label).click().run()
    assert not at.exception, at.exception
    assert any(m.value == "OK" for m in at.markdown), f"{name}: 生成結果が表示されない"


def app_env(**env):
    """app.py を、本物の .env を読まずにテスト用の環境変数で動かす。"""
    return mock.patch("dotenv.load_dotenv"), mock.patch.dict(os.environ, env)


def access_from(ip):
    """接続元の IP を固定する（AppTest では st.context.ip_address がモックの値になるため）。"""
    return mock.patch("streamlit.runtime.context.ContextProxy.ip_address",
                      new_callable=mock.PropertyMock, return_value=ip)


def from_mac():
    return access_from(None)  # この Mac 自身（ループバック）からは None


def from_phone():
    return access_from("192.168.11.20")


def tools_shown(at: AppTest) -> bool:
    return any("✨" in b.label for b in at.button)


def new_app() -> AppTest:
    return AppTest.from_file(str(SRC / "app.py"), default_timeout=30)


def check_access() -> None:
    no_dotenv, env = app_env(GEMINI_API_KEY="dummy")
    with no_dotenv, env, from_mac():
        at = new_app().run()
        assert tools_shown(at), "この Mac から使えない"
        assert any("📱" in e.label for e in at.sidebar.expander), "Mac のサイドバーにスマホ用 URL が無い"

    with no_dotenv, env, from_phone():
        at = new_app().run()
        assert not at.exception, at.exception
        assert tools_shown(at), "スマホから使えない"
        assert not at.sidebar.expander, "スマホにスマホ用 URL が表示されている"


def check_refine_and_history(history_file: Path) -> None:
    no_dotenv, env = app_env(GEMINI_API_KEY="dummy")
    with mock.patch("core.ui.stream_text", fake_stream), \
            mock.patch("core.history.HISTORY_FILE", history_file), no_dotenv, env, from_mac():
        at = new_app().run()
        assert not at.exception, at.exception
        at.text_input[0].set_value("テーマ")
        next(b for b in at.button if "✨" in b.label).click().run()
        next(t for t in at.text_input if "修正指示" in t.label).set_value("短く")
        next(b for b in at.button if b.label == "修正する").click().run()
        assert not at.exception, at.exception
        assert any("OK(turns=3)" in m.value for m in at.markdown), "修正指示が会話履歴付きで送られていない"

    saved = json.loads(history_file.read_text(encoding="utf-8"))
    assert len(saved) >= 2 and saved[0]["request"].startswith("[修正指示]"), "履歴がファイルに保存されていない"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        history_file = Path(tmp) / "history.json"
        failed = 0
        for name in TOOLS:
            try:
                check_tool(name, history_file)
                print(f"✅ {name}")
            except Exception as e:
                failed += 1
                print(f"❌ {name}: {e}")
        try:
            check_access()
            print("✅ アクセス（Mac・スマホとも合言葉なし）")
        except Exception as e:
            failed += 1
            print(f"❌ アクセス: {e}")
        try:
            check_refine_and_history(Path(tmp) / "history_app.json")
            print("✅ 生成 → 修正指示 → 履歴保存")
        except Exception as e:
            failed += 1
            print(f"❌ 生成 → 修正指示 → 履歴保存: {e}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
