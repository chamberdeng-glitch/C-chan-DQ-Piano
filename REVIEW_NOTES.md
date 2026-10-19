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

---

## 11. お問い合わせフォーム・プライバシーポリシー（2026-10-19）

状態: **ローカル実装・自動テスト完了。Cloudflare設定と実メール試験は未実施。デプロイ未実施。**

### 11.1 変更ファイル一覧

- `src/worker.js`: `/api/contact` と `/api/contact/config` を静的配信より先に処理するルートを追加。
- `src/contact.js`: Origin/Referer検査、16KB制限、入力検証、Turnstile検証、ブロックリスト、ハッシュ化レート制限、分類、メール送信を実装。
- `config/contact-classification.json`: `[RIGHTS]` と `[NG]` の編集可能な公開キーワード設定。
- `assets/contact.js`: フォーム送信、二重送信防止、Turnstileの期限切れ・失敗時のリセット、汎用結果表示。
- `assets/contact.css`: 既存配色・余白に合わせたフォーム、プライバシーポリシー、モバイル表示。
- `build-seo-pages.py`: 日英のcontact/privacyページ生成、全ページの法務フッター、canonical/hreflang/sitemap登録。
- `build-worker-assets.py`: `contact/` と `privacy/` を公開アセットへ追加。
- `wrangler.jsonc`: `CONTACT_EMAIL` の`send_email` binding宣言を追加。
- `tests/contact.test.mjs`: API、分類、レート制限、UTF-8、Reply-To、失敗系の単体テスト。
- `scripts/validate-contact.py`: 生成ページ、SEO、Turnstileの読み込み範囲、フッター、秘密情報の静的検査。
- `.github/workflows/deploy.yml`: 将来のデプロイ前にcontact関連JavaScript、単体テスト、生成ページ検証を実行。
- 生成物: `/contact/`、`/en/contact/`、`/privacy/`、`/en/privacy/`、既存生成ページ、`sitemap.xml`、`dist/`。

依存パッケージは追加していない。

### 11.2 設計判断

#### API実装方式

- 既存のCloudflare Workerに`POST /api/contact`を追加した。ホスティング、フレームワーク、ビルド方式は変更していない。
- `GET /api/contact/config`は公開情報であるTurnstile Site Keyだけを返す。これにより実Site Keyを静的HTMLへ直書きせずCloudflare環境変数で設定できる。
- POST以外は405、16KB超過は413、Origin/Referer不一致または両方欠落は403、Content-Type不一致は415、入力・Turnstile不正は400、レート超過は429、設定不足は503、メール送信失敗は502とする。
- 名前・メールへのCR/LFは拒否し、本文はtext/plainとしてのみ送る。本文・名前・メールをログ、DB、KVへ保存しない。

#### Turnstile検証方式

- サーバーからCloudflare Siteverifyへ毎回送信し、`success`、`hostname`、`action=contact`を検査する。
- トークンは公式仕様どおり5分で期限切れ・1回限り。期限切れや再利用は`timeout-or-duplicate`を含む失敗として400にする。
- 本番Secretは`TURNSTILE_SECRET_KEY`、公開Site Keyは`TURNSTILE_SITE_KEY`で管理する。
- Cloudflare公式テストキーの利用手順は後述。実装テストではSiteverifyをモック化し、成功・失敗・期限切れ・再利用を区別した。

#### レート制限方式

- Workers Rate Limiting bindingは現行仕様で設定期間が10秒または60秒に限られ、IP 5回/時、20回/日、メール3回/日、全体200回/日をそのまま表現できないため採用しなかった。
- `CONTACT_RATE_LIMITS` Workers KVで固定時間窓を実装した。IPとメールは`CONTACT_HASH_SALT`を使ったHMAC-SHA-256のみをキーに含め、生値は保存しない。IP時間キーは1時間、日次キーは24時間で失効する。
- 同一キーへの1秒1書き込み制限を避けるため、カウンタの上書きではなく送信ごとの一意キーを作り、prefixの件数を数える。200件/日の上限まで最大約800書き込み/日で、Freeの1,000書き込み/日以内を想定する。
- 同一Worker isolate内はロックで直列化する。同時リクエストのテストは5件成功・6件目429を確認した。
- KVは結果整合であり、別isolate・別coloの完全な原子性は保証しない。短時間の同時送信で上限超過が通る可能性は既知の制限として残る。
- 制限値は`CONTACT_RATE_LIMITS_JSON`で変更できる。権利関連であってもレート制限を回避しない。

#### メール送信方式

