# fandom の表を読む: 各行 {page, heads, cols:{...}}
import json, re, glob, sys, collections
sys.path.insert(0,'wiki')
ns={}; src=open('wiki/tparse.py',encoding='utf-8').read(); exec(src[:src.index('out={}')],ns)
P=ns['P']
exsrc=open('wiki/extract.py',encoding='utf-8').read()
gsrc=exsrc[exsrc.index('def grid'):exsrc.index('TABLE_PAGES')]
exec(gsrc)
def clean(s): return re.sub(r'\s+',' ',re.sub(r'\[\s*\d+\s*\]|\[\s*note \d+\s*\]','',s.replace('\xa0',' '))).strip()
rows=[]; hdrs=collections.Counter()
for f in sorted(glob.glob('fandom/*.html')):
    s=open(f,encoding='utf-8').read(); title=s[s.index(':')+1:s.index('-->')]
    p=P(); p.feed(s)
    for tb in p.tables:
        if not tb['rows']: continue
        g=grid(tb['rows'])
        # header row = first row with th that includes 'Release'
        hi=next((i for i,r in enumerate(g[:3]) if any('Release' in t or 'Date' in t for t,_ in r)),None)
        if hi is None: continue
        hdr=[clean(t) for t,_ in g[hi]]
        hdrs[(' | '.join(hdr))]+=1
        sect=None
        for r in g[hi+1:]:
            vals=[clean(t) for t,_ in r]
            if all(th for _,th in r) or len(set(vals))==1:
                sect=vals[0]; continue
            d=dict(zip(hdr,vals))
            rows.append({'page':title,'heads':[h for _,h in tb['heading']],'sect':sect,**{'c_'+k:v for k,v in d.items()}})
json.dump(rows,open('fandom_rows.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(rows))
for h,n in hdrs.most_common(40): print(n,h)
