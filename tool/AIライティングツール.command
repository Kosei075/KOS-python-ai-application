#!/bin/zsh
# ダブルクリックで AI ライティングツールを起動し、ブラウザで開く。
# このウィンドウを閉じる（または Ctrl + C）とツールが終了する。
cd "$(dirname "$0")/.."

URL="http://localhost:8501"

if curl -s "$URL/_stcore/health" > /dev/null 2>&1; then
    echo "すでに起動しています。ブラウザで開きます。"
    open "$URL"
    exit 0
fi

echo "AI ライティングツールを起動しています..."
echo "終了するときは、このウィンドウを閉じてください。"
echo "スマホから使うときは、ブラウザのサイドバー「📱 スマホで開く」の URL をスマホでブックマークしてください。"

# 起動が完了したらブラウザを開く
(
    for _ in {1..30}; do
        if curl -s "$URL/_stcore/health" > /dev/null 2>&1; then
            open "$URL"
            break
        fi
        sleep 1
    done
) &

.venv/bin/streamlit run src/app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false
