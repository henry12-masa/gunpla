# Gundam Wiki(英語版ファンWiki)からの追加分

全キット名簿のうち、日本語版ウィキペディアに載っていない限定品(プレミアムバンダイ・ガンダムベース・イベント・キャンペーン賞品など)を、
英語版ファンWiki「Gundam Wiki」(https://gundam.fandom.com/wiki/Category:Gunpla 、CC BY-SA 3.0)の各シリーズの記事から足したもの。
出力は `data/catalog/gundamwiki.json`(`src: "gw"`)。

作業フォルダ(リポジトリの外)に、ウィキペディア側の `extract.py` が作った `wiki/kits.json` と `tparse.py`・`extract.py` を置いて、次の順に動かす。

1. `node ffetch.mjs` … Category:Gunpla の記事を `fandom/` に取得
2. `python fparse.py` … 表を読んで `fandom_rows.json`
3. `python fmatch.py` … 型式番号と発売月で名簿と突き合わせ、名簿にないものを `fandom_new.json` に
4. `python ftrans.py` → `python fprep.py` … 番号付きの通常品(名簿と月ずれの重複)を除き、確認用の `todo.txt` を作る
5. `ja/*.tsv` … 英語の商品名に、人の手で日本語名を付けたもの(`-` は除外、3列目は販路の上書き、`!O ` はグレード「その他」)
6. `python fmerge.py` … 日本語名・グレードの接頭辞・販路を付け、名簿と半年以内の同名を落として `gundamwiki.json` を作る

海外だけの限定品(Tmall、GUNDAM docks など)と、名簿と重複する番号付きの通常品は除いている。発売年月はGundam Wikiの記載による。
