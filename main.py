import os
import time
import datetime
from google import genai

# 1. APIキーの読み込み
api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# 2. プロンプト設定
prompt = """
あなたはプロのガジェット・生活便利グッズのレビュアーです。
現在（2026年）日本のECサイト（楽天市場やAmazon）でトレンドになっている、または口コミ評価が高い具体的な人気商品・ジャンルを1つ選び、購入を検討している読者向けのレビュー記事をMarkdown形式で書いてください。

【必須の構成】
1. 記事タイトル（読者が検索したくなる魅力的なタイトル）
2. 商品の概要と、どんな人におすすめか
3. 実際の口コミ・評判からわかる3つのメリット
4. 購入前に知っておくべき2つのデメリット・注意点
5. まとめ（どんな買い方をすべきか）

※出力は本文のMarkdownのみにしてください（最初の公式な挨拶などは不要です）。
※一番最初の行に `# 記事タイトル` を入れてください。
"""

# 3. サーバー混雑（503エラー）対策の自動リトライ付きで生成
article_text = ""
for attempt in range(1, 6):
    try:
        print(f"記事生成を試行中... ({attempt}回目)")
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        article_text = response.text.strip()
        break
    except Exception as e:
        print(f"エラー発生: {e}")
        if attempt < 5:
            print("サーバー混雑のため10秒待機して再試行します...")
            time.sleep(10)
        else:
            raise e

# タイトルの抽出（1行目の # を取り除く）
lines = article_text.split("\n")
title = lines[0].replace("#", "").strip()
body = "\n".join(lines[1:]).strip()

# 4. GitHub Pages（Jekyll）用の記事ファイルとして保存
today = datetime.date.today().strftime("%Y-%m-%d")
os.makedirs("_posts", exist_ok=True)
filename = f"_posts/{today}-review.md"

front_matter = f"""---
layout: post
title: "{title}"
date: {today}
---

"""

with open(filename, "w", encoding="utf-8") as f:
    f.write(front_matter + body)

print(f"記事を生成しました: {filename}")
