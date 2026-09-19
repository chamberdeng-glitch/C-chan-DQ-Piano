# REVIEW_NOTES — 曲別ページ リッチデザイン移行

対象: Codex（レビュー担当AI）／プロジェクトオーナー
状態: **試作1曲（DQ1「広野を行く」/ `/dq1/unknown-world/`）のみ完了。量産・デプロイ未着手。**
目的: この1ページで「データ↔テンプレート分離」「条件付き表示」「JSON-LD自動生成」
　　　「slug参照解決」の型を固める。承認後に全曲へ展開する。

---

## 1. 設計の全体像（どこを触れば何が変わるか）

```
データ層（曲ごとの中身）            テンプレート層（見た目・構造）
─────────────────────            ─────────────────────
song-reference-data.js   ┐
  曲ID/曲名/カテゴリ/難易度/動画 │
song-page-content.js     ┼──→  build-seo-pages.py
  slug/公開日/紹介文/楽譜/別テイク │      write_song_page_rich()  ← リッチ版テンプレ
song-title-translations.js┘      （データを流し込むだけ。HTML直書き禁止）
                                        │
                                        ├─→ assets/song-page.css     ← 見た目
                                        └─→ assets/lite-yt-embed.*   ← 遅延埋め込み
```

- **デザインを変える** → `assets/song-page.css` と `write_song_page_rich()` の1か所だけ直せば全曲に反映。
- **曲の中身を足す**（紹介文・楽譜・別テイク等）→ `song-page-content.js` の該当曲に項目を追加するだけ。
- **どの曲をリッチ版にするか** → `build-seo-pages.py` の `SONG_RICH_IDS`（現在 `{'I-4'}`）。
  量産時はここを全曲IDに広げる（下記 7 参照）。

---

## 2. 既存データ形式 → 新データ構造への変換方針と理由

新デザイン案のスキーマ（`title_ja/title_en/series/category/difficulty/composer/release/
youtube_main/takes/medleys/scorebook/related`）を、**既存データを壊さず**に次のように対応付けた。

| 新スキーマ項目 | データの出どころ | 方針と理由 |
|---|---|---|
| slug / title_ja / title_en / series / category / youtube_main | 既存（reference + translations） | そのまま使用。URL不変の制約を守るため slug は既存値を厳守 |
| difficulty（数字→★） | 既存 `difficultyStars`（0–5） | `stars_html()` が数字から★★★☆☆を自動描画。0は「未設定」 |
| composer | **新規**：コード定数 `SONG_COMPOSER='すぎやまこういち'` | DQ1〜11 全曲すぎやまこういち作曲のため一律。曲データに項目を持たせず定数化（冗長回避） |
| release（収録作品の年） | **新規**：`SERIES_RELEASE`（I=1986…XI=2017） | 年は作品単位で確定。曲ごとに持たせず シリーズキーから導出（データ重複回避） |
| scorebook（楽譜 Amazon/楽天） | **新規**：`song-page-content.js` の曲別 `scorebook` | 各曲のYouTube概要欄に `[PR]アマゾン`/`[PR]楽天` のアフィリリンクがあり抽出可能（下記7で一括取得予定）。試作はI-4分を手動投入 |
| related（関連楽曲） | 既存から自動 | 同カテゴリ＋同シリーズ優先で自動抽出。slugだけ持てば表示名・サムネは参照先から解決 |
| 前後の曲 | 既存から自動 | series＋sortNumber順で前後を自動計算 |
| takes / medleys | **新規**：`song-page-content.js`（空でスタート） | 紐付けデータが現存しない。空ならセクションごと非表示（下記3）。データ投入の仕組みだけ先に実装 |

判断理由の要点: **「作品単位で決まる値（composer/release）はコード側、曲単位で変わる値は
データ側」** に置いた。これでデータファイルの肥大を避けつつ、量産時の入力負荷を最小化している。

---

## 3. 条件付き表示・JSON-LD自動生成・slug参照の実装箇所

すべて `build-seo-pages.py` 内（`write_song_page_rich()` とその補助関数）。