- `CONTACT_EMAIL`の`send_email` bindingを使用する。
- 2026-10-15更新の公式Workers APIは、新規実装では生RFC 5322 MIMEではなく構造化`send()`を推奨している。そのため追加ライブラリなしで`from`、`to`、`subject`、`text`、`replyTo`を渡す。Cloudflare側がMIME-Version、Content-Type、Content-Transfer-Encoding等を生成する。
- 送信先は`CONTACT_TO_EMAIL`から取得する。実設定値は`dqpiano.c@gmail.com`で、ソースコードには記載していない。
- 送信元は`CONTACT_FROM_EMAIL`から取得する。想定値は`contact-form@dqpiano.com`。
- Reply-Toは検証済みのフォーム入力メールアドレスとし、Gmailの通常の返信操作で問い合わせ者へ返信できる形にする。
- Cloudflare API受付成功とGmail受信トレイへの最終配送は別である。`send()`が例外を返した場合は成功扱いにしない。

#### スパム分類方式

- `config/contact-classification.json`をNFKC正規化・小文字化して照合する。
- `[RIGHTS]`が一致した場合は排他的にし、URL数やNGワードにかかわらず`[LINKS]`、`[NG]`、`[REPEAT]`を付けない。
- `[RIGHTS]`でない場合だけURL3件以上、NGワード、同一行3回以上の繰り返しを判定する。複数タグを許可し、分類だけを理由に破棄しない。
- ブロックリストとHoneypotだけはメールを送らず200を返し、理由をクライアントへ開示しない。

#### 秘密情報

- 実値をリポジトリへ保存しない。`TURNSTILE_SECRET_KEY`、`CONTACT_HASH_SALT`、`CONTACT_TO_EMAIL`、個別ブロックリストはCloudflare secretを推奨する。
- Site Key、許可オリジン、許可ホスト名、送信元、制限値はCloudflare環境変数で管理できる。
- `CONTACT_TO_EMAIL`が無い、KV bindingが無い、メールbindingが無い等の場合はメールを送らず503にする。

#### SEO・CSP・既存サイトとの整合性

- 新規4ページは既存の`make_head()`、`topbar()`、`shell()`を使い、末尾スラッシュ、canonical、ja/en/x-default hreflang、JSON-LD、sitemapを既存規約に合わせた。
- 既存CSPと`_headers`は存在しなかったため、新しいCSPを全体へ追加していない。Turnstile公式で必要な`script-src`と`frame-src`は、将来CSPを導入する場合に限りcontactページへ追加する。
- Turnstile外部スクリプトは日英contactページだけで読み込む。
- 既存フッターの著作権・言語リンクを残し、Contact/Privacyと非公式ファンサイト表記だけを追加した。

### 11.3 必要な環境変数・binding

| 名前 | 種別 | 用途 | 推奨設定 |
|---|---|---|---|
| `TURNSTILE_SITE_KEY` | 環境変数 | contactページへ返す公開Site Key | Cloudflare Worker Settings |
| `TURNSTILE_SECRET_KEY` | secret | Siteverify検証 | Cloudflare Worker Secret |
| `CONTACT_TO_EMAIL` | secret/環境変数 | 固定送信先 | `dqpiano.c@gmail.com` |
| `CONTACT_FROM_EMAIL` | 環境変数 | 固定送信元 | `contact-form@dqpiano.com` |
| `CONTACT_HASH_SALT` | secret | IP・メールのHMAC | 十分に長いランダム値 |
| `CONTACT_ALLOWED_ORIGINS` | 環境変数 | POSTを許可するorigin | 既定`https://dqpiano.com` |
| `CONTACT_ALLOWED_HOSTNAMES` | 環境変数 | Turnstile hostname | 既定`dqpiano.com` |
| `CONTACT_TURNSTILE_ACTION` | 環境変数 | Turnstile action | 既定`contact` |
| `CONTACT_RATE_LIMITS_JSON` | 環境変数 | 制限値の上書き | 例`{"ipHour":5,"ipDay":20,"emailDay":3,"globalDay":200}` |
| `CONTACT_BLOCKED_EMAILS` | secret | カンマ/改行区切りの個別アドレス | 必要時のみ |
| `CONTACT_BLOCKED_DOMAINS` | secret | カンマ/改行区切りのドメイン | 必要時のみ |
| `CONTACT_EMAIL` | `send_email` binding | Cloudflare Email送信 | `wrangler.jsonc`に名前のみ宣言済み |
| `CONTACT_RATE_LIMITS` | Workers KV binding | 24時間以内のレート制限イベント | ユーザーがnamespace作成・binding登録 |

KV namespace IDはユーザーのCloudflareアカウント固有なのでリポジトリへ仮値を記載していない。`CONTACT_RATE_LIMITS` bindingはデプロイ前にDashboardまたは有効なWrangler環境設定へ追加すること。

