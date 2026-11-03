import json,glob,os,sys,re
for f in sorted(glob.glob(sys.argv[1]+'/*.json')):
    try: d=json.load(open(f))
    except Exception as e:
        txt=re.sub(r'^\s*#.*$','',open(f).read(),flags=re.M); txt=re.sub(r',\s*([\]}])',r'\1',txt)
        try: d=json.loads(txt); 
        except Exception as e2: print("!!",f,e2); continue
    def p(ps,ind=''):
        out=[]
        for x in ps:
            s=f"{x.get('id')}:{x.get('type')}"
            if x.get('wstype'): s+=f"[{x['wstype']}]"
            if x.get('required') in (1,'1',True): s+='*'
            if x.get('allow_multiple') in (1,True,'1'): s+='+'
            if x.get('type')=='group': s+='{'+', '.join(p(x.get('group',[])))+'}'
            out.append(s)
        return out
    print(f"## {d.get('id')} ({d.get('script')}): {d.get('label')}")
    print("   ", '; '.join(p(d.get('parameters',[]))))
