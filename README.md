# 組み継ぐ

1980年の1/144ガンダムから最新のHG・EGまで、いま作る価値のあるガンプラをグレード・作品・年代で横断するキュレーションサイト。

公開URL: https://gunpla.napoblog.com

[EmDash](https://github.com/emdash-cms/emdash)(Astro製CMS)で作り、Cloudflare Workers + D1 + R2 で動かしています。姉妹サイト「遊び継ぐ」(game-curation)と同じ作りです。

## ページ

| ページ | パス |
|---|---|
| トップ | `/` |
| キット一覧(年代・グレード・作品・推し度で絞り込み) | `/kits` |
| キットページ | `/kits/:slug` |
| 年表 | `/timeline` |
| グレードガイド | `/grades` |
| 全キット名簿(グレード別・年別) | `/catalog`, `/catalog/:グレード`, `/catalog/:グレード/:年` |
| 特集 | `/posts`, `/posts/:slug` |
| 検索 | `/search` |
| このサイトについて | `/pages/about` |
| プライバシーポリシー | `/privacy` |

## データ

- 厳選キットは `data/kits-*.mjs` に `data/entry.mjs` の `k()` で書く。本文は「どんなキット/組みどころ/ガンプラ史の中で/こんな人におすすめ」の4見出し。`data/catalog.mjs` が全ファイルを集める
- 発売年月は `node scripts/check-years.mjs data/kits-*.mjs` で全キット名簿と照合する。名簿にないキットは `data/catalog/additions.json` に足す
- 名簿から商品名を探す: `node scripts/find-kit.mjs <正規表現> [グレード]`
- `data/taxonomies.mjs` に年代・グレード・作品・推し度、`data/grades.mjs` にグレードガイドと道具のAmazonリンク、`data/features.mjs` に特集記事
- `node scripts/build-seed.mjs` で `seed/seed.json` を生成(seed は空のデータベースにだけ適用される)
- 公開中のサイトへの反映は `node scripts/sync-remote.mjs --url https://gunpla.napoblog.com`(先に `npx emdash login`)。キットに加えて特集と「このサイトについて」も同期する(`--posts-only` で特集だけ)

## 全キット名簿

日本語版ウィキペディア「ガンプラの一覧」と各グレードの記事、「SEED HG」「SDガンダムワールド 三国創傑伝」(CC BY-SA 4.0)から作り、ウィキペディアにない限定品などを英語版ファンWiki「Gundam Wiki」(CC BY-SA 3.0)から足しています。

1. `scripts/catalog/fetch.mjs <記事名...>` で記事のHTMLを取得
2. `python scripts/catalog/extract.py`(表は `tparse.py` で読む)で `kits.json` を作り、`data/catalog/raw.json` に置く
3. Gundam Wiki からの追加分は `scripts/catalog/gundamwiki/`(手順はその README)で `data/catalog/gundamwiki.json` を作る
4. `node scripts/build-catalog.mjs` で `raw.json` + `gundamwiki.json` + `additions.json` を `public/catalog-data/` に書き出す(静的アセット、ASSETSバインディングで読む)

## 定期更新

週2回(火・金)、`curation-sites-update` スキルで最新情報を反映する。新しい厳選は `data/kits-updates.mjs` に足し、名簿の追加は `data/catalog/` に入れる。本番DBへは `node scripts/sync-remote.mjs --url <サイト> --only <slug,...>` で変えたものだけを同期する(`--only` のときは特集・固定ページは書き直さない)。コミットの先頭は `[curation-update]`。

## 開発とデプロイ

```bash
npm install
npm run dev      # http://localhost:4321
npm run deploy   # astro build && wrangler deploy(手動デプロイ)
```

`main` ブランチに push すると、Cloudflare Workers Builds が自動でビルド・デプロイします(ビルド `npm run build`、デプロイ `npx wrangler deploy`)。ブランチごとのプレビュー版は本番と同じデータベースにつながるため、無効にしています。

`src/layouts/Base.astro` の `google-site-verification` は Search Console の所有権確認用なので消さないでください。

日本語の全文検索は trigram トークナイザが必要です。データベースを作り直したときは、管理者でログインした状態で各コレクション(kits / posts / pages)に対して `POST /_emdash/api/search/enable`(`{"collection": "...", "enabled": true, "tokenize": "trigram"}`)を実行してください。

当サイトはファンによる非公式のサイトで、株式会社BANDAI SPIRITSとは関係ありません。
