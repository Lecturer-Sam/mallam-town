import re
def syllables(w):
    w=re.sub(r'[^a-z]','',w.lower())
    if not w: return 0
    g=re.findall(r'[aeiouy]+',w)
    n=len(g)
    if w.endswith('e') and n>1 and not w.endswith(('le','ee','ye')): n-=1
    return max(1,n)
def stats(text):
    text=re.sub(r'\*\*\[[^\]]*\]\*\*','',text)
    text=re.sub(r'\n?---\n?','\n',text)
    words=re.findall(r"[A-Za-z'’\-]+",text)
    nw=len(words)
    sents=[s for s in re.split(r'(?<=[.!?])\s+',text) if s.strip()]
    ns=max(1,len(sents))
    nsyl=sum(syllables(w) for w in words)
    wps=nw/ns; spw=nsyl/nw
    ease=206.835-1.015*wps-84.6*spw
    fk=0.39*wps+11.8*spw-15.59
    return nw,ns,fk,ease,wps
