# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

Streamlit + Gemini API（`google-genai` SDK）で作った個人用 AI ライティングツール。DB なし。同じ Wi-Fi のスマホからも使えるよう LAN に公開している（`server.address = "0.0.0.0"`）。合言葉などのログインはなく、同じ Wi-Fi の端末なら誰でも使える（ユーザーの選択）。この Mac かどうか（`st.context.ip_address is None`、ループバック）は、サイドバーの「📱 スマホで開く」を Mac だけに出すために使う。AppTest ではこの値がモックになるので、スモークテストは `from_mac()` / `from_phone()` で固定している。UI 文言・プロンプト・コメントはすべて日本語。

ユーザーへの返答は、作業の合間の短い報告も含めてすべて日本語で書くこと。

## コマンド

```bash
.venv/bin/pip install -r src/requirements.lock.txt   # 依存インストール（.venv は Python 3.13 で作成済み）
.venv/bin/streamlit run src/app.py              # 起動 → http://localhost:8501（runOnSave 有効）
.venv/bin/python scripts/smoke_test.py          # 全ツールの動作確認（API キー不要・Gemini はモック）
```

コマンドはすべてプロジェクト直下で実行する（`.streamlit/config.toml` は実行時のカレントディレクトリから読まれるため）。ユーザーは `tool/AIライティングツール.command` をダブルクリックして起動する（直下に `cd` して `src/app.py` を起動し、ブラウザを開く）。

API キーは `.env` の `GEMINI_API_KEY`（`.env.example` 参照）。未設定ならサイドバーで入力。

リンターはない。テストは `scripts/smoke_test.py`（`streamlit.testing.v1.AppTest` ベース）のみ。Gemini 呼び出しは **`core.ui.stream_text`** を差し替える（`core/ui.py` が名前で import しているため、`core.gemini` 側だけ patch しても効かない）。1ツールだけ確認する場合は `AppTest.from_string` でそのモジュールの `render()` を呼ぶスクリプトを渡す。

## アーキテクチャ

アプリ本体は `src/` にあり、`core` と `tools` は `src/` 直下のパッケージとして import される（`streamlit run src/app.py` で `src/` が `sys.path` に入る）。`.env`・`.python-version`・`.venv`・`.streamlit/`・`data/` はプロジェクト直下に置く（各ツールが直下を探すため）。README は `docs/README.md`。

- **`src/app.py`**：サイドバーで設定を `st.session_state` の `api_key` / `model` / `temperature` に書き込み、`st.navigation` に各ツールの `render` 関数を `st.Page` として登録する。
- **`src/core/gemini.py`**：`stream_text(contents, system)` は設定を引数ではなく `st.session_state` から読む。`contents` は文字列か `{"role": "user"|"model", "text": ...}` のリスト（複数ターン）。
- **`src/core/ui.py` の `render_output(key, tool, system, prompt)`**：全ツール共通の結果エリアで、次の流れを持つ。
  - `prompt` が渡された回だけ新規生成してストリーミング表示。それ以外の回は保存済みの結果を表示する。
  - ツールごとの状態は `st.session_state[f"tool_{key}"] = {"messages", "output"}`。`messages` は会話履歴そのもの。
  - 修正指示はフォーム送信で `st.session_state[f"refine_{key}"]` に入れて `st.rerun()`。次の実行で `messages` に追記して再生成する。システムプロンプトには `REFINE_SYSTEM_SUFFIX` が常に付く。
  - 生成ごとに `core/history.py` の `add_history` がプロジェクト直下の `data/history.json`（gitignore 済み・最新 300 件）に保存する。セッションでは `st.session_state["history"]` にキャッシュされ、読み書きは必ず `get_history` / `save_history` を通す。テストでは `core.history.HISTORY_FILE` を一時ファイルに差し替える。
- **`src/tools/*.py`**：各ツールは `SYSTEM`（システムプロンプト）と `render()` を持つ。`render()` はフォームを描画し、生成ボタンが押されたときだけ `prompt` を組み立てて `render_output` に渡す。ツールを追加するときは、このパターンのモジュールを作り `app.py` の `st.navigation` に登録する。

## 注意点

- **Python 3.13**（`.python-version`）。macOS 標準の `python3` は 3.9 なので使わない。仮想環境を作り直すときは `~/.local/bin/uv venv --seed .venv`（uv は PATH に入っていない）。既存コードの `Optional` や `from __future__ import annotations` は 3.9 時代の名残で、書き換える必要はない。
- Streamlit 1.66 以降の `AppTest.from_file` は、相対パスを呼び出し元ファイル基準で解決する。絶対パスを渡すこと。
- `genai.Client` は参照を保持しないと「client has been closed」で失敗する。アプリでは `st.cache_resource` の `get_client` を使う。
- `src/app.py` は直下の `.env` をパス指定の `load_dotenv(..., override=True)` で毎回読み直す（起動中にキーを書き換えても反映させるため）。`.env.example` の仮の値 `your-api-key-here` は未設定として扱う。
- モデルの提供状況は変わる。`gemini-2.5-*` は新規ユーザーには 404、Pro 系はこのキーでは 429（利用枠の上限）だった。`DEFAULT_MODELS` を変えるときは `client.models.list()` と実際の呼び出しで確認する。
- 標準入力から実行するスクリプトでは、`load_dotenv()` の自動探索が失敗するので `load_dotenv(".env")` とパスを渡す。
- プロジェクト直下の `.DS_Store` は削除しない。ユーザーが Finder で整えたアイコンの並び（名前順で横一列）が保存されている。VSCode では `.vscode/settings.json` で非表示にしてある。
