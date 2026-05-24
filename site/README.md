# lc-handson-site — Cloudflare Pages 配布版 (Basic Auth)

リベシティ ハンズオン会の **当日資料** を Apple 公式風 SPA として Cloudflare Pages に Basic Auth 付きでデプロイするためのプロジェクトです。

ハンズオン本編 (`guides/handson-guide.md`) と活用事例集 (`cc-use-cases/*.md`) の 2 つの SPA を提供します。

## 公開 URL

| ページ | URL |
|---|---|
| 当日資料 (本編) | https://lc-handson-site.pages.dev/ |
| 活用事例集 | https://lc-handson-site.pages.dev/cc-use-cases/ |

ユーザー名 / パスワードはイベント参加者向けに別途共有してください (本リポジトリには記載しません)。

## 構成

| パス | 内容 |
|---|---|
| `index.html` | 本編 SPA。 サイドバー目次 + メインビュー、 Markdown は `<script id="md-source">` にインライン埋め込み |
| `src/handson-guide.md` | リポジトリの `guides/handson-guide.md` のコピー (baker が再生成) |
| `cc-use-cases/index.html` | 活用事例集 SPA。 4 事例 + 補足を 1 ページに統合 |
| `cc-use-cases/src/use-cases.md` | 4 事例 + フライヤープロンプトを統合した markdown (baker が再生成) |
| `assets/*.png` | 両 SPA で参照する画像 (リポジトリの `assets/` からコピー) |
| `scripts/bake.py` | `guides/handson-guide.md` と `cc-use-cases/*.md` を SPA に焼き込み |
| `scripts/bake.sh` | `bake.py` への薄いラッパ |
| `functions/_middleware.ts` | Pages Functions: 全リクエストに HTTP Basic Auth |
| `_headers` | セキュリティヘッダ + キャッシュ制御 |
| `wrangler.toml` | Cloudflare Pages プロジェクト設定 |

## 原稿の更新フロー

```bash
# 1. リポジトリの原稿を編集
#    guides/handson-guide.md       (本編)
#    cc-use-cases/*.md             (事例集)

# 2. baker で両 SPA を再生成
./site/scripts/bake.py
# (もしくは ./site/scripts/bake.sh でも可)

# 3. 新規画像があれば site/assets/ に手動コピー
cp assets/<新規画像>.png site/assets/

# 4. デプロイ
cd site
npx wrangler pages deploy . \
  --project-name lc-handson-site \
  --branch main \
  --commit-dirty=true \
  --commit-message="..."
```

> 💡 `bake.py` は次のことを自動でやります:
> - `guides/handson-guide.md` 内の `../assets/` → `assets/` 置換 (画像パス調整)
> - `../cc-use-cases/` → `cc-use-cases/` 置換 (本編→事例集リンク調整)
> - `cc-use-cases/*.md` の見出しを 1 段下げて、 `parseChapters` (`## ` 区切り) に対応
> - 各事例タイトルを「事例 N: 〜」 形式に正規化
> - 「← ハンズオン本編に戻る」 章を末尾に追加

## ローカル動作確認

`.dev.vars` を作成 (Git 管理外):

```ini
BASIC_AUTH_USER="handson"
BASIC_AUTH_PASS="libe2026"
```

```bash
npx wrangler pages dev . --port 8788
```

ブラウザで http://localhost:8788 を開き、 Basic Auth ダイアログでユーザー名 `handson` / パスワード `libe2026` を入力。

## 本番デプロイ

### 初回のみ

```bash
# プロジェクトを作成 (production ブランチは main)
npx wrangler pages project create lc-handson-site --production-branch main

# Secret 投入 (production と preview 両方)
printf 'handson'  | npx wrangler pages secret put BASIC_AUTH_USER --project-name lc-handson-site
printf 'libe2026' | npx wrangler pages secret put BASIC_AUTH_PASS --project-name lc-handson-site
```

### 毎回

```bash
npx wrangler pages deploy . \
  --project-name lc-handson-site \
  --branch main \
  --commit-dirty=true
```

完了すると `https://<deployment-id>.lc-handson-site.pages.dev` のような URL が発行されます。 本番 URL は `https://lc-handson-site.pages.dev`。

## 認証情報の変更

### パスワード変更の標準手順

