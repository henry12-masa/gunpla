// キットデータの書き方。解説本文は4つの見出しで組み立てる。
export const SECTIONS = ["どんなキット", "組みどころ", "ガンプラ史の中で", "こんな人におすすめ"];

/**
 * k(slug, 商品名, 型式番号, 発売年月"YYYY-MM", スケール, グレード, 作品(空白区切り), 推し度, ひとこと紹介, 一言, [本文4段落], Amazon検索語?)
 * 発売年月は全キット名簿(data/catalog/raw.json)と scripts/check-years.mjs で照合する。
 */
export const k = (slug, title, model, released, scale, grade, series, tier, summary, note, parts, amazonQuery = "") => ({
	slug,
	title,
	model,
	released,
	year: Number(released.slice(0, 4)),
	scale,
	grades: grade.split(" "),
	series: series.split(" "),
	tier,
	summary,
	note,
	body: parts.map((text, i) => `## ${SECTIONS[i]}\n${text}`).join("\n\n"),
	amazonQuery,
});