- **条件付き表示**：`takes` / `medleys` / `scorebook` / `related` が空の曲は、その
  `if ...:` ブロックに入らず**セクションごと出力されない**（空の箱を残さない）。
  - 試作ページでこの両方が確認できる：`scorebook`＝**表示**、`takes`/`medleys`＝**非表示**。
- **難易度の自動描画**：`stars_html(stars)`。0/未設定は `<span ...>未設定</span>`。
- **slug参照の自動解決**：`sr_video_card(row)` が、対象曲に曲ページが有れば内部リンク、
  無ければYouTube直リンクを自動選択。表示名・サムネ・カテゴリは参照先の曲データから取得。
- **JSON-LD自動生成**：`write_song_page_rich()` 内で必ず
  `VideoObject`（name/description/thumbnailUrl/embedUrl/uploadDate）＋`BreadcrumbList`＋
  `WebSite` を曲データから生成。手書き箇所はゼロ。
- **画像の遅延読み込み**：カード・楽譜カバー・プロフィール画像は `loading="lazy"` 既定。
  ファーストビューの動画はlite-youtubeがサムネのみ先読みする軽量方式。
- **メタデータ自動生成**：title / description / canonical（自己参照）/ og:image（hqdefault）/
  hreflang（ja・en相互＋x-default）を `make_head()` 経由で自動生成。

---

## 4. 判断に迷った点・確認してほしいこと（要返答）

1. **演奏者プロフィールの本文**：デザイン案の「京都女子大学…大学院…」という経歴文は
   `site-content.js` に存在せず、実在の経歴か不明。**架空の経歴を載せるのは避ける**ため、
   試作では既存の正式文（「元クラシックピアニストとしての技術を活かし…」）を使用した。
   → 実在の経歴・肩書きがあれば教えてほしい（あれば差し替える）。
2. **ヘッダー/フッターのスコープ**：デザイン案のヘッダー（DQ PIANO LIBRARY＋新ナビ）は
   全ページ共通要素のため、曲ページだけ変えると不統一になる。今回は**既存ヘッダー/フッターを
   流用**し、曲ページ本体だけ新デザインにした。→ サイト全体のヘッダー刷新は別スコープにすべきか確認。
3. **難易度の値**：デザイン案は★★★だが、実データ（`difficultyStars`）では「広野を行く」は
   ★★（初中級）。→ **実データを優先**した。デザイン案の★★★は仮表示と解釈。
4. **メドレー欄**：紐付けデータが無く自動化もできないため、オーナー承認のうえ
   **空＝非表示**で進行（仕組みは実装済み、データは後日投入）。
5. **release は作品単位**（曲ごとの初出年ではなく収録作品の発売年）で表示している。これでよいか。

---

## 5. ⚠️ 既知の不具合・未解決

- **プレビューで CSS 未適用・レイアウト崩れ**：`song-page.css` は 200/`text/css` で配信され、
  `<link>` も DOM にあるのに、ブラウザの `styleSheets` に載らず未適用（タグが箇条書き・2カラム
  にならない等）。**Pythonビルドレベルの検証は全項目パス**（HTML構造/JSON-LD/canonical/hreflang/
  内部リンク/条件付き表示）。CSS自体の構文も波括弧対応OK。
  - 調査中に**ツール出力へ偽テキストが混入する環境不具合**が頻発し、ブラウザ側のデバッグ
    （console/network/eval）の結果が信頼できず、原因の確定に至っていない。
  - **次にやること**：クリーンな環境（別のローカルサーバ、または本番ステージング）で
    `/dq1/unknown-world/` を開き、(a) `song-page.css` が `document.styleSheets` に載るか、
    (b) `.sr-lead-grid` が2カラムになるか、(c) lite-youtube が再生するか を確認。
    CSS/HTML自体のバグか、プレビュー環境固有かを切り分ける。

---

## 6. TODO（量産フェーズで対応）

- [ ] 上記5のCSS適用問題の切り分け・解消（**最優先。これが解けないと量産しても見た目が出ない**）
- [ ] **英語版 rich テンプレート**（試作は日本語のみ。`write_song_page_rich` を lang対応に拡張）
- [ ] 英語版 og:image（将来 `thumbnail_en` を使う設計余地。現状は日英とも hqdefault 共通）
- [ ] **全曲の scorebook 一括取得**：各曲YouTube概要欄から `[PR]アマゾン`/`[PR]楽天` を抽出し
      `song-page-content.js` に流し込むスクリプト（公開日取得 `scripts/fetch-upload-dates.py` と同方式）
