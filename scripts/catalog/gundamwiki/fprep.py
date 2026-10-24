import json,re,collections
N=json.load(open('fandom_keep.json',encoding='utf-8'))
G={'OLD':'OLD','HG':'HG','MG':'MG','MGEX':'MG','SD':'SD','MGSD':'SD','RG':'RG','PG':'PG','EG':'EG','MegaSize':'MegaSize','FM':'FM','RE/100':'RE','HiRM':'HiRM'}
def key(x):
    n=re.sub(r'The Gundam Base Limited|​','',x['name'],flags=re.I)
    n=re.sub(r'[^a-z0-9]','',n.lower())
    return (G[x['g']],x['d'],n)
seen={};out=[];drop=0
for x in N:
    k=key(x)
    if k in seen: drop+=1; continue
    seen[k]=1; out.append(x)
print(len(N),'->',len(out))
out.sort(key=lambda x:(x['g'],x['d']))
lines=[]
for x in out:
    lines.append(f"{x['id']}|{x['g']}|{x['d']}|{x['name']}|{x['venue']}|{x['notes'][:75]}")
open('todo.txt','w',encoding='utf-8').write('\n'.join(lines))
json.dump(out,open('fandom_todo.json','w',encoding='utf-8'),ensure_ascii=False)
print(collections.Counter(x['g'] for x in out))
import unicodedata
raw=json.load(open('wiki/kits.json',encoding='utf-8'))
def nm(m): return re.sub(r'[^A-Z0-9]','',unicodedata.normalize('NFKC',m).upper())
def rmodel(k):
    n=unicodedata.normalize('NFKC',k['n'])
    m=re.search(r'(?:^|\s)([A-Z]{1,6}[A-Z0-9]*-[\w/\-\[\]]*\d[\w/\-\[\]]*)',n)
    return nm(k['m'].split(' ')[0]) if k.get('m') and not k['m'].startswith('-') else (nm(m.group(1)) if m else '')
RG={'旧キット':'OLD','その他':'OLD','HG':'HG','MG':'MG','MGEX':'MG','SD':'SD','MGSD':'SD','RG':'RG','PG':'PG','EG':'EG','MegaSize':'MegaSize','FM':'FM','RE/100':'RE','HiRM':'HiRM'}
byk=collections.defaultdict(list)
for k in raw: byk[(RG[k['g']],rmodel(k))].append(k)
def mon(d): return int(d[:4])*12+(int(d[5:7]) if len(d)>4 else 6)
lines=[]
for x in out:
    lines.append(f"{x['id']}|{x['g']}|{x['d']}|{x['name']}|{x['venue']}|{x['notes'][:75]}")
    if x['model']:
        for k in byk.get((G[x['g']],x['model']),[]):
            if abs(mon(k['d'])-mon(x['d']))<=12: lines.append(f"   ~ {k['d']} {'限' if k['l'] else ''} {k['n']}")
open('todo.txt','w',encoding='utf-8').write('\n'.join(lines))
print(len(lines))