### 11.4 ユーザーが行うCloudflare設定

#### Turnstile

1. Cloudflare DashboardでTurnstileウィジェットを作成し、許可hostnameを`dqpiano.com`にする。
2. Site Keyを`TURNSTILE_SITE_KEY`環境変数へ登録する。
3. Secret Keyを`TURNSTILE_SECRET_KEY` secretへ登録する。
4. ローカル/テストでは公式テストSite Key `1x00000000000000000000AA` と成功Secret `1x0000000000000000000000000000000AA`を使用できる。失敗Secretと再利用Secretも公式テストページに記載されている。本番Secretと混在させない。

#### Email Routing、受信先、送信元、binding

1. Compute > Email Service > Email Routingで`dqpiano.com`のEmail Routingを有効化する。
2. Destination Addressesへ`dqpiano.c@gmail.com`を登録する。
3. Gmailに届くCloudflare認証メールを開き、送信先を認証する。
4. 送信元`contact-form@dqpiano.com`を利用できるようにする。固定の認証済み宛先へ送る無料経路では、送信元はEmail Routingのonboard済みドメインに属している必要がある。DashboardがEmail Sendingドメインのonboardingを要求する場合は、案内される`cf-bounce` MX、SPF、DKIM、DMARCを確認して設定する。既存SPFがある場合は重複TXTを作らず統合する。
5. Workerへ`CONTACT_EMAIL`という名前の`send_email` bindingを登録する。コード側の送信先は`CONTACT_TO_EMAIL`で固定し、認証済み1件以外へは設定しない。
6. `CONTACT_TO_EMAIL=dqpiano.c@gmail.com`と`CONTACT_FROM_EMAIL=contact-form@dqpiano.com`をWorkerの環境設定へ登録する。
7. 実フォームから日本語・英語を含むテストメールを送り、Cloudflare Email sending metrics/logsとGmail受信を確認する。Email Routing summaryではWorker送信が「dropped」と表示されても配送成功の場合があるため、Outbound側のログを見る。
8. Gmailで「返信」を押し、宛先がフォーム入力者のメールアドレス（Reply-To）になることを確認する。`From`は`contact-form@dqpiano.com`、`To`は`dqpiano.c@gmail.com`であることも確認する。
9. Gmailで件名フィルタを作成する。
   - `[RIGHTS]`: スター・重要マーク（受信トレイを維持）
   - `[LINKS]`: 専用ラベル、受信トレイをスキップ
   - `[NG]`: 専用ラベル、受信トレイをスキップ
   - `[REPEAT]`: 専用ラベル、受信トレイをスキップ
   - スパム系タグも自動削除しない。

#### KV、WAF、Bot Fight Mode

1. Workers KV namespaceを作成し、Workerへ`CONTACT_RATE_LIMITS`としてbindingする。
2. `CONTACT_HASH_SALT`をsecretとして登録する。
3. 必要に応じて`CONTACT_RATE_LIMITS_JSON`、`CONTACT_BLOCKED_EMAILS`、`CONTACT_BLOCKED_DOMAINS`を登録する。
4. WAF Rate Limitingは補助防御として`/api/contact`だけを対象に検討する。Freeは1ルール・10秒窓・IP単位のため、アプリ内の1時間/1日制限の代わりにはならない。正常送信を妨げない余裕のある閾値でManaged ChallengeまたはBlockを検討する。
5. Bot Fight ModeはFreeで利用できるがドメイン全体へ作用し、WAFでcontactだけを除外できない。正常閲覧やAPIを誤検知する可能性があるため、Security Analyticsを確認しながら利用可否を判断する。

Cloudflare Dashboard操作、認証メールの承認、secret登録、実メール試験はユーザー本人が行う。

### 11.5 Cloudflare公式仕様の確認結果

- Workers API: https://developers.cloudflare.com/email-service/api/send-emails/workers-api/
  - `send_email` bindingで構造化`send()`が利用可能。`text`と`replyTo`は専用フィールド。生MIMEはlegacy扱い。
- Send bindings: https://developers.cloudflare.com/email-service/configuration/send-bindings/
  - 宛先はアカウント内の認証済みDestinationである必要があり、送信元はonboard済みEmail Serviceドメインに属する必要がある。
- Routing addresses: https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/
  - Gmailへ認証メールを送りDestinationを有効化する。認証済みDestinationへのWorkers binding送信は全プランで無料。
