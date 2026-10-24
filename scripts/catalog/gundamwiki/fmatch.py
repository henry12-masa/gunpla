import json,re,collections,unicodedata
R=json.load(open('fandom_rows.json',encoding='utf-8'))
raw=json.load(open('wiki/kits.json',encoding='utf-8'))+json.load(open('C:/Users/thier/Desktop/gunpla-curation/data/catalog/additions.json',encoding='utf-8'))
EXCL_PAGES=('Action Base','Builders Parts','Cup Noodle','Customize ','Figure-rise','Gashapla','GUNDAM Gunpla Package','Gundam Decal','Gundarium','Gunpla Battle','Gunpla Love','Haropla','Minipla','Speed Grade','Mobile Suit Gundam 30th','Real Experience','Gunpla Trial','Mobile Suit Sengokuden','GAT-X105')
MIXED=('The Gundam Base Tokyo','Gundam Side-F','Gundam Front Tokyo','Gundam Factory Yokohama','Gundam Next Future Pavilion','Limited Model','Gundam XMX')
def series_grade(s):
    s=s or ''
    for pat,g in [(r'^Master Grade SD|MGSD','MGSD'),(r'MGEX|Master Grade EX','MGEX'),(r'^Master Grade|^MG\b','MG'),(r'^Perfect Grade|^PG','PG'),(r'^Real Grade|^RG','RG'),(r'^High Grade|^HG','HG'),(r'^Entry Grade|^EG','EG'),
                  (r'^SD|BB Senshi|Cross Silhouette|EX-Standard','SD'),(r'Reborn|RE/100','RE/100'),(r'Mega Size','MegaSize'),(r'Full Mechanics','FM'),(r'Hi-Resolution','HiRM'),(r'^1/\d+|First Grade|Advanced Grade|EX Model|Hyper Hybrid|Jumbo','OLD')]:
        if re.search(pat,s): return g
    return None
def page_grade(p):
    if p.startswith(EXCL_PAGES): return None
    if p=='Master Grade SD': return 'MGSD'
    if p=='Universal Century Hard Graph': return 'HG'
    if p=='HG Customize Campaign': return 'HG'
    if p=='Option Parts Set': return None
    g=series_grade(p)
    if g: return g
    if re.search(r'Model Series|Action Models|Gunpla-kun',p):
        return 'SD' if p.startswith('SD') else 'OLD'
    return None
MON={m:i+1 for i,m in enumerate('January February March April May June July August September October November December'.split())}
def pdate(s):
    s=s or ''
    m=re.search(r'(\d{4})\s+(January|February|March|April|May|June|July|August|September|October|November|December)',s) or re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:\d{1,2},\s*)?(\d{4})',s)
    if m:
        a,b=m.groups()
        if a.isdigit(): return f"{a}-{MON[b]:02d}"
        return f"{b}-{MON[a]:02d}"
    m=re.search(r'\b(19[89]\d|20[0-3]\d)\b',s)
    return m.group(1) if m else ''
MODEL_RE=re.compile(r'(?:^|\s)([A-Za-z]{1,6}[A-Za-z0-9]*-[\w/\-\[\]\.]*\d[\w/\-\[\]\.]*)(?=\s|$)')
def norm_model(m): return re.sub(r'[^A-Z0-9]','',unicodedata.normalize('NFKC',m).upper())
def fmodel(name):
    m=MODEL_RE.search(name); return norm_model(m.group(1)) if m else ''
def rmodel(k):
    if k.get('m') and not k['m'].startswith('-'): return norm_model(k['m'].split(' ')[0])
    n=unicodedata.normalize('NFKC',k['n'])
    m=re.search(r'(?:^|\s)([A-Z]{1,6}[A-Z0-9]*-[\w/\-\[\]]*\d[\w/\-\[\]]*)',n)
    return norm_model(m.group(1)) if m else ''
GRP=lambda g: 'OLD' if g in ('旧キット','その他') else g
rows=[]
for r in R:
    g=page_grade(r['page'])
    if r['page'] in MIXED or g is None and r['page'] in MIXED:
        g=series_grade(r.get('c_Gunpla Series') or r.get('c_Grade') or r.get('c_Gunpla/Toy Series'))
    if not g: continue
    name=r.get('c_Model','')
    numk=[k for k in r if k.endswith('#')]
    num=r[numk[0]] if numk else ''
    if numk and 'B-Club' in numk[0]: continue
    if re.search(r'resin|B-Club|Conversion|Gashapon|Shokugan|candy toy',r.get('c_Notes','')+name,re.I): continue
    if not name or name in ('TBA','N/A'): continue
    d=pdate(r.get('c_Release Date',''))
    if not d or d>'2026-10': continue
    if g=='HG' and r.get('c_Scale') and r['c_Scale'] not in ('1/144',''): pass
    rows.append({'g':g,'d':d,'name':name,'num':num,'page':r['page'],'series':r.get('c_Series',''),'notes':r.get('c_Notes',''),'price':r.get('c_Yen Price',''),'scale':r.get('c_Scale',''),'model':fmodel(name),'excl':('Exclusive' in ' '.join(r['heads'])) or bool(re.search(r'exclusive',r.get('c_Notes',''),re.I)) or r['page'] in MIXED})
# dedupe fandom rows (same page appear twice e.g. in Gundam Base page and HGUC exclusives)
seen=set(); F=[]
for x in rows:
    kk=(x['g'],x['d'],re.sub(r'\W','',x['name'].lower()))
    if kk in seen: continue
    seen.add(kk); F.append(x)
