import datetime
import os
import random
from google import genai

MODEL_NAME = "gemini-3.8-flash"

# 収益化（成約）しやすく、ニッチ検索を狙いやすい4つのテーマプール
TARGET_GENRES = [
    {
        "name": "観葉植物・水耕栽培の環境づくり＆消耗品",
        "focus": "植物育成LEDライト（パネル型・クリップ型）、室内用液体肥料・活力剤、水耕栽培キット・スポンジ培地、小型静音サーキュレーター、害虫対策など、2,000円〜6,000円前後で買い足しやすい実用アイテム",
        "keywords": "植物育成ライト クリップ 電気代 / 水耕栽培 液体肥料 室内 / 観葉植物 サーキュレーター 静音",
    },
    {
        "name": "ゲームソフト＆コントローラー・収納周辺機器",
        "focus": "背面ボタン・連射機能付きサードパーティ製コントローラー、カセット収納付き持ち運びケース、大容量microSDカード、充電ドック周辺機器、複数人で遊べる定番・隠れ名作ソフトなど、2,000円〜7,000円前後で手が伸びやすいアイテム",
        "keywords": "Switch コントローラー 背面ボタン コスパ / ゲームソフト 2人プレイ おすすめ / Switch ケース カセット収納",
    },
    {
        "name": "スマホ快適化・充電＆MagSafe周辺ガジェット",
        "focus": "Qi2対応折りたたみマグネット充電スタンド、アンチグレア・覗き見防止ガラスフィルム、巻き取り式100W対応USB-Cケーブル、MagSafe対応カードケース・スマホリングなど、1,500円〜5,000円前後で日常の不満を解決するアイテム",
        "keywords": "Qi2 充電器 折りたたみ 旅行 / 巻き取り式 ケーブル 100W 持ち運び / スマホ フィルム アンチグレア 比較",
    },
    {
        "name": "AIスマートグラス・ウェアラブル活用＆接続アクセサリー",
        "focus": "スマートグラスや映像出力メガネをスマホ・ゲーム機と繋ぐ変換アダプター、専用遮光カバー・インサートレンズ周辺、または寝ながら動画・翻訳用途で注目される手頃なエントリー〜ミドルモデルなど、検索ライバルが少ないニッチ商材",
        "keywords": "スマートグラス Switch 接続 アダプター / スマートグラス 寝ながら 動画 / AIスマートグラス 口コミ 比較",
    },
]


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
    selected_genre = random.choice(TARGET_GENRES)

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
        - 1行目には、記事のタイトルのみを書いてください（具体的な商品名・型番と用途・実績が伝わるタイトルにする。記号や「タイトル：」などの前置き、# は付けない）。
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

    return f"""
    あなたは実用性とコスパを重視する商品レビュアーです。
    今回は以下の【指定ジャンル】の中から、読者が「2,000円〜6,000円前後で手を出しやすい（一部ニッチ機器はエントリー〜周辺パーツ中心）」かつ「売れ行きが良く口コミ数・評価でも支持されている具体的な商品（型番や具体的仕様が明確なもの）」を1つ選び、レビュー記事を書いてください。

    【指定ジャンル】
    - テーマ: {selected_genre["name"]}
    - 狙い目商材の条件: {selected_genre["focus"]}
    - 意識する検索キーワード例: {selected_genre["keywords"]}

    【出力ルール】
    - 1行目には、記事のタイトルのみを書いてください（具体的な商品名・型番と、読者の悩み・用途がひと目で伝わるタイトルにする。記号や「タイトル：」などの前置き、# は付けない）。
    - 2行目は空行にし、3行目以降にMarkdown形式で本文を書いてください。
    - 挨拶や前置きは一切書かないでください。

    【本文の構成と装飾ルール】
    文字ばかりにならないよう、以下の要素を必ず使って見やすく構成してください：
    1. 導入文（具体的な悩みや使用シーンに寄り添い、人気・口コミで選ばれている理由に触れつつ2〜3行で簡潔に）
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
        article_title = "人気・口コミで注目の厳選アイテム徹底レビュー"

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
