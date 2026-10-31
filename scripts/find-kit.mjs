// 全キット名簿から商品名を探す: node scripts/find-kit.mjs <正規表現> [グレード]
import { readFileSync } from "node:fs";
import { loadCatalog } from "../data/catalog/load.mjs";
const kits = loadCatalog();
const [re, grade] = process.argv.slice(2);
const r = new RegExp(re, "i");
for (const k of kits) if (r.test(k.n.normalize("NFKC")) && (!grade || k.g === grade)) console.log(`${k.d}\t${k.g}\t${k.l ? "限定\t" : "\t"}${k.n}\t${k.w}`);
