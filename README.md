# リベシティ オフ会 — Claude Code & Cowork ゆるっとハンズオン会

話題の **Claude Code & Cowork** を Claude デスクトップアプリで実際に触って体験する、 リベシティ オフ会の公開資料です。

## サイト

| 用途 | URL | 認証 |
|---|---|---|
| 事前案内 (LP) | https://clshinji.github.io/lc-claude-code-handson/ | なし |
| 当日資料 (本編) | https://lc-handson-site.pages.dev/ | あり (参加者に共有) |
| 活用事例集 | https://lc-handson-site.pages.dev/cc-use-cases/ | あり (参加者に共有) |

- **事前案内 LP** は GitHub Pages で公開しており、 誰でも閲覧できます (Schedule / 事前準備 / チェックリスト)
- **当日資料** は Cloudflare Pages で Basic Auth 保護しており、 当日に参加者へユーザー名/パスワードを共有します

## 構成

| パス | 内容 |
|------|------|
| [`index.html`](index.html) | LP (事前準備ガイド)。 GitHub Pages で公開 |
| [`guides/handson-guide.md`](guides/handson-guide.md) | 当日資料の原稿 (Markdown)。 Desktop アプリ主導の構成 |
| [`guides/BUILD.md`](guides/BUILD.md) | 配布用 HTML (`dist/handson-guide.html`) のビルド手順 |
| [`cc-use-cases/`](cc-use-cases/) | 活用事例集 (ホームページ / チラシ / 動画編集 / SNS) |
| [`site/`](site/) | Cloudflare Pages 配布版 (本編 SPA + 事例集 SPA + Basic Auth) |
| [`assets/`](assets/) | 共通画像アセット (インフォグラフィックス含む) |
| [`slides/`](slides/) | Marp スライド (講師用、 リポジトリでは非公開) |
| [`_admin/infographics-harness/`](_admin/infographics-harness/) | インフォグラフィックスを OpenAI gpt-image-2 で生成し、 Gemini で評価するハーネス (リポジトリでは非公開) |

## 当日資料の更新フロー

1. [`guides/handson-guide.md`](guides/handson-guide.md) / [`cc-use-cases/*.md`](cc-use-cases/) を編集
2. `./site/scripts/bake.py` を実行 → site/ 内の SPA に焼き込み
3. 必要なら `cp assets/<新規画像>.png site/assets/`
4. `cd site && npx wrangler pages deploy . --project-name lc-handson-site --branch main --commit-dirty=true --commit-message="..."`

詳しい運用は [`site/README.md`](site/README.md) を参照してください。 パスワード変更や Basic Auth 設定など。

## ライセンス

このリポジトリの内容は個人利用・学習目的で自由にご利用ください。
