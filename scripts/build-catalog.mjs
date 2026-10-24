// data/catalog/raw.json(全キット名簿)を、サイトが読む形に分割して public/catalog-data/ に書き出す。
//   public/catalog-data/index.json            グレードごとの件数と年ごとの件数
//   public/catalog-data/<グレード>/<年>.json  その年の発売キット [[発売年月, 商品名, 作品, 限定なら1, 厳選slug], ...]
// 厳選キット(data/catalog.mjs)と商品名・発売年月が一致するものには、キットページへのリンク用に slug を付ける。
// data/catalog/gundamwiki.json は、英語版ファンWiki「Gundam Wiki」から足した限定品など(scripts/catalog/gundamwiki/)。
// data/catalog/additions.json は、元の記事に載っていないキットを手で足す分。
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { games } from "../data/catalog.mjs";
import { GRADES } from "../data/taxonomies.mjs";
import { coreName, GRADE_OF_RAW } from "../data/kit-key.mjs";

const read = (name) => JSON.parse(readFileSync(new URL(`../data/catalog/${name}`, import.meta.url), "utf8"));
const raw = [...read("raw.json"), ...read("gundamwiki.json"), ...read("additions.json")];
// 名簿の更新日(日本時間)
const TODAY = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
const OUT = new URL("../public/catalog-data/", import.meta.url);

// 名簿での並び順(大きいグレードから)
const ORDER = ["pg", "mgex", "mg", "mgsd", "rg", "hg", "eg", "re100", "fm", "hirm", "mega", "sd", "kyukit", "other"];
const SHORT = { pg: "PG", mgex: "MGEX", mg: "MG", mgsd: "MGSD", rg: "RG", hg: "HG", eg: "EG", re100: "RE/100", fm: "フルメカニクス", hirm: "ハイレゾ", mega: "メガサイズ", sd: "SD・BB戦士", kyukit: "旧キット", other: "その他" };

// 厳選キットの索引: グレード+商品名のキー
const curated = new Map();
for (const g of games) curated.set(`${g.grades[0]}|${coreName(g.title)}|${g.released}`, g);

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });

const index = [];
let linked = 0;
for (const slug of ORDER) {
	const list = raw.filter((k) => GRADE_OF_RAW[k.g] === slug).sort((a, b) => a.d.localeCompare(b.d) || a.n.localeCompare(b.n, "ja"));
	if (!list.length) continue;
	const byYear = new Map();
	for (const k of list) {
		const year = k.d.slice(0, 4);
		const hit = curated.get(`${slug}|${coreName(k.n)}|${k.d}`);
		const row = [k.d, k.n, k.w, k.l ? 1 : 0];
		if (hit) { row.push(hit.slug); linked++; }
		if (!byYear.has(year)) byYear.set(year, []);
		byYear.get(year).push(row);
	}
	mkdirSync(new URL(`${slug}/`, OUT), { recursive: true });
	const years = [];
	for (const [year, rows] of [...byYear].sort()) {
		writeFileSync(new URL(`${slug}/${year}.json`, OUT), JSON.stringify(rows));
		years.push([Number(year), rows.length]);
	}
	index.push({ slug, label: GRADES[slug], short: SHORT[slug], count: list.length, dl: list.filter((k) => k.l).length, years });
}
const total = index.reduce((n, p) => n + p.count, 0);
writeFileSync(new URL("index.json", OUT), JSON.stringify({ updated: TODAY, total, grades: index }));
console.log(`全キット名簿: ${total}件 / ${index.length}グレード(厳選キットへのリンク ${linked}件 / 厳選${games.length}件)`);
