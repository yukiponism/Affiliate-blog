import datetime
import os
from google import genai

MODEL_NAME = "gemini-3.8-flash"


def fetch_rakuten_product_data() -> dict | None:
    """
    将来の楽天デベロッパーズAPI連携用のプレースホルダー。
    API復旧・ID設定後に、実在する商品名・型番・価格・レビュー件数・評価・画像URL・購入URLを取得して返す。
    """
    app_id = os.environ.get("RAKUTEN_APP_ID")
    affiliate_id = os.environ.get("RAKUTEN_AFFILIATE_ID")
    if not app_id or not affiliate_id:
        return None
    return None


def build_prompt(product_data: dict | None) -> str:
    if product_data:
        return f"""
        以下の実在商品データをもとに、売れ行きや口コミ実績、同等レベルの競合商品との比較を重視したレビュー記事を書いてください。

        【商品情報】
        - 商品名・型番: {product_data.get("title", "")}
        - 参考価格: {product_data.get("price", "")}
        - レビュー件数・評価目安: {product_data.get("review_info", "")}
        - 商品画像URL: {product_data.get("image_url", "")}
        - 購入リンクURL: {product_data.get("affiliate_url", "")}

        【出力ルール】
        - 1行目には、記事のタイトルのみを書いてください（具体的な商品名・型番と魅力・実績が伝わるタイトルにする。記号や「タイトル：」などの前置き、# は付けない）。
        - 2行目は空行にし、3行目以降にMarkdown形式で本文を書いてください。
        - 挨拶や前置きは一切書かないでください。

        【本文の構成と装飾ルール】
        1. 導入文（具体的な悩み・利用シーンに寄り添い、売れ行きや口コミで注目されている背景を2〜3行で簡潔に）
        2. 商品画像の表示（提供された商品画像URLがある場合は `![商品名](画像URL)` の形式で冒頭付近に表示）
        3. ## 売れ行き・口コミで評価されている理由（レビュー件数の多さや高評価につながっているポイント、よく挙がる好意的な声・気になる声を整理）
        4. ## 同等レベルの競合商品との比較（Markdownの表で「今回のレビュー商品」「同等クラス競合A」「同等クラス競合B」を並べ、価格帯・口コミ/人気の傾向・強み・弱点を比較。表のあとに2〜3行で選び方の違いを解説）
        5. ## 実際に使ってわかるメリット3選（✅ を使い、具体的な使用シーンを交えて箇条書き＋太字）
        6. ## 購入前に知っておきたい注意点・向かない人（⚠️ を使い、デメリット2つと「こういう人には合わない」を明記）
        7. ## まとめ・チェックはこちら（引用「>」でおすすめ像をまとめ、購入リンクURLがある場合は案内を記載）
        """

    return """
    一般的な「おすすめ便利グッズ」ではなく、特定の悩みや用途を持つ人が検索しそうな「売れ行きが良く、口コミ数や評価でも支持されているニッチで具体的なトレンド商品・アイテム（型番や具体的仕様がイメージできるもの）」を1つ選び、同等レベルの競合商品と比較しながらレビュー記事を書いてください。
    ※デスク周り、室内・ベランダの植物ケア、旅行・移動、家事の時短、暮らしの道具など、生活の中で具体的に役立つ切り口を優先してください。

    【出力ルール】
    - 1行目には、記事のタイトルのみを書いてください（具体的な商品名と用途・実績が伝わるタイトルにする。記号や「タイトル：」などの前置き、# は付けない）。
    - 2行目は空行にし、3行目以降にMarkdown形式で本文を書いてください。
    - 挨拶や前置きは一切書かないでください。

    【本文の構成と装飾ルール】
    文字ばかりにならないよう、以下の要素を必ず使って見やすく構成してください：
    1. 導入文（具体的な悩みやシーンに寄り添い、人気・口コミで選ばれている理由に触れつつ2〜3行で簡潔に）
    2. ## 売れ行き・口コミで支持される理由（なぜ売れ行きが伸びているのか、口コミ数や高評価につながりやすい強みと、購入前に確認したい口コミ傾向を整理）
    3. ## 同等レベルの競合商品との比較（Markdownの「表」を使って、「今回の商品」「同等クラス競合A（同価格帯・定番人気モデル）」「同等クラス競合B（同等レベル・別強みモデル）」を比較し、価格目安・売れ行き/口コミの傾向・強み・弱点を整理。表の下に選び方の違いを簡潔に解説）
    4. ## ここが刺さる！メリット3選（✅ を使い、「どんな場面でどう助かるか」を具体的に箇条書き＋太字）
    5. ## デメリットと「向かない人」（⚠️ を使い、正直な弱点2つと「こういう人にはおすすめしない」を明確に書く）
    6. ## こんな人におすすめ！（引用「>」を使って、刺さる読者像をわかりやすくまとめる）
    """


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)
    product_data = fetch_rakuten_product_data()
    prompt = build_prompt(product_data)

    print("Geminiに記事の生成を依頼中...")
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    raw_text = (response.text or "").strip()
    lines = raw_text.splitlines()

    article_title = lines[0].replace("#", "").replace('"', "”").strip() if lines else ""
    if not article_title:
        article_title = "人気・口コミで注目のトレンドアイテム徹底レビュー"

    article_body = "\n".join(lines[1:]).strip()

    os.makedirs("_posts", exist_ok=True)
    now = datetime.datetime.now()
    filename = f"_posts/{now.strftime('%Y-%m-%d-%H-%M-%S')}-review.md"

    front_matter = f"""---
layout: post
title: "{article_title}"
date: {now.strftime('%Y-%m-%d %H:%M:%S')}
---

"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + article_body + "\n")

    print(f"記事の生成と保存に成功しました: {filename} (タイトル: {article_title})")


if __name__ == "__main__":
    main()
