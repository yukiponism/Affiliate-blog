import datetime
import os
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
    client = genai.Client(api_key=api_key)

    # 1行目にタイトル、2行目以降に読みやすく装飾した本文を出させるプロンプト
    prompt = """
    今話題の便利なトレンド商品やガジェットを1つ選び、読者が読みたくなるレビュー記事を書いてください。

    【出力ルール】
    - 1行目には、記事のタイトルのみを書いてください（具体的な商品名と魅力が伝わるキャッチーなタイトルにする。記号や「タイトル：」などの前置き、# は付けない）。
    - 2行目は空行にし、3行目以降にMarkdown形式で本文を書いてください。
    - 挨拶や前置きは一切書かないでください。

    【本文の構成と装飾ルール】
    文字ばかりにならないよう、以下の要素を必ず使って見やすく構成してください：
    1. 導入文（読者の悩みに寄り添う親しみやすい語り口で2〜3行）
    2. ## 商品の基本スペック・特徴（Markdownの「表（テーブル）」を使って、価格目安・おすすめ度・特徴などを整理する）
    3. ## ここが最高！メリット3選（✅ を使い、箇条書き＋太字で分かりやすく）
    4. ## 購入前に知っておきたい注意点（⚠️ を使い、デメリットを正直に2つ）
    5. ## こんな人におすすめ！（引用「>」を使って、どんなシーンで役立つかイメージしやすくまとめる）
    """

    print("Geminiに記事の生成を依頼中...")
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    
    raw_text = response.text.strip()
    lines = raw_text.splitlines()

    # 1行目をタイトルとして取得（ダブルクォーテーションが含まれるとYAMLが崩れるため置換）
    article_title = lines[0].replace("#", "").replace('"', "”").strip()
    if not article_title:
        article_title = "話題のトレンド商品徹底レビュー"

    # 2行目以降を本文として結合
    article_body = "\n".join(lines[1:]).strip()

    # _postsフォルダ作成
    os.makedirs("_posts", exist_ok=True)

    # 上書き防止のため、ファイル名に「年月日・時分秒」を含める
    now = datetime.datetime.now()
    filename = f"_posts/{now.strftime('%Y-%m-%d-%H-%M-%S')}-review.md"

    # Jekyll用のFront Matter（抽出した商品名入りタイトルをセット）
    front_matter = f"""---
layout: post
title: "{article_title}"
date: {now.strftime('%Y-%m-%d %H:%M:%S')}
---

"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + article_body)

    print(f"記事の生成と保存に成功しました: {filename} (タイトル: {article_title})")

if __name__ == "__main__":
    main()
