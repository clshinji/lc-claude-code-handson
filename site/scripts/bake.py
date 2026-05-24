#!/usr/bin/env python3
"""
site/ 配下の SPA に最新の Markdown を焼き込む baker。

生成物:
  - site/index.html               (ハンズオン本編、 guides/handson-guide.md ベース)
  - site/cc-use-cases/index.html  (活用事例集、 cc-use-cases/*.md 統合)

site/index.html はテンプレートとして使い続け、 markdown だけを差し替える。
site/cc-use-cases/index.html は毎回 site/index.html から再生成 (title / GROUPS / md だけ差し替え)。
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
REPO = SITE.parent

MD_BLOCK = re.compile(
    r'(<script type="text/plain" id="md-source">)([\s\S]*?)(</script>)'
)
GROUPS_BLOCK = re.compile(
    r'(const GROUPS = \[)([\s\S]*?)(\];)'
)
HERO_TITLES_BLOCK = re.compile(
    r'(const HERO_TITLES = \{)([\s\S]*?)(\};)'
)
SUBTITLES_BLOCK = re.compile(
    r'(const SUBTITLES = \{)([\s\S]*?)(\};)'
)
SHORT_BLOCK = re.compile(
    r'(const SHORT = \{)([\s\S]*?)(\};)'
)
TITLE_BLOCK = re.compile(r"<title>[^<]*</title>")


def _inject_block(html: str, pattern: re.Pattern, body: str) -> str:
    if not pattern.search(html):
        raise SystemExit(f"ERROR: block not found for {pattern.pattern[:40]}")
    return pattern.sub(lambda m: f"{m.group(1)}{body}{m.group(3)}", html, count=1)


# --- Hands-on 本編 (site/index.html) ---


def bake_main_guide() -> None:
    src_md = (REPO / "guides" / "handson-guide.md").read_text(encoding="utf-8")
    # site/cc-use-cases/ にもこの SPA からリンクを張れるようにパス変換
    src_md = src_md.replace("../assets/", "assets/")
    # cc-use-cases/ への相対リンクは site/ ルート基準で `cc-use-cases/` に揃える
    src_md = src_md.replace("](../cc-use-cases/)", "](cc-use-cases/)")
    src_md = src_md.replace("[cc-use-cases/](../cc-use-cases/)", "[cc-use-cases/](cc-use-cases/)")

    # ローカル src/ にもコピー (運用上の参照用)
    (SITE / "src" / "handson-guide.md").write_text(src_md, encoding="utf-8")

    html_path = SITE / "index.html"
    html = html_path.read_text(encoding="utf-8")
    new_html = _inject_block(html, MD_BLOCK, f"\n{src_md}\n")
    html_path.write_text(new_html, encoding="utf-8")
    print(f"Baked main guide -> {html_path.relative_to(REPO)} ({len(src_md)} chars)")


# --- Use Cases SPA (site/cc-use-cases/index.html) ---


def _downshift(md: str) -> str:
    """`# 〜` を `## 〜` に、 `## 〜` を `### 〜` に、 ... 1 段下げる。"""
    out: list[str] = []
    in_code = False
    for line in md.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if not in_code:
            m = re.match(r"^(#{1,5}) ", line)
            if m:
                line = "#" + line  # add one more `#`
        out.append(line)
    return "\n".join(out) + ("\n" if md.endswith("\n") else "")


def _force_h2_title(md: str, new_title: str) -> str:
    """先頭の `## ...` を `## <new_title>` に置換。"""
    return re.sub(r"^## .+$", f"## {new_title}", md, count=1, flags=re.MULTILINE)


def bake_use_cases() -> None:
    template = (SITE / "index.html").read_text(encoding="utf-8")

    # title 差し替え
    template = TITLE_BLOCK.sub(
        "<title>Claude Code 活用事例集 — ハンズオン会</title>",
        template,
        count=1,
    )

    # GROUPS 差し替え
    groups_body = '''
    { label: "Overview", items: ["事例集について"] },
    { label: "Use Cases", items: [
      "事例 1: ホームページ作成",
      "事例 2: チラシ作り",
      "事例 3: 動画編集",
      "事例 4: SNS 投稿コンテンツの自動生成"
    ] },
    { label: "Bonus", items: ["フライヤー作成プロンプト集"] },
    { label: "Back", items: ["← ハンズオン本編に戻る"] }
  '''
    template = _inject_block(template, GROUPS_BLOCK, groups_body)

    # HERO_TITLES / SUBTITLES / SHORT 差し替え
    hero_titles = '''
    "事例集について": "事例集について",
    "事例 1: ホームページ作成": "ホームページ作成",
    "事例 2: チラシ作り": "チラシ作り",
    "事例 3: 動画編集": "動画編集",
    "事例 4: SNS 投稿コンテンツの自動生成": "SNS 投稿の自動生成",
    "フライヤー作成プロンプト集": "フライヤー作成プロンプト集",
    "← ハンズオン本編に戻る": "ハンズオン本編へ"
  '''
    template = _inject_block(template, HERO_TITLES_BLOCK, hero_titles)

    subtitles = '''
    "事例集について": "Claude Code & Cowork で「こんなこともできる」をまとめた事例集の入口です。",
    "事例 1: ホームページ作成": "自分だけの Web サイトを、Apple 公式風の対話プレビューで仕上げます。",
    "事例 2: チラシ作り": "イベント告知やメニュー表を、Cowork で一気に完成させる例。",
    "事例 3: 動画編集": "動画のカット・字幕付け・GIF 化を、 Claude Code に頼んでみよう。",
    "事例 4: SNS 投稿コンテンツの自動生成": "楽天 ROOM や Instagram の投稿ネタを、 1 週間分まとめて作る。",
    "フライヤー作成プロンプト集": "コピペで始められる、 フライヤー制作のステップ別プロンプト。",
    "← ハンズオン本編に戻る": "ハンズオン本編 (handson-guide) のページにジャンプします。"
  '''
    template = _inject_block(template, SUBTITLES_BLOCK, subtitles)

    short = '''
    "事例集について": "事例集について",
    "事例 1: ホームページ作成": "事例 1 ホームページ",
    "事例 2: チラシ作り": "事例 2 チラシ",
    "事例 3: 動画編集": "事例 3 動画編集",
    "事例 4: SNS 投稿コンテンツの自動生成": "事例 4 SNS 投稿",
    "フライヤー作成プロンプト集": "フライヤー プロンプト",
    "← ハンズオン本編に戻る": "← 本編に戻る"
  '''
    template = _inject_block(template, SHORT_BLOCK, short)

    # Markdown 統合: README + 01〜04 + flyer-prompts + back-link
    parts: list[str] = []

    def _load_and_shift(name: str, force_title: str) -> str:
        raw = (REPO / "cc-use-cases" / name).read_text(encoding="utf-8")
        shifted = _downshift(raw)
        return _force_h2_title(shifted, force_title)

    parts.append(_load_and_shift("README.md", "事例集について"))
    parts.append(_load_and_shift("01-homepage.md", "事例 1: ホームページ作成"))
    parts.append(_load_and_shift("02-flyer.md", "事例 2: チラシ作り"))
    parts.append(_load_and_shift("03-video-editing.md", "事例 3: 動画編集"))
    parts.append(_load_and_shift("04-sns-content.md", "事例 4: SNS 投稿コンテンツの自動生成"))
    parts.append(_load_and_shift("flyer-prompts.md", "フライヤー作成プロンプト集"))

    # 最後に本編へ戻るリンク章
    back_chapter = (
        "## ← ハンズオン本編に戻る\n"
        "\n"
        "事例集の閲覧、 お疲れさまでした。\n"
        "\n"
        "[👈 ハンズオン本編 (handson-guide) を開く](../)\n"
    )
    parts.append(back_chapter)

    combined = "\n\n".join(parts).rstrip() + "\n"
    # 画像パス: cc-use-cases/*.md は `../assets/foo.png` を使っている。
    # site/cc-use-cases/index.html から見て site/assets/ なので、 `../assets/` のままで OK。
    # README の事例リンク (01-homepage.md など) は、 同じ SPA 内なのでハッシュリンクで開けるよう削除/書き換えする
    combined = re.sub(
        r"\[(\d+\.\s*[^\]]+)\]\((\d+-[a-z]+\.md)\)",
        r"\1",  # link はテキストだけ残す
        combined,
    )

    # use-cases.md にも保存 (運用参考用)
    (SITE / "cc-use-cases" / "src").mkdir(parents=True, exist_ok=True)
    (SITE / "cc-use-cases" / "src" / "use-cases.md").write_text(combined, encoding="utf-8")

    template = _inject_block(template, MD_BLOCK, f"\n{combined}\n")

    out_path = SITE / "cc-use-cases" / "index.html"
    out_path.write_text(template, encoding="utf-8")
    print(f"Baked use cases -> {out_path.relative_to(REPO)} ({len(combined)} chars)")


def main() -> None:
    bake_main_guide()
    bake_use_cases()


if __name__ == "__main__":
    main()