- [ ] takes / medleys のデータ投入（仕組みは実装済み、中身が空）
- [ ] **量産**：`SONG_RICH_IDS` を全212曲へ拡張（下記7）
- [ ] シリーズ/カテゴリページのリンク・sitemap.xml を新ページに整合（量産時）
- [ ] **検証スクリプト**：title/description/canonical/og:image/JSON-LD/hreflang と
      内部リンク切れ・trailing slash・canonical自己参照を全曲チェックする
      `scripts/validate-song-pages.py` を追加し、ビルド時に実行できるようにする（制約事項）
- [ ] 出力レポート（量産時に生成）：難易度「未設定」の曲一覧CSV／takes・medleys・scorebookが
      空でセクション省略された曲一覧／全内部リンク整合性チェック結果

---

## 7. 量産の手順（承認後の引き継ぎメモ）

1. CSS適用問題（5）を解消する。
2. `write_song_page_rich()` を lang 対応にして英語版も生成できるようにする。
3. 全曲の `scorebook` を概要欄から取得して `song-page-content.js` に投入する。
4. `build-seo-pages.py` の `SONG_RICH_IDS` を全曲IDに拡張（または「rich をデフォルト化して
   簡易版 `write_song_page` を撤去」する。撤去する場合は影響範囲をレビューすること）。
5. `python3 build-seo-pages.py` → 検証スクリプト → `build-worker-assets.py` → デプロイ。
6. 既存URLは不変（slug据え置き）。canonical/hreflang/sitemap の自己整合を最終確認。

---

## 8. 補足：触ってよい／触ってはいけない

- 触ってよい：`write_song_page_rich()`、`assets/song-page.css`、`SONG_RICH_IDS`、
  `SERIES_RELEASE`、`SONG_PROFILE`、`song-page-content.js` の各曲データ。
- 触らない：**slug**（公開済みURL）、既存 `write_song_page()`（簡易版・量産済みページの生成元）、
  既存の他ページ生成ロジック。


---

## 9. Codex検証・仕上げ結果（2026-06-14）

### 検証したこと

- 作業場所は GoogleDrive 側の正規リポジトリ `/Users/c-chanai/Library/CloudStorage/GoogleDrive-kojikazu0520@gmail.com/マイドライブ/AI_Common/Project_codex` で確認。旧 `/Users/c-chanai/Documents/Project_codex` は未使用。
- `CHANGES.md` はリポジトリ直下に存在しなかったため読めなかった。
- `Project_cod567` のような化けたディレクトリは確認されなかった。
- `assets/song-page.css` は誤って `AI_Common/assets/song-page.css` に置かれていたため、正しい `Project_codex/assets/song-page.css` へ移動し、誤配置側は削除した。
- `python3 build-seo-pages.py` を実行し、492 URL の再生成に成功。

### 修正したこと

- `write_song_page_rich()` の基本情報を `dl/dt/dd` から `<table class="sr-info-table">` に変更。
- `assets/song-page.css` に `sr-info-table` 用スタイルを追加。
- `.sr-profile-avatar` を 56px に縮小。
- `.sr-cards` / `.sr-card` / `.sr-card-thumb` / `.sr-card-body` を補強し、カード高さ・サムネイル比率・本文縦積みが崩れにくい構造にした。
- `scorebook.cover` が無い場合は `.sr-score-cover` を出さず、`.sr-score.sr-score-nocover` でテキスト＋ボタンのみ表示することを確認。

### 実ファイル確認結果

- `SONG_RICH_IDS = {'I-4'}` のまま。rich出力対象は日本語 `/dq1/unknown-world/` の1曲のみ。
- `song-page-content.js` の `scorebook` 追加は `I-4` のみ。ほかの曲への scorebook 追加は無し。
- `/dq1/unknown-world/index.html` は rich 版で生成済み。
- `/en/dq1/unknown-world/` と他曲ページには `song-rich` / `sr-info-table` / `assets/song-page.css` は出力されず、従来版のまま。
- 参考楽譜セクションは `sr-score sr-score-nocover` になり、誤った `/assets/score-best-album-cover.jpg` は出力されていない。

