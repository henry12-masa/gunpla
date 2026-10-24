# ガンプラ全キット名簿を作る。
#  - グレード別ページ(MG/PG/RG/HGUC/EG/FM/BB戦士)の表
#  - 「ガンプラの一覧」の箇条書き(作品別・グレード別)
#  - 個別記事「SEED HG」の箇条書き
# 出力: kits.json  [{n:名前, g:グレード, s:スケール, d:YYYY-MM, w:作品, m:型式番号, l:限定なら1}]
import json, re, html, unicodedata
from html.parser import HTMLParser

def clean(s):
    s = html.unescape(s).replace('　', ' ')
    s = re.sub(r'\[\d+\]|\[注 ?\d+\]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def ym(s):
    m = re.search(r'(\d{4})年\s*(\d{1,2})月', s)
    if m: return f"{m.group(1)}-{int(m.group(2)):02d}"
    m = re.search(r'(\d{4})年', s)
    return m.group(1) if m else ''

LIMIT_WORDS = ('限定', 'プレミアムバンダイ', 'イベント', 'ガンダムベース', 'EXPO', 'SIDE-F', '一番くじ', '賞品', '特典', '非売品', 'コラボ', '付録', 'プロショップ', 'フロント東京', '同梱')

def is_limited(heads):
    return 1 if any(w in heads for w in LIMIT_WORDS) else 0

GRADE_RULES = [
    (r'^MGEX', 'MGEX'), (r'^MGSD', 'MGSD'), (r'^MG ', 'MG'), (r'^PG ?UNLEASHED|^PGU', 'PG'), (r'^PG ', 'PG'), (r'^RG ', 'RG'),
    (r'^HGUC', 'HG'), (r'^HGCE', 'HG'), (r'^HGAC', 'HG'), (r'^HGBF|^HGBD|^HGBM|^HGBC', 'HG'), (r'^HG ', 'HG'),
    (r'^ENTRY GRADE|^EG ', 'EG'), (r'^FULL MECHANICS|^フルメカニクス|^1/100 フルメカニクス', 'FM'), (r'^RE/100', 'RE/100'),
]

def grade_of(name, default):
    for pat, g in GRADE_RULES:
        if re.search(pat, name): return g
    return default

def scale_of(name):
    m = re.search(r'1/(\d+)', name)
    return f"1/{m.group(1)}" if m else ''

# ---------- 表のページ
ns = {}
src = open('tparse.py', encoding='utf-8').read()
exec(src[:src.index('out={}')], ns)
P = ns['P']

def grid(rows):
    g = []; pending = {}
    for r in rows:
        row = []; ci = 0; k = 0; cells = list(r)
        while k < len(cells) or ci in pending:
            if ci in pending:
                txt, left, th = pending[ci]; row.append((txt, th))
                if left <= 1: del pending[ci]
                else: pending[ci] = (txt, left - 1, th)
                ci += 1; continue
            c = cells[k]; k += 1
            for _ in range(c['cs']):
                row.append((c['t'], c['th']))
                if c['rs'] > 1: pending[ci] = (c['t'], c['rs'] - 1, c['th'])
                ci += 1
        g.append(row)
    return g

TABLE_PAGES = {
    'p_マスターグレード.html': ('MG', '1/100'), 'p_パーフェクトグレード.html': ('PG', '1/60'), 'p_リアルグレード.html': ('RG', '1/144'),
    'p_ハイグレード・ユニバーサルセンチュリー.html': ('HG', '1/144'), 'p_ENTRY_GRADE.html': ('EG', '1/144'),
    'p_FULL_MECHANICS.html': ('FM', '1/100'), 'p_SDガンダム_BB戦士.html': ('SD', ''),
}
# SDガンダム BB戦士の記事は、BB戦士以外のSDシリーズ(クロスシルエット、EXスタンダードなど)の表も持つ。見出しからシリーズ名を付ける
SD_SERIES = [('クロスシルエット', 'SDガンダム クロスシルエット'), ('エクスタンダード', 'SDガンダム EXスタンダード'), ('ヒーローズ', 'SDW HEROES'),
             ('Gジェネレーション', 'SDガンダム Gジェネレーション'), ('ちーびー戦士', 'SDガンダム ちーびー戦士'), ('戦国英雄', 'SDガンダム戦国英雄'),
             ('三国伝 Brave Battle Warriors', 'BB戦士三国伝'), ('SDガンダムフォース', 'BB戦士 SDガンダムフォース')]
def sd_prefix(heads):
    for w, p in SD_SERIES:
        if w in heads: return p
    return 'BB戦士'

kits = []
for f, (grade, scale) in TABLE_PAGES.items():
    p = P(); p.feed(open(f, encoding='utf-8').read())
    for tb in p.tables:
        rows = tb['rows']
        if not rows: continue
        g = grid(rows)
        hdr = [clean(t) for t, _ in g[0]]
        if '商品名' not in hdr: continue
        heads = ' '.join(h for _, h in tb['heading'])
        if 'ガンプラ以外' in heads or 'ヱヴァンゲリヲン' in heads or 'キャラクタープラモデル' in heads: continue
        ni = hdr.index('商品名')
        di = next((i for i, h in enumerate(hdr) if h.startswith('発売')), None)
        wi = hdr.index('作品名') if '作品名' in hdr else None
        mi = hdr.index('型式番号') if '型式番号' in hdr else None
        for row in g[1:]:
            if len(row) <= ni or row[ni][1]: continue
            name = clean(row[ni][0])
            if not name or name == '商品名': continue
            d = ym(clean(row[di][0])) if di is not None and len(row) > di else ''
            if '予定' in (clean(row[di][0]) if di is not None and len(row) > di else ''): continue
            work = clean(row[wi][0]) if wi is not None and len(row) > wi else ''
            model = clean(row[mi][0]) if mi is not None and len(row) > mi else ''
            gr = grade_of(name, grade)
            if gr == 'RE/100' and not name.startswith('RE/100'): name = 'RE/100 ' + name
            if f.startswith('p_SD') and not re.match(r'^(BB|SD|LEGEND|LEGENDBB)', name): name = sd_prefix(heads) + ' ' + name
            PREFIX = {'MG': 'MG', 'PG': 'PG', 'RG': 'RG', 'EG': 'ENTRY GRADE', 'FM': 'FULL MECHANICS'}
            if f.startswith('p_ハイグレード'): PREFIX['HG'] = 'HGUC'
            if gr in PREFIX and not re.match(r'^(HG|MG|RG|PG|EG|ENTRY|FULL|1/\d+|フルメカ|MGEX|MGSD|PERFECT)', name):
                mm = model.split(' ')[0] if model and not model.startswith('-') and model.split(' ')[0] not in name else ''
                name = f"{PREFIX[gr]} {scale_of(name) or scale} {mm} {name}".replace('  ', ' ').replace('  ', ' ')
            if re.search(r'アクリル|エヴァ|ミレニアム|スター・?ウォーズ|X-?ウイング|STAR WARS', name): continue
            kits.append({'n': name, 'g': gr, 's': scale_of(name) or scale, 'd': d, 'w': work, 'm': model, 'l': is_limited(heads)})

# ---------- 一覧ページの箇条書き
class L(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.h = {}; s.cur = None; s.items = []; s.depth = 0; s.skip = 0; s.label = ''; s.lbuf = None; s.tbl = 0
    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag in ('sup', 'style', 'script'): s.skip += 1; return
        if tag == 'table': s.tbl += 1
        if tag in ('h2', 'h3', 'h4'): s.lbuf = ('h', int(tag[1]), ''); return
        if tag in ('dt',) or (tag == 'p' and s.depth == 0): s.lbuf = ('l', 0, ''); return
        if tag in ('ul', 'ol'): s.depth += 1
        if tag == 'li':
            if s.depth == 1 and not s.tbl: s.cur = {'t': '', 'heads': dict(s.h), 'label': s.label}
    def handle_endtag(s, tag):
        if tag in ('sup', 'style', 'script'): s.skip = max(0, s.skip - 1); return
        if tag == 'table': s.tbl -= 1
        if tag in ('h2', 'h3', 'h4') and s.lbuf and s.lbuf[0] == 'h':
            lv = s.lbuf[1]; txt = clean(re.sub(r'\[編集.*', '', s.lbuf[2]))
            s.h = {k: v for k, v in s.h.items() if k < lv}; s.h[lv] = txt; s.label = ''; s.lbuf = None; return
        if tag in ('dt', 'p') and s.lbuf and s.lbuf[0] == 'l':
            t = clean(s.lbuf[2])
            if t and len(t) < 40: s.label = t
            s.lbuf = None; return
        if tag in ('ul', 'ol'):
            s.depth -= 1
        if tag == 'li' and s.depth == 1 and s.cur is not None:
            s.items.append(s.cur); s.cur = None
    def handle_data(s, d):
        if s.skip: return
        if s.lbuf: s.lbuf = (s.lbuf[0], s.lbuf[1], s.lbuf[2] + d); return
        if s.cur is not None and s.depth == 1: s.cur['t'] += d

l = L(); l.feed(open('list.html', encoding='utf-8').read())
WORKS = [w for w in dict.fromkeys(it['heads'].get(3, '') for it in l.items if it['heads'].get(2) == '作品別') if w]
WORKS.sort(key=len, reverse=True)
def match_work(rest):
    r = unicodedata.normalize('NFKC', rest)
    for w in WORKS:
        wn = unicodedata.normalize('NFKC', w)
        if r.startswith(wn) and (len(r) == len(wn) or not re.match(r'[0-9A-Za-z]', r[len(wn)])): return w
    return ''
H3_GRADE = {'ハイグレード (HG)': 'HG', 'マスターグレード (MG)': 'MG', 'パーフェクトグレード (PG)': 'PG', 'リアルグレード (RG)': 'RG',
            'リボーンワンハンドレッド(RE/100)': 'RE/100', 'ハイレゾリューションモデル (HiRM)': 'HiRM', 'メガサイズモデル': 'MegaSize',
            'ENTRY GRADE(エントリーグレード)': 'EG', 'FULL MECHANICS[フルメカニクス]': 'FM'}
H3_SKIP = ('フィギュアライズ', 'ハロプラ')
LABEL_GRADE = [(r'^HG|ハイグレード', 'HG'), (r'^MG|マスターグレード', 'MG'), (r'^RG', 'RG'), (r'^PG', 'PG'), (r'^SD|BB戦士|SDBD|SDCS|SDW', 'SD'),
               (r'^RE/100', 'RE/100'), (r'^FM|FULL MECHANICS|フルメカ', 'FM'), (r'^EG|ENTRY', 'EG'), (r'^1/100|^1/144|^1/60|^1/250|^1/550', None)]
for it in l.items:
    h2 = it['heads'].get(2, ''); h3 = it['heads'].get(3, ''); h4 = it['heads'].get(4, ''); label = it['label']
    if h2 not in ('作品別', 'グレード別、他'): continue
    if any(x in h3 for x in H3_SKIP): continue
    h3g = next((g for k_, g in H3_GRADE.items() if re.sub(r'\W', '', k_) == re.sub(r'\W', '', h3)), None)
    if 'RE/100' in h3: h3g = 'RE/100'
    t = clean(it['t'])
    m = re.match(r'^(?:\d+\.\s*)?(.*?)(?:[（(]([^（）()]*?\d{4}年[^（）()]*?|時期不明)[）)])\s*(.*)$', t)
    if not m: continue
    name, date_s, rest = m.group(1).strip(), m.group(2), m.group(3).strip()
    if '予定' in date_s or not name: continue
    name = re.sub(r'\s*［\d+］', '', name)
    sc_h = re.match(r'^(?:限定モデル\s*)?(1/\d+)$', h4) or re.match(r'^(?:限定モデル\s*)?(1/\d+)$', label)
    if not scale_of(name) and sc_h: name = sc_h.group(1) + ' ' + name
    if 'メガサイズ' in h3 and not scale_of(name): name = '1/48 ' + name
    rest = re.sub(r'^[-–—]\s*', '', rest)
    if h2 == '作品別':
        work = h3 if h3 != 'ガンダムビルドシリーズ' else ''
        if not work or h3 in ('オルタナティブシリーズ',):
            work = match_work(rest) or work
        grade = grade_of(name, '')
        if not grade:
            for pat, g in LABEL_GRADE:
                if re.search(pat, label) or re.search(pat, h4):
                    grade = g; break
        if not grade:
            grade = '旧キット' if scale_of(name) and ym(date_s)[:4] and ym(date_s)[:4] < '2000' else 'その他'
        if grade == '旧キット' and h4 in ('グレード別、その他',): grade = 'その他'
        name = re.sub(r'^\d{3}\s+', '', name)
        if grade == 'RE/100' and not name.startswith('RE/100'): name = 'RE/100 ' + name
        if h3 == 'ガンダムビルドシリーズ' and grade == 'その他' and not scale_of(name) and not re.search(r'SD|BB|ガンダムベース', label + name): grade = 'HG'
        if grade == 'HG' and not re.match(r'^(HG|1/144)', name): name = 'HG 1/144 ' + name
    else:
        grade = grade_of(name, h3g or 'その他')
        work = match_work(rest)
    if grade == 'RE/100' and not name.startswith('RE/100'): name = 'RE/100 ' + name
    if grade == 'HiRM' and 'ハイレゾ' not in name: name = 'ハイレゾリューションモデル ' + name
    if grade == 'MegaSize' and 'メガサイズ' not in name: name = name.replace('1/48 ', '1/48 メガサイズモデル ', 1)
    model_m = re.match(r'^(?:[A-Z]+\s+)?(?:1/\d+\s+)?([A-Z]{1,6}[A-Z0-9]*-[\w/\-\[\]]*\d[\w/\-\[\]]*)\s', name)
    kits.append({'n': name, 'g': grade, 's': scale_of(name), 'd': ym(date_s), 'w': work, 'm': model_m.group(1) if model_m else '',
                 'l': 1 if is_limited(' '.join([h3, h4, label])) or re.search(r'限定|賞品|景品|付録|同梱|非売品', rest) else 0})

# ---------- 個別記事の箇条書き: 「SEED HG」(SEED系のHG・1/144コレクション・1/100・1/60。HGCE以前)
def article_items(f):
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'<sup.*?</sup>|<style.*?</style>', '', s, flags=re.S)
    t = re.sub(r'<h([2345])[^>]*>(.*?)</h\1>', lambda m: '\n#' + m.group(1) + ' ' + re.sub('<[^>]+>', '', m.group(2)) + '\n', s, flags=re.S)
    t = re.sub(r'<li>', '\n- ', t)
    t = html.unescape(re.sub(r'<[^>]+>', '', t))
    h = {}
    for line in t.split('\n'):
        line = line.strip()
        m = re.match(r'^#(\d) (.*)', line)
        if m: h = {k: v for k, v in h.items() if k < int(m.group(1))}; h[int(m.group(1))] = re.sub(r'\[編集.*', '', m.group(2)).strip(); continue
        if line.startswith('- '): yield dict(h), clean(line[2:])
SEED_WORK = {'ASTRAY': '機動戦士ガンダムSEED ASTRAY', 'MSV': '機動戦士ガンダムSEED MSV', 'DESTINY': '機動戦士ガンダムSEED DESTINY', 'STARGAZER': '機動戦士ガンダムSEED C.E.73 STARGAZER',
             'FRAME ASTRAYS': '機動戦士ガンダムSEED FRAME ASTRAYS', 'ASTRAY B': '機動戦士ガンダムSEED DESTINY ASTRAY', 'ASTRAY R': '機動戦士ガンダムSEED DESTINY ASTRAY'}
for h, t in article_items('p_SEED_HG.html'):
    h2, h3 = h.get(2, ''), h.get(3, '')
    m = re.match(r'^(.*?)[（(]([^（）()]*?\d{4}年[^（）()]*?)[）)]', t)
    if not m or '予定' in m.group(2): continue
    name = re.sub(r'^(R?\d{1,3})\s+', '', m.group(1).strip()); d = ym(m.group(2))
    work = '機動戦士ガンダムSEED'
    for w, full in SEED_WORK.items():
        if w in h3: work = full
    lim = 1 if '限定' in h3 else 0
    if h2.startswith('SEED HG'):
        grade = 'HG'
        if not name.startswith(('HG', '1/144')): name = 'HG 1/144 ' + name
        if 'リニューアル' in h3: name = name.replace('HG 1/144 ', 'HG 1/144 リマスター ', 1)
    else:
        sc = re.match(r'^(1/\d+)', h2).group(1)
        grade = 'その他'
        if not name.startswith('1/'): name = sc + ' ' + name
    mm = re.search(r'(?:^|\s)([A-Z]{1,6}[A-Z0-9]*-[\w/\-\[\]]*\d[\w/\-\[\]]*)\s', name)
    kits.append({'n': name, 'g': grade, 's': scale_of(name), 'd': d, 'w': work, 'm': mm.group(1) if mm else '', 'l': lim})

# ---------- 個別記事: 「SDガンダムワールド 三国創傑伝」のガンプラ節
# 日本ではガンダムベース東京・福岡の限定販売(2019〜2020年)が先で、2021年に一般販売。両方を載せる
s = open('p_SDガンダムワールド_三国創傑伝.html', encoding='utf-8').read()
s = s[s.index('id="ガンプラ"'):]
for m in re.finditer(r'<dt>(.*?)</dt>\s*</dl>\s*<ul>(.*?)</ul>', s, re.S):
    dt = clean(re.sub(r'<[^>]+>', '', m.group(1)))
    dates = re.findall(r'(\d{4})年(\d{1,2})月', dt)
    if not dates: continue
    for li in re.findall(r'<li>(.*?)</li>', m.group(2), re.S):
        n = clean(html.unescape(re.sub(r'<[^>]+>', '', li)))
        if 'ハロプラ' in n: continue
        first = f"{dates[0][0]}-{int(dates[0][1]):02d}"
        kits.append({'n': f'SDガンダムワールド 三国創傑伝 {n}（ガンダムベース限定先行販売）', 'g': 'SD', 's': '', 'd': first, 'w': 'SDガンダムワールド 三国創傑伝', 'm': '', 'l': 1})
        if len(dates) > 1:
            kits.append({'n': f'SDガンダムワールド 三国創傑伝 {n}', 'g': 'SD', 's': '', 'd': f"{dates[1][0]}-{int(dates[1][1]):02d}", 'w': 'SDガンダムワールド 三国創傑伝', 'm': '', 'l': 0})

# ---------- 整理
def core(n):
    n = unicodedata.normalize('NFKC', n)
    n = re.sub(r'^(HGUC|HGCE|HGAC|HGBF|HGBD:R|HGBD|HGBM|HGBC|HGFC|HG|MG|RG|PG|EG|ENTRY GRADE|MGEX|MGSD|SDW HEROES|SDガンダムワールド 三国創傑伝)\s+', '', n)
    n = re.sub(r'1/\d+\s*', '', n)
    n = re.sub(r'^[A-Z]{1,6}[A-Z0-9]*-[\w/\-\[\]]*\s+', '', n)
    n = re.sub(r'\[\d+\]|［\d+］', '', n)
    return re.sub(r'[\s・･\-_]', '', n).lower()
def key(k): return (core(k['n']), k['d'][:4], k['g'])
seen = {}; out = []
for k in kits:
    k['n'] = re.sub(r'^(HGUC|HGCE|HGAC|HG|MG|RG|PG)\s?/(\d+)\s', r'\1 1/\2 ', k['n'])  # 記事側で「1」が欠けた表記を直す
    if not k['s']: k['s'] = scale_of(k['n'])
    if not k['d']: continue
    if k['d'] > '2026-10': continue
    kk = key(k)
    if kk in seen:
        # SDW HEROESの表の000番は三国創傑伝のキットなので、三国創傑伝側の表記を残す
        if k['n'].startswith('SDガンダムワールド 三国創傑伝'): out[seen[kk]] = k
        continue
    seen[kk] = len(out); out.append(k)
mw = {}
cw = {}
for k in out:
    if k['w']:
        if k['m']: mw.setdefault(k['m'], k['w'])
        cw.setdefault(core(k['n']), k['w'])
for k in out:
    if not k['w']:
        k['w'] = mw.get(k['m'], '')
out.sort(key=lambda k: (k['d'], k['g'], k['n']))
json.dump(out, open('kits.json', 'w', encoding='utf-8'), ensure_ascii=False)
from collections import Counter
print('total', len(out), 'limited', sum(k['l'] for k in out))
print(Counter(k['g'] for k in out).most_common())
print(Counter(k['d'][:3] + '0s' for k in out))
print(Counter(k['w'] for k in out).most_common(25))
for k in out[::400]: print(k)
