import streamlit as st

from core.ui import page_header, render_output, text_or_file_input

SYSTEM = """あなたは優秀な秘書です。
走り書きのメモや文字起こしから、要点が一目でわかる整った文書を作成します。
メモに書かれていない事実は推測で追加しないでください。"""

FORMATS = {
    "議事録": "会議名・日時・参加者（わかる範囲で）、議題、決定事項、議論の要点、ToDo（担当・期限）の構成の議事録",
    "日報": "本日の業務内容、成果、課題・気づき、明日の予定の構成の日報",
    "ToDoリスト": "優先度（高・中・低）付きのチェックボックス形式のToDoリスト",
    "アイデア整理": "テーマごとにグルーピングし、各アイデアの要点と次のアクションを整理した文書",
    "手順書": "番号付きのステップと注意点で構成された手順書",
}


def render() -> None:
    page_header("🗒️ メモ整形・議事録", "走り書きのメモや文字起こしを、議事録・日報などの文書に整えます。")

    memo = text_or_file_input("メモ・文字起こし *", "minutes",
                              placeholder="例: 定例MTG 田中 佐藤 / 新機能リリース 12月→1月に延期 理由テスト不足 ...")
    fmt = st.selectbox("出力形式", list(FORMATS))

    prompt = None
    if st.button("✨ 整形する", type="primary"):
        if not memo.strip():
            st.warning("メモを入力してください。")
        else:
            prompt = f"""以下のメモを、{FORMATS[fmt]}にMarkdownで整形してください。
不明な項目は「（記載なし）」としてください。

---
{memo}"""

    render_output("minutes", "メモ整形・議事録", SYSTEM, prompt, filename=f"{fmt}.md")
