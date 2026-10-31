// キットデータの発売年月を、全キット名簿(data/catalog/raw.json)と照合する。
// 使い方: node scripts/check-years.mjs data/kits-mg.mjs [...]
// 名簿は商品名の表記ゆれがあるので、グレードと発売年月が同じで名前が近いものを「一致」とみなす。
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { loadCatalog } from "../data/catalog/load.mjs";
import { resolve } from "node:path";

const raw = loadCatalog();
import { coreName as core, GRADE_OF_RAW } from "../data/kit-key.mjs";
const GRADE = Object.fromEntries(Object.entries(GRADE_OF_RAW).map(([raw, slug]) => [slug, raw]));
let bad = 0, miss = 0, ok = 0;
for (const file of process.argv.slice(2)) {
	const list = (await import(pathToFileURL(resolve(file)).href)).default;
	for (const kit of list) {
		const c = core(kit.title);
		const g = GRADE[kit.grades[0]];
		const cands = raw.filter((r) => (r.g === g || (g === "旧キット" && r.g === "その他")) && (core(r.n) === c || core(r.n).includes(c) || c.includes(core(r.n))));
		if (!cands.length) { miss++; console.log(`?? ${kit.slug} 「${kit.title}」${kit.released} 名簿に見つからない`); continue; }
		const exact = cands.filter((r) => core(r.n) === c);
		const pool = exact.length ? exact : cands;
		if (pool.some((r) => r.d === kit.released)) { ok++; continue; }
		bad++; console.log(`NG ${kit.slug} 「${kit.title}」掲載${kit.released} / 名簿 ${pool.slice(0, 4).map((r) => `${r.d} ${r.n}`).join(" | ")}`);
	}
}
console.log(`一致 ${ok} / 年月が違う ${bad} / 名簿で見つからない ${miss}`);
