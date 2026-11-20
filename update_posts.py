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

    # 元のFront Matterから日付（date）とカテゴリ（categories）があれば引き継ぐ
    date_match = re.search(r"^date:\s*(.+)$", original_content, flags=re.MULTILINE)
    existing_date = date_match.group(1).strip() if date_match else ""

    cat_match = re.search(r"^categories:\s*(.+)$", original_content, flags=re.MULTILINE)
    existing_categories = cat_match.group(1).strip() if cat_match else ""

    # --- 以降（Front Matterの終わり）を元記事として抽出
    parts = original_content.split("---", 2)
    source_text = parts[2].strip() if len(parts) == 3 else original_content.strip()

    prompt = f"""
    以下は過去に作成したレビュー記事の下書き・本文です。
    扱っている商品やテーマの方向性は活かしつつ、海外の読者にも読みやすい「和英併記（日本語＋英語）」のレビュー記事にリライトしてください。

    【出力ルール】
    - 1行目には、記事のタイトルのみを書いてください。「日本語タイトル | English Title」のように和英併記にしてください（記号や「タイトル：」などの前置き、#、ダブルクォーテーションは付けない）。
    - 2行目は空行にし、3行目以降にMarkdown形式で本文を書いてください。
    - 挨拶や前置きは一切書かないでください。
    - 本文の各セクション・表・箇条書き・引用は、まず自然な日本語を書き、そのすぐ下（または同じ項目内）に自然な英語を併記してください。

    【本文の構成と装飾ルール】
    文字ばかりにならないよう、以下の要素を必ず使って見やすく構成してください（すべて和英併記）：
    1. 導入文（具体的な悩みやシーンに寄り添い、人気・口コミで選ばれている理由に触れつつ簡潔に）
    2. ## 売れ行き・口コミで支持される理由 / Why It’s Popular & Well-Reviewed（売れ行きと口コミ傾向、評価されるポイントを整理）
    3. ## 同等レベルの競合商品との比較 / Comparison with Similar Products（Markdownの「表」を使って、「今回の商品」「同等クラス競合A」「同等クラス競合B」を比較し、表の下に選び方の違いを解説）
    4. ## ここが刺さる！メリット3選 / 3 Key Benefits in Real Use（`✅` を使い、「どんな場面でどう助かるか」を具体的に箇条書き＋太字）
    5. ## デメリットと「向かない人」 / Drawbacks & Who It’s Not For（`⚠️` を使い、正直な弱点2つと「こういう人にはおすすめしない」を明確に書く）
    6. ## こんな人におすすめ！ / Recommended For（引用「>」を使って、刺さる読者像をわかりやすくまとめる）

    【元記事】
    {source_text}
    """

    raw_text = generate_with_retry(client, prompt)
    lines = raw_text.splitlines()

    article_title = lines[0].replace("#", "").replace('"', "”").strip() if lines else ""
    if not article_title:
        article_title = "人気・口コミで注目の厳選アイテム徹底レビュー | Curated Product Review"

    article_body = "\n".join(lines[1:]).strip()

    date_line = f"\ndate: {existing_date}" if existing_date else ""
    cat_line = f"\ncategories: {existing_categories}" if existing_categories else ""
    front_matter = f"""---
layout: post
title: "{article_title}"{date_line}{cat_line}
---

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(front_matter + article_body + "\n")

    print(f"和英併記更新完了: {filepath} -> {article_title}")


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
