# ✍️ AI ライティングツール

Streamlit + Gemini API で作る、個人用の AI ライティングツールです。

## 機能

| カテゴリ | ツール | 内容 |
|---|---|---|
| 作成 | 📝 ブログ記事作成 | テーマから構成案・本文を作成（文字数・トーン・キーワード指定） |
| | ✉️ メール作成・返信 | 受信メールへの返信／新規メール。関係性・トーン・複数パターン |
| | 📣 SNS投稿作成 | X / Instagram / LinkedIn など媒体別の投稿文を複数案 |
| | 💡 タイトル・キャッチコピー | ブログ・YouTube・商品などのタイトル案とおすすめ |
| 編集・整理 | 📚 要約 | 箇条書き・3行・レポート形式など。ToDo / キーワード抽出 |
| | 🔍 校正・リライト | 誤字脱字チェック（修正箇所一覧付き）、リライト、トーン変換、文字数調整 |
| | 🌐 翻訳 | 自然な翻訳＋訳のポイント解説 |
| | 🗒️ メモ整形・議事録 | 走り書きメモ → 議事録・日報・ToDo・手順書 |
| その他 | 🧩 フリープロンプト | 役割と指示を自由に設定 |
| | 🕘 生成履歴 | 生成結果を `data/history.json` に自動保存（最新300件）。検索・個別削除・JSON エクスポート |

全ツール共通：ストリーミング表示 / **修正指示による追加ブラッシュアップ** / コピー / Markdown ダウンロード / モデル・temperature 切り替え

## セットアップ

コマンドはすべてプロジェクトのフォルダ直下で実行します。Python 3.13 を使います（`.python-version` で指定）。macOS 標準の `python3` は 3.9 なので、[uv](https://docs.astral.sh/uv/) で環境を作ります。

```bash
~/.local/bin/uv venv --seed .venv     # .python-version を見て Python 3.13 の仮想環境を作成
source .venv/bin/activate
pip install -r src/requirements.lock.txt   # 動作確認済みのバージョンで入れる

cp .env.example .env   # GEMINI_API_KEY を記入
streamlit run src/app.py
```

### ダブルクリックで起動

Finder で `tool/AIライティングツール.command` をダブルクリックすると、起動してブラウザが開きます（すでに起動中ならブラウザを開くだけ）。開いたターミナルのウィンドウを閉じると終了します。

### スマホなど他の端末から使う

同じ Wi-Fi のスマホなどからも開けます。この Mac から開くときは何もいりません。

1. この Mac でツールを開き、サイドバーの「📱 スマホで開く」を開く
2. 表示された URL（合言葉入り）をスマホで開いてブックマークする
3. 次からはブックマークを開くだけで使える

合言葉は `.env` の `APP_PASSWORD`（8 文字以上）です。URL を知らない他人は入れません。合言葉を変えると、古いブックマークでは入れなくなります。通信は暗号化されないので、自宅など信頼できる Wi-Fi でだけ使ってください。

API キーは [Google AI Studio](https://aistudio.google.com/apikey) で取得できます。
`.env` を使わない場合は、起動後にサイドバーから入力することもできます。

## 構成

```
src/                    # アプリ本体
  app.py                #   エントリーポイント（ナビゲーション・サイドバー設定）
  requirements.txt      #   依存パッケージ（下限のみ）
  requirements.lock.txt #   動作確認済みのバージョンを固定したもの
  core/gemini.py        #   Gemini API クライアント・ストリーミング
  core/ui.py            #   共通 UI（結果表示・修正指示）
  core/history.py       #   履歴のファイル保存
  tools/*.py            #   各ライティングツール（render() を持つ）
tool/
  AIライティングツール.command  # ダブルクリックで起動
scripts/
  smoke_test.py         # 動作確認（API キー不要）
docs/README.md          # このファイル
.claude/CLAUDE.md       # Claude Code 向けの説明
data/history.json       # 生成履歴（自動作成）
```

`.env` や `.venv` などの隠しファイルは、各ツールがプロジェクト直下を探すため直下に置いています。

## 動作確認

```bash
.venv/bin/python scripts/smoke_test.py
```

Gemini をモックして、全ツールの描画・生成・修正指示・履歴保存をチェックします。

新しいツールを追加するには、`src/tools/` に `render()` 関数を持つモジュールを作り、`src/app.py` の `st.navigation` に登録します。
