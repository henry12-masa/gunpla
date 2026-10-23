// 年代・グレード・作品・推し度の定義。seed/seed.json は scripts/build-seed.mjs がここから生成する。

// 年代は「発売年」で自動判定する(from〜to を含む)
export const ERAS = [
	{ slug: "kyukit", label: "旧キットの時代(1980〜1989)", short: "旧キット", from: 1980, to: 1989,
		lead: "1980年7月の1/144ガンダムから始まった最初のブーム。接着剤と塗料が前提の時代に、MSVやリアルタイプ、BB戦士が生まれた。" },
	{ slug: "hg", label: "HGと色分けの時代(1990〜1994)", short: "HG誕生", from: 1990, to: 1994,
		lead: "1990年にHG(ハイグレード)が登場し、成形色の組み合わせで色分けする発想が広がった。SDガンダムの人気も頂点を迎える。" },
	{ slug: "mg", label: "MG・PG誕生(1995〜1999)", short: "MG・PG", from: 1995, to: 1999,
		lead: "1995年にMG(マスターグレード)、1998年にPG(パーフェクトグレード)、1999年にHGUCが始まり、現在のグレード体系の骨格ができた。" },
	{ slug: "seed", label: "HGUCとSEEDの時代(2000〜2006)", short: "SEED世代", from: 2000, to: 2006,
		lead: "HGUCが宇宙世紀のMSを次々と立体化し、『SEED』『SEED DESTINY』で新しいファンが一気に増えた時代。" },
	{ slug: "rg", label: "ダブルオーとRGの時代(2007〜2012)", short: "RG誕生", from: 2007, to: 2012,
		lead: "『ガンダム00』と『UC』の展開、そして2010年のRG(リアルグレード)。1/144でここまでできるのか、という驚きの時代。" },
	{ slug: "build", label: "ビルドシリーズと鉄血(2013〜2019)", short: "ビルド世代", from: 2013, to: 2019,
		lead: "ガンプラそのものが主役のアニメ『ビルドファイターズ』と『鉄血のオルフェンズ』。改造と自由な遊び方が当たり前になった。" },
	{ slug: "now", label: "EGと水星の魔女(2020〜)", short: "現行", from: 2020, to: 2100,
		lead: "ニッパーなしでも組めるEG(エントリーグレード)と『水星の魔女』の大ヒット。品薄が社会現象になった今のガンプラ。" },
];

// グレード。キットの大きさ・作りの細かさの区分
export const GRADES = {
	pg: "PG(パーフェクトグレード)",
	mgex: "MGEX",
	mg: "MG(マスターグレード)",
	mgsd: "MGSD",
	rg: "RG(リアルグレード)",
	hg: "HG(ハイグレード)",
	eg: "EG(エントリーグレード)",
	re100: "RE/100",
	fm: "フルメカニクス",
	hirm: "ハイレゾリューションモデル",
	mega: "メガサイズモデル",
	sd: "SD・BB戦士",
	kyukit: "旧キット(ノーグレード)",
	other: "その他",
};

// 作品(シリーズ)
export const SERIES = {
	"0079": "機動戦士ガンダム",
	msv: "MSV・モビルスーツバリエーション",
	origin: "機動戦士ガンダム THE ORIGIN",
	"08ms": "第08MS小隊",
	"0080": "0080 ポケットの中の戦争",
	"0083": "0083 STARDUST MEMORY",
	thunderbolt: "機動戦士ガンダム サンダーボルト",
	zeta: "機動戦士Ζガンダム",
	zz: "機動戦士ガンダムΖΖ",
	sentinel: "ガンダム・センチネル",
	cca: "逆襲のシャア",
	unicorn: "機動戦士ガンダムUC",
	hathaway: "閃光のハサウェイ",
	f91: "ガンダムF91・クロスボーン",
	victory: "機動戦士Vガンダム",
	g: "機動武闘伝Gガンダム",
	wing: "新機動戦記ガンダムW",
	x: "機動新世紀ガンダムX",
	turna: "∀ガンダム",
	seed: "機動戦士ガンダムSEED・ASTRAY",
	destiny: "機動戦士ガンダムSEED DESTINY",
	"seed-freedom": "機動戦士ガンダムSEED FREEDOM",
	"00": "機動戦士ガンダム00",
	age: "機動戦士ガンダムAGE",
	build: "ガンダムビルドシリーズ",
	reco: "ガンダム Gのレコンギスタ",
	ibo: "機動戦士ガンダム 鉄血のオルフェンズ",
	witch: "機動戦士ガンダム 水星の魔女",
	gquuuuuux: "機動戦士Gundam GQuuuuuuX",
	sd: "SDガンダム(BB戦士・武者・騎士)",
};

export const TIERS = {
	essential: "定番",
	recommended: "推し",
	deep: "通好み",
};

export function eraForYear(year) {
	return ERAS.find((e) => year >= e.from && year <= e.to);
}
