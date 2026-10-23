import json, re, sys, os
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.tables=[]; s.stack=[]; s.heading=None; s.htext=None; s.headings=[]
        s.skip=0; s.skipstack=[]; s.licount=0
    def handle_starttag(s,tag,a):
        a=dict(a)
        if tag in ('sup','style','script'):
            s.skip+=1; return
        if s.skip and tag in ('span','div','small','i','b','a','abbr','bdi'):
            s.skipstack.append(tag); s.skip+=1; return
        st=(a.get('style') or '').replace(' ','')
        cl=a.get('class') or ''
        if tag in ('span','div','small') and ('display:none' in st or 'sortkey' in cl or 'mw-cite-backlink' in cl):
            s.skipstack.append(tag); s.skip+=1; return
        if tag in ('h2','h3','h4','h5'):
            s.htext=''; return
        if tag=='table':
            s.stack.append({'heading':list(s.headings),'rows':[],'cls':a.get('class','')}); return
        if not s.stack: return
        t=s.stack[-1]
        if tag=='tr': t['rows'].append([])
        elif tag=='li' and len(s.stack)==1:
            s.licount+=1
            if s.licount>=2: s.skipstack.append('li'); s.skip+=1
        elif tag in ('td','th'):
            s.licount=0
            if not t['rows']: t['rows'].append([])
            t['rows'][-1].append({'th':tag=='th','t':'','rs':int(re.sub(r'\D','',a.get('rowspan','1')) or 1),'cs':int(re.sub(r'\D','',a.get('colspan','1')) or 1)})
        elif tag=='br':
            s._add(' / ')
    def handle_endtag(s,tag):
        if tag in ('sup','style','script'):
            s.skip=max(0,s.skip-1); return
        if s.skipstack and tag==s.skipstack[-1]:
            s.skipstack.pop(); s.skip=max(0,s.skip-1); return
        if tag in ('h2','h3','h4','h5') and s.htext is not None:
            lvl=int(tag[1]); txt=re.sub(r'\[編集\]','',s.htext).strip()
            s.headings=[h for h in s.headings if h[0]<lvl]+[(lvl,txt)]; s.htext=None; return
        if tag=='table' and s.stack:
            t=s.stack.pop()
            if not s.stack: s.tables.append(t)
    def _add(s,d):
        if s.stack and s.stack[-1]['rows'] and s.stack[-1]['rows'][-1]:
            s.stack[-1]['rows'][-1][-1]['t']+=d
    def handle_data(s,d):
        if s.skip: return
        if s.htext is not None: s.htext+=d; return
        if len(s.stack)==1: s._add(d)

out={}
pages=json.load(open('pages.json',encoding='utf-8'))
for pf,lst in pages.items():
    out[pf]=[]
    for t in lst:
        fn='html/'+re.sub(r'[\/:*?"<>| ]','_',t)+'.html'
        if not os.path.exists(fn): continue
        p=P(); p.feed(open(fn,encoding='utf-8').read())
        for tb in p.tables:
            tb['page']=t; out[pf].append(tb)
json.dump(out,open('tables.json','w',encoding='utf-8'),ensure_ascii=False)
# header summary
from collections import Counter
c=Counter()
for pf,tbs in out.items():
    for tb in tbs:
        if not tb['rows']: continue
        hdr=[x['t'].strip() for x in tb['rows'][0] if x['th']]
        c[(pf,' | '.join(hdr)[:120])]+=1
for (pf,h),n in sorted(c.items()): print(pf,n,h)