- Email pricing/limits: https://developers.cloudflare.com/email-service/platform/pricing/ および https://developers.cloudflare.com/email-service/platform/limits/
  - 認証済みDestinationへの送信は月次quota・日次送信制限に算入されない。任意宛先へのOutbound Email SendingはWorkers Paidが必要。本件は認証済み固定宛先1件なので無料経路に合致する。
- Domain configuration: https://developers.cloudflare.com/email-service/configuration/domains/
  - Email Sendingをonboardする場合、Cloudflareが`cf-bounce`用MX、SPF、DKIM、DMARCを設定する。RoutingとSendingの認証レコードは別。
- Turnstile validation: https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
  - サーバー検証必須、トークンは5分・1回限り、hostname/action検査推奨。
- Turnstile CSP: https://developers.cloudflare.com/turnstile/reference/content-security-policy/
  - CSPがある場合は`script-src`と`frame-src`へ`https://challenges.cloudflare.com`が必要。本サイトには既存CSPが無いため今回は追加していない。
- Workers KV limits: https://developers.cloudflare.com/kv/platform/limits/
  - Freeは100,000 reads/日、1,000 writes/日、同一キー1 write/秒。KVは結果整合。
- WAF Rate Limiting: https://developers.cloudflare.com/waf/rate-limiting-rules/
  - Freeは1ルール、10秒の計数期間、IP characteristic。精密な到達件数保証ではない。
- Bot Fight Mode: https://developers.cloudflare.com/bots/get-started/bot-fight-mode/
  - Freeで利用可能だがドメイン全体へ作用し、WAF custom ruleでskipできない。

### 11.6 Gmailフィルタ案

上記11.4の件名フィルタを設定する。`[RIGHTS]`は見落とし防止のため受信トレイに残す。`[LINKS]`、`[NG]`、`[REPEAT]`はラベルを付けて受信トレイをスキップしても、自動削除しない。

### 11.7 ローカルテスト結果

- `node --test tests/contact.test.mjs`: 19テスト成功。
- `python3 scripts/validate-contact.py`: 新規4ページ、560フッター、canonical/hreflang/sitemap、Turnstile読込範囲、環境変数参照を検証して成功。
- `python3 build-seo-pages.py`: 556 URL生成成功。
- `python3 build-worker-assets.py`: 617公開アセット生成成功。
- モックで確認済み: 正常送信、Honeypot、blocklist、Turnstile成功/失敗/期限切れ/再利用、各入力境界、CRLF、同意なし、16KB、Origin/Referer、GET、メール失敗、全レート上限、同一isolate内同時送信、分類優先順位、UTF-8文字列とReply-To。
- 未実施: Cloudflare公式テストキーを使った実Siteverify通信、Cloudflare KV実環境、実Email binding、Gmail最終配送、Gmail Reply-To操作、モバイル実機、キーボード/スクリーンリーダー実機確認。

### 11.8 ロールバック

1. `contact/`、`en/contact/`、`privacy/`、`en/privacy/`とcontact用assetsを生成対象から外す。
2. `src/worker.js`から`/api/contact`とconfigルートを削除し、`src/contact.js`と分類configを撤去する。
3. `site_footer()`の追加リンク・非公式表記を外し、従来の著作権・言語リンクだけへ戻す。
4. Cloudflareで`CONTACT_EMAIL`と`CONTACT_RATE_LIMITS` bindingを解除する。
5. Turnstile widget、Email Routing/送信設定、KV namespace、関連secret・環境変数を削除する。

### 11.9 既知の制限・残課題

- Workers KVは結果整合のため、別isolate・別coloからの同時送信では一時的に制限値を超える可能性がある。WAFは補助防御であり、メール単位・日単位の代替にはならない。
- メールアドレス単位の制限は第三者が他人のアドレスを入力して枠を消費できる。権利連絡だけを無条件に回避させる実装はしていない。
- Turnstile、分類キーワード、blocklistには誤判定の可能性がある。分類ではメールを破棄しない。
- `send()`受付成功はGmail受信成功を保証しない。DashboardのEmail sending metrics/logsと実受信の両方を確認する。
- Cloudflare Email Serviceの画面名称・Beta状態・プラン条件は変更される可能性がある。設定時にDashboardの現行表示を再確認する。
- Email Routing/Email SendingのDNSを有効化する際、既存MX/SPF/DKIMとの競合を事前に確認する。

### 11.10 ユーザーへの確認事項

- メール送信先は`dqpiano.c@gmail.com`で確定済み。
- 未確定: お問い合わせメールの保存期間（`【要確認：対応完了後◯か月で削除】`）。
- フッター権利表記は、指定文言で最終承認済み。
- 未確定: プライバシーポリシーの運営者表記を活動名「しーちゃん / C-chan」のみにしてよいか。
