import datetime
import os
from google import genai

def main():
    # 1. Geminiクライアントの初期化（GitHub SecretsのGEMINI_API_KEYを使用）
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
    client = genai.Client(api_key=api_key)

    # 2. Geminiに生成させる記事のプロンプト（指示）
    prompt = """
    今話題の便利なトレンド商品やガジェットを1つ選び、そのレビュー記事をMarkdown形式で書いてください。
    以下の構成を必ず含めてください：
    - 魅力的で具体的な商品名
    - この商品の概要・特徴
    - メリット（長所）3選
    - デメリット（短所）2選
    - どんな人におすすめか・まとめ
    ※挨拶や前置きは書かず、記事本文のMarkdownから出力してください。
    """

    print("Geminiに記事の生成を依頼中...")
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    
    article_content = response.text

    # 3. _postsフォルダがなければ作成する
    os.makedirs("_posts", exist_ok=True)

    # 4. 上書きを防ぐため、ファイル名に「年月日・時分秒」を含める
    # 例: _posts/2026-11-19-15-30-00-review.md
    now = datetime.datetime.now()
    filename = f"_posts/{now.strftime('%Y-%m-%d-%H-%M-%S')}-review.md"

    # 5. Jekyll用のFront Matter（メタデータ）を確実に付与してファイルに保存
    # Jekyllは記事の先頭に --- で囲まれた layout や date がないと一覧に表示しないため付与します
    front_matter = f"""---
layout: post
title: "トレンド商品AIレビュー ({now.strftime('%Y/%m/%d %H:%M')})"
date: {now.strftime('%Y-%m-%d %H:%M:%S')}
---

"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + article_content)

    print(f"記事の生成と保存に成功しました: {filename}")

if __name__ == "__main__":
    main()
