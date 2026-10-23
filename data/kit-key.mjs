// 商品名の表記ゆれを吸収した比較用のキー(グレード名・スケール・型式番号を外す)。
// 全キット名簿と厳選キットを突き合わせるときに使う。
export const coreName = (t) =>
	t.normalize("NFKC").toLowerCase()
		.replace(/^(hguc|hgce|hgac|hgbf|hgbd|hgfc|hgcc|hg|mg|rg|pg|pg unleashed|mgex|mgsd|re\/100|entry grade|full mechanics|bb戦士|legend bb|ハイレゾリューションモデル)\s+/, "")
		.replace(/1\/\d+\s*/g, "")
		.replace(/メガサイズモデル|フルメカニクス|ハイレゾリューションモデル/g, "")
		.replace(/\b[a-z]{1,6}[a-z0-9]*-[\w/\-[\]]*\s+/g, "")
		.replace(/[\s・:：\-－―‐~〜!！?？'’"「」『』()（）\[\]【】.,、。&＆/]/g, "");

/** 名簿のグレード表記 ⇔ サイトのグレードslug */
export const GRADE_OF_RAW = {
	PG: "pg", MGEX: "mgex", MG: "mg", MGSD: "mgsd", RG: "rg", HG: "hg", EG: "eg", "RE/100": "re100",
	FM: "fm", HiRM: "hirm", MegaSize: "mega", SD: "sd", 旧キット: "kyukit", その他: "other",
};