1. **本番 (production) のパスワードを更新**

   ```bash
   printf '新しいパスワード' | npx wrangler pages secret put BASIC_AUTH_PASS --project-name lc-handson-site
   ```

   > ⚠️ `printf` を使うのは **末尾改行を入れないため** 。 `echo` だと改行 `\n` がパスワードに含まれてしまい、 認証が通らなくなります。

2. **プレビュー (preview) も同時に更新したい場合**

   ```bash
   printf '新しいパスワード' | npx wrangler pages secret put BASIC_AUTH_PASS --project-name lc-handson-site --env preview
   ```

3. **再デプロイで反映を確実にする** (Secret は次回デプロイから有効になります)

   ```bash
   cd /Users/kentaro/Documents/code/daily/lc-offline-meeting/site
   npx wrangler pages deploy . \
     --project-name lc-handson-site \
     --branch main \
     --commit-dirty=true \
     --commit-message="Rotate BASIC_AUTH_PASS"
   ```

4. **動作確認**

   ```bash
   # 旧パスワードで 401 になるか
   curl -sS -o /dev/null -w "%{http_code}\n" -u handson:旧パスワード https://lc-handson-site.pages.dev/
   # 新パスワードで 200 になるか
   curl -sS -o /dev/null -w "%{http_code}\n" -u handson:新パスワード https://lc-handson-site.pages.dev/
   ```

### ユーザー名を変える場合

```bash
printf '新しいユーザー名' | npx wrangler pages secret put BASIC_AUTH_USER --project-name lc-handson-site
# preview も同様に
printf '新しいユーザー名' | npx wrangler pages secret put BASIC_AUTH_USER --project-name lc-handson-site --env preview
# 再デプロイで反映
```

### ローカルの `.dev.vars` も更新する

`site/.dev.vars` はローカル開発専用 (`wrangler pages dev`) の設定ファイルです。 本番の Secret を変えたら、 ローカル動作確認のために `.dev.vars` も同じ値に更新してください。

```ini
BASIC_AUTH_USER="新しいユーザー名"
BASIC_AUTH_PASS="新しいパスワード"
```

(`.dev.vars` は `.gitignore` で除外されているので、 Git に commit されることはありません)

### 現在の Secret 一覧を確認したい

```bash
npx wrangler pages secret list --project-name lc-handson-site
# preview は --env preview を付けて確認
npx wrangler pages secret list --project-name lc-handson-site --env preview
```

### 緊急で認証を無効化したいとき (非推奨)

`site/functions/_middleware.ts` の `onRequest` を `return next();` のみに書き換えてデプロイすれば認証をバイパスできます。 イベント終了後など、 一時的に資料を公開したいときに使います。 用が済んだら元に戻すのを忘れずに。

### よくある失敗

| 症状 | 原因 | 対処 |
|---|---|---|
| 新パスワードでも 401 | デプロイ直後で Secret がまだ反映されていない | 30 秒〜1 分待って再試行 |
| 旧パスワードでも 200 | ブラウザがキャッシュ済みの認証情報を送っている | プライベートブラウズで確認、 または `curl -u` で確認 |
| すべて 500 | `BASIC_AUTH_PASS` が空 / 未設定 | `wrangler pages secret list` で存在確認 → 再投入 |
| 設定したのに反映されない | production と preview を取り違えた | `--env preview` の付け忘れがないか確認 |
| `wrangler` コマンドが認証エラー | OAuth トークンの期限切れなど | `npx wrangler login` で再ログイン |

## トラブルシューティング

- **401 が返り続ける**: Secret が未投入の可能性。 `wrangler pages secret list --project-name lc-handson-site` で確認
- **画像が 404**: `site/assets/` への画像コピー漏れ。 `bake.py` は Markdown と HTML しか同期しない (画像は手動コピー)
- **`cc-use-cases/` 経由のリンクが切れる**: handson-guide.md で `[...](../cc-use-cases/)` のようなパスを使った場合、 baker が `cc-use-cases/` (site/ ルート相対) に書き換えるかを確認
- **本番に古いコンテンツが残る**: `--branch main` でデプロイしたあと、 Cloudflare の edge cache (`_headers` の `max-age=300`) が効いている可能性。 30 秒〜数分待って再アクセス
- **`Invalid commit message, it must be a valid UTF-8 string`**: ローカルの直近 git コミットメッセージに wrangler が読めない絵文字が含まれていると出る。 `--commit-message="..."` を明示すれば回避できる
- **wrangler コマンドが認証エラー**: `npx wrangler login` でブラウザ認証を通す
