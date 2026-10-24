import json,re,collections,unicodedata
F=json.load(open('fandom_all.json',encoding='utf-8'))
raw=json.load(open('wiki/kits.json',encoding='utf-8'))+json.load(open('C:/Users/thier/Desktop/gunpla-curation/data/catalog/additions.json',encoding='utf-8'))
N=json.load(open('fandom_new.json',encoding='utf-8'))
WL={'Hyper Hybrid Model','Jumbo Grade','High Grade Fighting Action','HG Customize Campaign'}
def keep(x):
    if x['excl'] or x['num'] in ('','N/A','-','—'): return True
    if x['page'] in WL: return True
    if x['page']=='Perfect Grade' and 'Custom Set' in x['name']: return True
    if x['page']=='Entry Grade' and x['d'].startswith('2011'): return True
    return False
N=[x for x in N if keep(x)]
MODEL=re.compile(r'(?:^|\s)([A-Za-z]{1,6}[A-Za-z0-9]*-[\w/\-\[\]\.αβγ]*\d[\w/\-\[\]\.αβγ]*)(?=\s|$)')
def strip_model(n):
    return re.sub(r'\s+',' ',MODEL.sub(' ',n)).strip()
def jp_base(k):
    n=unicodedata.normalize('NFKC',k['n'])
    n=re.sub(r'^(HGUC|HGCE|HGAC|HGBF|HGBD:R|HGBD|HGBM|HGBC|HGFC|HGAW|HGPG|HGCC|HG|MG|RG|PG UNLEASHED|PG|EG|ENTRY GRADE|MGEX|MGSD|RE/100|BB戦士|SDガンダム クロスシルエット|SDガンダム EXスタンダード|SDW HEROES|FULL MECHANICS)\s+','',n)
    n=re.sub(r'^1/\d+\s+','',n)
    n=re.sub(r'^(?:[A-Z]{1,6}[A-Z0-9]*-[\w/\-\[\]]*\d[\w/\-\[\]]*)\s+','',n)
    return n.strip()
D={}
for x in F:
    if 'match' not in x or x.get('pass')!='A': continue
    k=raw[x['match']]
    D.setdefault((x['g'],strip_model(x['name']).lower()),jp_base(k))
    D.setdefault(('*',strip_model(x['name']).lower()),jp_base(k))
keys=sorted({k[1] for k in D},key=len,reverse=True)
res=[];suf=collections.Counter();un=0
for x in N:
    en=strip_model(x['name']); low=en.lower(); hit=None
    for kk in keys:
        if low.startswith(kk) and (len(low)==len(kk) or not low[len(kk)].isalnum()):
            hit=kk;break
    if hit:
        jp=D.get((x['g'],hit)) or D[('*',hit)]
        rest=en[len(hit):].strip()
        x['jp_base']=jp; x['rest']=rest
        suf[re.sub(r'\d+','#',rest)]+=1
    else: un+=1
print(len(N),'hit',len(N)-un,'unresolved',un)
for s,c in suf.most_common(150): print(c,repr(s))
json.dump(N,open('fandom_keep.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
