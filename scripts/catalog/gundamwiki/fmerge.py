# Gundam Wiki(fandom)由来の追加分を、手で付けた日本語名(ja/*.tsv)と合わせて名簿の形にする
import json, re, glob, collections, unicodedata, sys
T = json.load(open('fandom_todo.json', encoding='utf-8'))
ALL = json.load(open('fandom_all.json', encoding='utf-8'))
raw = json.load(open('wiki/kits.json', encoding='utf-8'))
ans = {}
for f in sorted(glob.glob('ja/*.tsv')):
    for line in open(f, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip(): continue
        p = line.split('\t')
        ans[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else None)
missing = [x['id'] for x in T if x['id'] not in ans]
print('missing', len(missing), missing[:50])
bad = [k for k, v in ans.items() if v[0].endswith('?') or v[0].endswith('? ）')]
print('junk', bad)

CODE = [(r'\bHGBD:R-?\d', 'HGBD:R 1/144'), (r'\bHGUC[- ]?\d', 'HGUC 1/144'), (r'\bHGCE-?\d', 'HGCE 1/144'), (r'\bHGAC-?\d', 'HGAC 1/144'), (r'\bHGFC-?\d', 'HGFC 1/144'),
        (r'\bHGCC-?\d', 'HGCC 1/144'), (r'\bHGBF-?\d', 'HGBF 1/144'), (r'\bHGBD-?\d', 'HGBD 1/144'), (r'\bHGPG-?\d', 'HGPG'), (r'\bHG[A-Z0-9]*-?\d', 'HG 1/144'),
        (r'\bSDCS-?\d', 'SDガンダム クロスシルエット'), (r'\bSDEX-?\d', 'SDガンダム EXスタンダード'), (r'\bSDSS-?\d', 'SDガンダムワールド 三国創傑伝'), (r'\bSDWH-?\d', 'SDW HEROES'),
        (r'\bMGEX-?\d', 'MGEX 1/100'), (r'\bPGU-?\d', 'PG UNLEASHED 1/60')]
PAGE = {'High Grade Universal Century': None, 'High Grade Build Fighters': 'HGBF 1/144', 'High Grade Build Divers': 'HGBD 1/144', 'High Grade Build Divers Re:RISE': 'HGBD:R 1/144',
        "High Grade Petit'gguy": 'HGPG', 'HG Customize Campaign': 'HG', 'High Grade After Colony': 'HGAC 1/144', 'High Grade Gundam SEED': 'HG 1/144',
        'SD Gundam Cross Silhouette': 'SDガンダム クロスシルエット', 'SD Gundam EX-Standard': 'SDガンダム EXスタンダード', 'SD Gundam World Heroes Model Series': 'SDW HEROES',
        'SD Gundam World Sangoku Soketsuden Model Series': 'SDガンダムワールド 三国創傑伝', 'Universal Century Hard Graph': 'HGUC 1/144'}
GRADE_PREFIX = {'MG': 'MG 1/100', 'MGEX': 'MGEX 1/100', 'RG': 'RG 1/144', 'PG': 'PG 1/60', 'EG': 'ENTRY GRADE 1/144', 'FM': 'FULL MECHANICS 1/100', 'RE/100': 'RE/100 1/100',
                'HiRM': 'ハイレゾリューションモデル 1/100', 'MegaSize': '1/48 メガサイズモデル', 'MGSD': 'MGSD', 'SD': 'BB戦士', 'HG': 'HG 1/144'}
def prefix(x, name):
    g = x['g']
    if g == 'OLD': return ''
    if name.startswith('PG UNLEASHED'): return ''
    if g == 'HG' or g == 'SD' or g == 'MG':
        if x['page'] in PAGE and PAGE[x['page']]: return PAGE[x['page']]
        for pat, p in CODE:
            if re.search(pat, x['notes']):
                if g == 'MG' and not p.startswith('MG'): continue
                if (g == 'SD') == (not p.startswith(('HG', 'MG', 'PG'))): return p
        if g == 'HG':
            s = x['series']
            if 'SEED' in s: return 'HGCE 1/144'
            if 'Wing' in s: return 'HGAC 1/144'
            if 'G Gundam' in s: return 'HGFC 1/144'
            if x['page'] == 'High Grade Universal Century': return 'HGUC 1/144'
    return GRADE_PREFIX[g]
MODEL = re.compile(r'(?:^|\s)([A-Za-z]{1,6}[A-Za-z0-9]*-[\w/\-\[\]\.αβγι]*\d[\w/\-\[\]\.αβγι]*)(?=\s|$)')
# 英語の作品名 → 名簿の作品名(型式番号で一致した組から多数決)
wv = collections.defaultdict(collections.Counter)
for x in ALL:
    if 'match' in x and x.get('pass') == 'A' and x['series']:
        w = raw[x['match']]['w'] if x['match'] < len(raw) else ''
        if w and w != '-': wv[x['series']][w] += 1
WORK = {k: v.most_common(1)[0][0] for k, v in wv.items()}
out = []; drop = 0
for x in T:
    a = ans.get(x['id'])
    if not a or a[0] == '-': drop += 1; continue
    name, venue = a
    g = x['g']
    other = name.startswith('!O ')
    if other: name = name[3:]; g = 'OLD'
    pre = {1119: 'MG 1/100'}.get(x['id']) or prefix(dict(x, g=g), name)
    mm = MODEL.search(x['name'])
    model = mm.group(1) if mm else ''
    if pre and model and model not in name and not re.match(r'^(1/|FG|HY2M|ジャンボ|PG UNLEASHED|ガンプラくん|ザクプラくん|シャア専用ザクプラくん|G-3 ガンプラくん)', name) and g not in ('SD', 'MGSD'):
        name = f'{model} {name}'
    full = f'{pre} {name}'.strip()
    v = venue if venue is not None else x['venue']
    if v in ('限定', '海外限定'): v = '' if v == '限定' else v
    if v == '一番くじ等': v = '' if '一番くじ' in full else '一番くじ'
    if v and v not in full: full = f'{full}（{v}）'
    if g == 'OLD': rg = '旧キット' if x['d'][:4] < '2000' else 'その他'
    elif g == 'MGEX' or pre.startswith('MGEX'): rg = 'MGEX'
    else: rg = g
    lim = 1 if (x['excl'] or venue or x['venue']) else 0
    sc = re.search(r'1/(\d+)', full)
    out.append({'n': full, 'g': rg, 's': f'1/{sc.group(1)}' if sc else '', 'd': x['d'], 'w': WORK.get(x['series'], ''), 'm': model, 'l': lim, 'src': 'gw'})
print('kept', len(out), 'dropped', drop)
# 名簿(ウィキペディア由来)との重複を落とす: 比較キーが同じで、発売が半年以内
def core(n):
    n = unicodedata.normalize('NFKC', n)
    n = re.sub(r'^(HGUC|HGCE|HGAC|HGBF|HGBD:R|HGBD|HGBM|HGBC|HGFC|HGCC|HGPG|HG|MG|RG|PG UNLEASHED|PG|EG|ENTRY GRADE|MGEX|MGSD|RE/100|BB戦士|SDガンダム クロスシルエット|SDガンダム EXスタンダード|SDW HEROES|FULL MECHANICS|SDガンダムワールド 三国創傑伝)\s+', '', n)
    n = re.sub(r'1/\d+\s*', '', n)
    n = re.sub(r'(?:^|\s)[A-Z]{1,6}[A-Z0-9]*-[\w/\-\[\]]*\d[\w/\-\[\]]*', ' ', n)
    n = re.sub(r'（[^（）]*限定[^（）]*）|ガンダムベース限定|プレミアムバンダイ限定|\[\d+\]|［\d+］', '', n)
    return re.sub(r'[\s・･\-_\[\]［］（）()「」"“”]', '', n).lower()
def mon(d): return int(d[:4]) * 12 + (int(d[5:7]) if len(d) > 4 else 6)
GRP = lambda g: 'OLD' if g in ('旧キット', 'その他') else ('MG' if g == 'MGEX' else g)
idx = collections.defaultdict(list)
for k in raw: idx[(GRP(k['g']), core(k['n']))].append(k)
final = []; dup = []
seen = set()
for k in out:
    key = (GRP(k['g']), core(k['n']))
    hit = [r for r in idx.get(key, []) if abs(mon(r['d']) - mon(k['d'])) <= 6]
    if hit: dup.append((k['n'], k['d'], hit[0]['n'], hit[0]['d'])); continue
    if key + (k['d'],) in seen: dup.append((k['n'], k['d'], '(自己重複)', '')); continue
    seen.add(key + (k['d'],)); final.append(k)
print('dup vs wiki', len(dup))
for d in dup: print('  DUP', d)
final.sort(key=lambda k: (k['d'], k['g'], k['n']))
json.dump(final, open('gundamwiki.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('final', len(final), collections.Counter(k['g'] for k in final))
for k in final[::60]: print(k['d'], k['g'], k['n'], '|', k['w'])
