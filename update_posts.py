import glob
import os
import re
import time
from google import genai
from google.genai import errors

MODEL_NAME = "gemini-3.8-flash"


def generate_with_retry(client: genai.Client, prompt: str, max_retries: int = 4) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            return (response.text or "").strip()
        except errors.ServerError as exc:
            if attempt == max_retries:
                raise
            wait_sec = 5 * attempt
            print(f"サーバー混雑（{exc.code}）のため {wait_sec} 秒待機して再試行します（{attempt}/{max_retries}）...")
            time.sleep(wait_sec)
    return ""


def rewrite_post(client: genai.Client, filepath: str) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        original_content = f.read()

    date_match = re.search(r"^date:\s*(.+)$", original_content, flags=re.MULTILINE)
    existing_date = date_match.group(1).strip() if date_match else ""

    parts = original_content.split("---", 2)
    source_text = parts[2].strip() if len(parts) == 3 else original_content.strip()

    prompt = f"""
    以下は過去に作成したレビュー記事の下書き・本文です。
    扱っている商品やテーマの方向性は活かしつつ、読者が読みやすく魅力的な記事にリライトしてください。

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

    【元記事】
    {source_text}
    """

    raw_text = generate_with_retry(client, prompt)
    lines = raw_text.splitlines()

    article_title = lines[0].replace("#", "").replace('"', "”").strip() if lines else ""
    if not article_title:
        article_title = "話題のトレンド商品徹底レビュー"

    article_body = "\n".join(lines[1:]).strip()

    date_line = f"\ndate: {existing_date}" if existing_date else ""
    front_matter = f"""---
layout: post
title: "{article_title}"{date_line}
---

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(front_matter + article_body + "\n")

    print(f"更新完了: {filepath} -> {article_title}")


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)
    post_files = sorted(glob.glob("_posts/*.md"))

    if not post_files:
        print("_posts フォルダに対象のMarkdownファイルが見つかりませんでした。")
        return

    for idx, filepath in enumerate(post_files):
        if idx > 0:
            time.sleep(3)
        rewrite_post(client, filepath)


if __name__ == "__main__":
    main()
