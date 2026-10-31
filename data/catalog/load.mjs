// 全キット名簿を読み込む(ウィキペディア由来 + Gundam Wiki由来 + 手で足した分)。
// bandai-official.json は、公式の商品一覧にあって元の名簿に無かったキット。
// official-dates.json は、バンダイ ホビーサイトの商品一覧(公式)と照合して発売年月が違っていたものの上書き。
import { readFileSync } from "node:fs";

const read = (name) => JSON.parse(readFileSync(new URL(`./${name}`, import.meta.url), "utf8"));

export function loadCatalog() {
	const fixes = new Map(read("official-dates.json").map((f) => [f.n, f]));
	return [...read("raw.json"), ...read("gundamwiki.json"), ...read("additions.json"), ...read("bandai-official.json")].map((k) => {
		const f = fixes.get(k.n);
		if (!f) return k;
		// rename は公式の商品名(全角英数字は半角に)
		return { ...k, d: f.d, n: f.rename ? f.rename.normalize("NFKC") : k.n, official: true };
	});
}