### ブラウザ確認結果

ローカルサーバ `python3 -m http.server 8000` で `http://localhost:8000/dq1/unknown-world/` をChrome表示確認。

- `styles.css`、`assets/lite-yt-embed.css`、`assets/song-page.css` は `document.styleSheets` に読み込まれている。
- `.sr-lead-grid` は `display: grid` で、デスクトップでは動画＋基本情報の2カラムになっている。
- 基本情報は `<table class="sr-info-table">` で表示され、`main` 内の `<dl>` は0件。
- プロフィールアイコンは 56px x 56px。
- 関連カードはデスクトップ確認時に同一行で高さが揃っていた。
- JSON-LD は `WebSite` / `BreadcrumbList` / `VideoObject` を確認。
- canonical は `https://dqpiano.com/dq1/unknown-world/`。
- hreflang は ja/en/x-default の3件。
- og:image は YouTube hqdefault サムネイル。

### 残TODO

- 正しい公式スコアブック表紙画像が用意できるまでは、参考楽譜画像は非表示のまま維持する。
- モバイル実機幅での最終視認は未実施。CSS上は860px以下で1カラム化するが、量産前に実機またはDevToolsで確認する。
- Claude作業メモにあるCSS未適用問題は、Codex側のChrome確認では再現しなかった。原因はファイル誤配置またはClaude側プレビュー環境の問題だった可能性が高い。
- 量産前に `scripts/validate-song-pages.py` のような検証スクリプトを追加し、canonical/hreflang/JSON-LD/内部リンク/scorebook cover条件を全曲で自動確認できるようにする。


---

## 10. 全曲 rich 版量産結果（2026-06-14）

### 実施内容

- 曲別ページの rich 版テンプレート `write_song_page_rich()` を日本語・英語の両方に対応。
- 曲別ページは全件 rich 版をデフォルト生成に変更し、旧簡易版の出力分岐は使用しない状態にした。
- `SONG_RICH_IDS` は互換用の空セットとして残し、量産対象の制御には使わない。
- `python3 build-seo-pages.py` を実行し、492 URL の再生成に成功。

### 生成件数確認

- 日本語曲別ページ: 212件
- 英語曲別ページ: 212件
- rich 版曲別ページ: 424件
- 旧曲別ページ判定マーカー: 0件

確認条件:

- `assets/song-page.css` を読み込んでいること
- `sr-info-table` が存在すること
- 旧 `song-detail-page` / `song-detail-layout` マーカーが残っていないこと

### サンプリング確認

確認ページ:

- `/dq1/unknown-world/`
- `/en/dq1/unknown-world/`
- `/dq8/strange-world/`
- `/en/dq8/strange-world/`

確認結果:

- canonical は各ページの末尾スラッシュ付き自己URL。
- hreflang は ja / en / x-default の相互参照を出力。
- JSON-LD は `WebSite` / `BreadcrumbList` / `VideoObject` を出力。
- 動画埋め込みは `lite-youtube` を使用。
- 基本情報は `<table class="sr-info-table">` で出力。
- 参考楽譜は曲情報の直下に配置。
- `scorebook.cover` が無い場合、誤った代替表紙画像は出力しない。
- 曲別ページの演奏者欄はロゴサムネイル＋「演奏：しーちゃん」/ `Performed by C-chan` と、トップページプロフィールへのリンクのみ。

### 注意点・残TODO

- KMP楽譜として登録済みの曲は、ピアノ編曲を日本語 `今村 康`、英語 `Yasushi Imamura` として表示。
- scorebook未登録またはKMP以外の曲は、現時点では `要確認` / `Needs confirmation` と表示する実装。表示が多すぎる場合は、未確認行を非表示にする方針も検討する。
- 全曲の公式楽譜データ、ピアノ編曲者、参考楽譜リンクは今後のデータ精査が必要。
- デプロイは未実施。
