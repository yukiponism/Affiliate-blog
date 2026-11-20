import datetime
import os
import random
from google import genai

MODEL_NAME = "gemini-3.8-flash"

# 検索需要が高く、2,000円〜1万円前後でレビュー記事が書きやすいキーワードプール
TARGET_GENRES = [
    {
        "category": "カメラ",
        "name": "カメラ周辺機器・撮影グッズ",
        "keywords": [
            "三脚 軽量 トラベル",
            "ミニ三脚 卓上",
            "NDフィルター 可変",
            "ブラックミスト フィルター",
            "CPLフィルター 偏光",
            "ストロボ クリップオン 小型",
            "LEDビデオライト 小型",
            "忍者レフ 反射防止",
            "レリーズ シャッターリモコン",
            "カメラバッグ ショルダー スリング",
            "カメラリュック おしゃれ 軽量",
            "インナーカメラバッグ",
            "カメラストラップ クイックリリース",
            "ジンバル スタビライザー",
            "ワイヤレスマイク ピンマイク",
            "防湿庫 ドライボックス",
            "レンズクリーニングキット ブロアー",
            "互換バッテリー 充電器",
            "SDカード 高速 UHS-II",
            "L型プレート クイックリリース",
        ],
    },
    {
        "category": "植物",
        "name": "観葉植物・水耕栽培の育成グッズ",
        "keywords": [
            "植物育成ライト LED パネル",
            "植物育成ライト クリップ",
            "水耕栽培 キット 室内",
            "水耕栽培 液体肥料 ハイポニカ",
            "観葉植物 液体肥料 活力剤",
            "観葉植物 培養土 虫がわかない",
            "スリット鉢 観葉植物",
            "自動給水 プランター",
            "サーキュレーター 小型 静音",
            "水やりチェッカー サスティー",
            "温湿度計 デジタル 観葉植物",
            "霧吹き 観葉植物 おしゃれ",
            "剪定バサミ 観葉植物",
            "ハイドロカルチャー 用土",
            "コバエ 対策 観葉植物 粘着",
            "植物棚 アイアン ラック",
            "鉢カバー おしゃれ 室内",
            "苔テラリウム キット",
            "発根促進剤 メネデール",
            "植物 受け皿 キャスター付き",
        ],
    },
    {
        "category": "ゲーム",
        "name": "ゲーム周辺機器・おすすめソフト",
        "keywords": [
            "Switch コントローラー 背面ボタン",
            "Switch プロコン 代替 おすすめ",
            "Joy-Con 充電スタンド",
            "Switch ケース 持ち運び",
            "Switch カセットケース 収納",
            "microSDカード 256GB 512GB Switch",
            "ゲーミングヘッドセット 軽量",
            "ゲーミングイヤホン 有線 マイク付き",
            "ゲーミングマウス ワイヤレス 軽量",
            "ゲーミングキーボード ラピッドトリガー",
            "モバイルモニター ゲーミング",
            "キャプチャーボード 配信 録画",
            "Switch 有線LANアダプター",
            "Switch 保護フィルム ガラス",
            "アナログスティック カバー エイムリング",
            "Switch ソフト 2人プレイ おすすめ",
            "Switch パーティゲーム おすすめ",
            "レバーレス コントローラー",
            "PS5 コントローラー 充電スタンド",
            "ゲーミング座椅子 クッション",
        ],
    },
    {
        "category": "スマホ",
        "name": "スマホ充電・MagSafe・快適ガジェット",
        "keywords": [
            "モバイルバッテリー 軽量 小型",
            "モバイルバッテリー MagSafe",
            "モバイルバッテリー コンセント一体型",
            "Qi2 充電器 折りたたみ",
            "急速充電器 Type-C 小型 65W",
            "巻き取り式 ケーブル Type-C",
            "MagSafe カードケース ウォレット",
            "MagSafe スマホリング",
            "スマホショルダー ストラップホルダー",
            "ガラスフィルム ガイド枠付き",
            "覗き見防止 フィルム iPhone",
            "アンチグレア フィルム ゲーム",
            "スマホスタンド 卓上 折りたたみ",
            "車載ホルダー スマホ MagSafe",
            "紛失防止タグ スマートトラッカー",
            "外付けSSD スマホ Type-C",
            "SDカードリーダー iPhone Type-C",
            "スマホ 冷却ファン ペルチェ",
            "骨伝導イヤホン オープンイヤー",
            "スマホ ジンバル 自撮り棒",
        ],
    },
    {
        "category": "スマートグラス",
        "name": "スマートグラス・ウェアラブル映像グラス周辺機器",
        "keywords": [
            "スマートグラス おすすめ 比較",
            "スマートグラス 寝ながら 映画",
            "スマートグラス Switch 接続 アダプター",
            "HDMI Type-C 変換アダプター 給電",
            "Type-C 映像出力 ケーブル L字",
            "スマートグラス 度付き インサートレンズ",
            "スマートグラス 遮光カバー ライトシールド",
            "スマートグラス 翻訳 リアルタイム",
            "スマートグラス オーディオ メガネ",
            "ワイヤレスHDMI トランスミッター",
        ],
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


def build_prompt(selected_genre: dict, selected_keyword: str, product_data: dict | None) -> str:
    if product_data:
        return f"""
        以下の実在商品データをもとに、売れ行きや口コミ実績、同等レベルの競合商品との比較を重視した「和英併記（日本語＋英語）」のレビュー記事を書いてください。

        【商品情報】
        - 商品名・型番: {product_data.get("title", "")}
        - 参考価格: {product_data.get("price", "")}
        - レビュー件数・評価目安: {product_data.get("review_info", "")}
        - 商品画像URL: {product_data.get("image_url", "")}
        - 購入リンクURL: {product_data.get("affiliate_url", "")}

        【出力ルール】
        - 1行目には、記事のタイトルのみを書いてください。「日本語タイトル | English Title」のように和英併記にしてください（記号や「タイトル：」などの前置き、#、ダブルクォーテーションは付けない）。
        - 2行目は空行にし、3行目以降にMarkdown形式で本文を書いてください。
        - 挨拶や前置きは一切書かないでください。
        - 本文の各セクション・表・箇条書き・引用は、まず自然な日本語を書き、そのすぐ下（または同じ項目内）に自然な英語を併記してください。

        【本文の構成と装飾ルール】
        1. 導入文（具体的な悩み・利用シーンに寄り添い、売れ行きや口コミで注目されている背景を簡潔に）
        2. 商品画像の表示（提供された商品画像URLがある場合は `![商品名](画像URL)` の形式で冒頭付近に表示）
        3. ## 売れ行き・口コミで評価されている理由 / Why It Sells & High Ratings（和英併記：評価ポイントと口コミ傾向を整理）
        4. ## 同等レベルの競合商品との比較 / Comparison with Similar Products（和英併記のMarkdown表で「今回のレビュー商品」「同等クラス競合A」「同等クラス競合B」を比較し、表のあとに選び方の違いを解説）
        5. ## 実際に使ってわかるメリット3選 / Top 3 Benefits in Daily Use（和英併記：`✅` を使い、具体的な使用シーンを交えて箇条書き＋太字）
        6. ## 購入前に知っておきたい注意点・向かない人 / Caveats & Who Should Skip It（和英併記：`⚠️` を使い、デメリット2つと「こういう人には合わない」を明記）
        7. ## まとめ・チェックはこちら / Summary & Where to Check（和英併記：引用「>」でおすすめ像をまとめ、購入リンクURLがある場合は案内を記載）
        """

    return f"""
    あなたは実用性とコスパを重視する商品レビュアーです。
    今回は以下の【ジャンル】と【ターゲット検索キーワード】から、読者が「2,000円〜10,000円前後で手を出しやすい（周辺機器・アクセサリー・実用アイテム中心）」かつ「売れ行きが良く口コミ数・評価でも支持されている具体的な商品（型番や具体的仕様・規格が明確なもの）」を1つ選び、「和英併記（日本語＋英語）」のレビュー記事を書いてください。

    【ジャンル】
    - カテゴリ: {selected_genre["name"]}
    - 今回のターゲット検索キーワード: {selected_keyword}

    【出力ルール】
    - 1行目には、記事のタイトルのみを書いてください。「日本語タイトル | English Title」のように和英併記にしてください（記号や「タイトル：」などの前置き、#、ダブルクォーテーションは付けない）。
    - 2行目は空行にし、3行目以降にMarkdown形式で本文を書いてください。
    - 挨拶や前置きは一切書かないでください。
    - 本文の各セクション・表・箇条書き・引用は、まず自然な日本語を書き、そのすぐ下（または同じ項目内）に自然な英語を併記して、海外の読者にも読みやすくしてください。

    【本文の構成と装飾ルール】
    文字ばかりにならないよう、以下の要素を必ず使って見やすく構成してください（すべて和英併記）：
    1. 導入文（具体的な悩みや使用シーンに寄り添い、人気・口コミで選ばれている理由に触れつつ簡潔に）
    2. ## 売れ行き・口コミで支持される理由 / Why It’s Popular & Well-Reviewed（売れ行きと口コミ傾向、評価されるポイントを整理）
    3. ## 同等レベルの競合商品との比較 / Comparison with Similar Products（Markdownの「表」を使って、「今回の商品」「同等クラス競合A」「同等クラス競合B」を比較し、表の下に選び方の違いを解説）
    4. ## ここが刺さる！メリット3選 / 3 Key Benefits in Real Use（`✅` を使い、「どんな場面でどう助かるか」を具体的に箇条書き＋太字）
    5. ## デメリットと「向かない人」 / Drawbacks & Who It’s Not For（`⚠️` を使い、正直な弱点2つと「こういう人にはおすすめしない」を明確に書く）
    6. ## こんな人におすすめ！ / Recommended For（引用「>」を使って、刺さる読者像をわかりやすくまとめる）
    """


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)
    selected_genre = random.choice(TARGET_GENRES)
    selected_keyword = random.choice(selected_genre["keywords"])
    product_data = fetch_rakuten_product_data()
    prompt = build_prompt(selected_genre, selected_keyword, product_data)

    print(
        f"Geminiに和英併記記事の生成を依頼中... "
        f"(カテゴリ: {selected_genre['category']}, キーワード: {selected_keyword})"
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    raw_text = (response.text or "").strip()
    lines = raw_text.splitlines()

    article_title = lines[0].replace("#", "").replace('"', "”").strip() if lines else ""
    if not article_title:
        article_title = "人気・口コミで注目の厳選アイテム徹底レビュー | Curated Product Review"

    article_body = "\n".join(lines[1:]).strip()

    os.makedirs("_posts", exist_ok=True)
    now = datetime.datetime.now()
    filename = f"_posts/{now.strftime('%Y-%m-%d-%H-%M-%S')}-review.md"
    category = selected_genre["category"]

    front_matter = f"""---
layout: post
title: "{article_title}"
date: {now.strftime('%Y-%m-%d %H:%M:%S')}
categories: [{category}]
---

"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + article_body + "\n")

    print(f"記事の生成と保存に成功しました: {filename} (カテゴリ: {category}, タイトル: {article_title})")


if __name__ == "__main__":
    main()