print('fandom usable',len(rows),'dedup',len(F),collections.Counter(x['g'] for x in F))
# raw index
RAWG=collections.defaultdict(list)
for i,k in enumerate(raw): RAWG[GRP(k['g'])].append(i)
rm=[rmodel(k) for k in raw]
used=set()
def mdiff(a,b):
    if len(a)==4 or len(b)==4: return 0 if a[:4]==b[:4] else 99
    return abs((int(a[:4])*12+int(a[5:7]))-(int(b[:4])*12+int(b[5:7])))

COMPAT={'HG':('HG','OLD'),'OLD':('OLD','HG','SD'),'MG':('MG','MGEX'),'MGEX':('MGEX','MG'),'SD':('SD','OLD','MGSD'),'MGSD':('MGSD','SD')}
FLAGS=[(r'clear|crystal','クリア|クリスタル'),(r'coating','コーティング'),(r'metallic','メタリック'),(r'plat|chrome|gold|メッキ','メッキ|ゴールド|プレーティング'),(r'titanium','チタニウム'),(r'\bHD\b','HD'),(r'gundam base','ガンダムベース'),(r'titans','ティターンズ'),(r'expo','EXPO|エキスポ'),(r'Ver\.?\s*Ka','Ver\.?Ka'),(r'special','スペシャル'),(r'anniversary|30th|40th|45th','周年|30th|40th|45th|アニバーサリー'),(r'extra finish','エクストラフィニッシュ'),(r'revive','REVIVE'),(r'set\b','セット')]
def vers(s):
    return set(re.findall(r'Ver\.?\s*(\d\.\d|ka|one year war|evolve|g30th|gft|rf)',unicodedata.normalize('NFKC',s),re.I))
def penalty(x,k):
    n=unicodedata.normalize('NFKC',k['n']); p=0
    for e,j in FLAGS:
        if bool(re.search(e,x['name'],re.I)) != bool(re.search(j,n,re.I)): p+=1
    if {v.lower() for v in vers(x['name'])} != {v.lower() for v in vers(n)}: p+=2
    return p
stat=collections.Counter()
for pass_ in ('A','B'):
    cands=[]
    for xi,x in enumerate(F):
        if 'match' in x: continue
        if pass_=='A' and not x['model']: continue
        for g in COMPAT.get(x['g'],(x['g'],)):
            for i in RAWG[g]:
                if i in used: continue
                if pass_=='A' and rm[i]!=x['model']: continue
                dd=mdiff(x['d'],raw[i]['d'])
                if pass_=='A' and dd>3: continue
                if pass_=='B' and dd>0: continue
                pen=penalty(x,raw[i])
                if pass_=='B' and pen>0: continue
                cands.append((dd*3+pen+(0 if g==x['g'] else 1),xi,i))
    cands.sort()
    for sc,xi,i in cands:
        if 'match' in F[xi] or i in used: continue
        F[xi]['match']=i; F[xi]['pass']=pass_; F[xi]['score']=sc; used.add(i); stat[pass_]+=1
print(stat)
bym=collections.defaultdict(list)
for i,k in enumerate(raw):
    if i not in used: bym[(GRP(k['g']),k['d'])].append(i)
new=[x for x in F if 'match' not in x]
print('phaseB',stat['B'],'new',len(new),collections.Counter(x['g'] for x in new))
print('raw unmatched',sum(len(v) for v in bym.values()))
print(collections.Counter(x['d'][:3] for x in new))
json.dump(new,open('fandom_new.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump(F,open('fandom_all.json','w',encoding='utf-8'),ensure_ascii=False)

# ---- review dump
unm=[i for v in bym.values() for i in v]
def venue(x):
    t=x['notes']+' '+x['page']
    for pat,v in [(r'P-Bandai|Premium Bandai','プレミアムバンダイ限定'),(r'Gundam Base','ガンダムベース限定'),(r'Expo','ガンプラEXPO限定'),(r'Gundam Front Tokyo','ガンダムフロント東京限定'),(r'Side-F','ガンダムSIDE-F限定'),(r'Factory Yokohama','GUNDAM FACTORY YOKOHAMA限定'),(r'Next Future','ガンダムネクストフューチャーパビリオン限定'),(r'Hobby Japan|Dengeki|magazine|Gundam Ace|Model Graphix','雑誌付録/誌上限定'),(r'C3|Chara Hobby|Japan Fantastic|Wonder Festival|convention|event|Hobby Fair|festival','イベント限定'),(r'Hong Kong|China|Taiwan|Korea|Asia|overseas|Singapore|Thailand|Shanghai','海外限定'),(r'lottery|Ichiban','一番くじ等'),(r'limited|exclusive','限定')]:
        if re.search(pat,t,re.I): return v
    return ''
out=[]
for n,x in enumerate(new):
    x['id']=n; x['venue']=venue(x) if x['excl'] or re.search(r'exclusive|limited',x['notes'],re.I) else ''
    c=[raw[i] for i in unm if GRP(raw[i]['g']) in COMPAT.get(x['g'],(x['g'],)) and mdiff(x['d'],raw[i]['d'])<=4]
    out.append(f"{n}|{x['g']}|{x['d']}|{x['name']}|{x['venue']}|{x['series'][:30]}|{x['notes'][:70]}")
    for k in c[:6]: out.append(f"    ~ {k['d']} {k['n']}")
open('review.txt','w',encoding='utf-8').write('\n'.join(out))
json.dump(new,open('fandom_new.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(out))
