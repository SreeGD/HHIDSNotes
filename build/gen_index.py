import json, os
ROOT="/Users/sree/Projects/HHIDSNotes"
rows=json.load(open(f"{ROOT}/build/manifest.json"))
mod_names={1:"Module 1",2:"Module 2",3:"Module 3",4:"Module 4",5:"Module 5"}
def is_en(r):
    sc=f"{ROOT}/build/summaries/{r['slug']}.json"
    return os.path.exists(sc) and json.load(open(sc)).get('language')=='en'
tot=len(rows); eng=sum(1 for r in rows if is_en(r))
nonen=sum(1 for r in rows if r.get('language') and r['language']!='en' and not is_en(r))
ph=sum(1 for r in rows if r.get('link')=='link_placeholder')
out=["## Lecture Index","",
     "> 🔎 Browse another way: **[Thematic Index](THEMES.md)** (by topic) · **[Category Index](CATEGORIES.md)** (by course category).","",
     f"All **{tot} lectures** across 5 modules — **{eng} English** (fully enriched), **{nonen} non-English** (transcript only, flagged), **{ph} placeholders** (awaiting audio URL). Each row links to the enriched **Note** and the **Transcript**.",""]
by_mod={}
for r in rows: by_mod.setdefault(r['module_idx'],[]).append(r)
for m in sorted(by_mod):
    out.append(f"### {mod_names.get(m,'Module '+str(m))}\n")
    out.append("| Wk | Title | Category | Lang | Links |")
    out.append("|---:|-------|----------|:----:|-------|")
    for r in sorted(by_mod[m],key=lambda x:(x['week'],x['title'])):
        wk=r['week']; title=r['title'].replace('|','\\|').strip(); cat=(r.get('category') or '').replace('|','\\|')
        stem=f"module-{m}/week-{int(wk):02d}-{r['slug']}.md"
        if r.get('link')=='link_placeholder': lang='—'; links=f"[note](notes/{stem}) · _no audio_"
        elif is_en(r): lang='EN'; links=f"[note](notes/{stem}) · [transcript](transcripts/{stem})"
        else: lang={'ru':'RU','pl':'PL'}.get(r.get('language'),'?'); links=f"[note](notes/{stem}) · [transcript](transcripts/{stem})"
        out.append(f"| {wk} | {title} | {cat} | {lang} | {links} |")
    out.append("")
index="\n".join(out).strip()
readme=open(f"{ROOT}/README.md",encoding='utf-8').read()
pre=readme.split("## Lecture Index")[0]
post="## How it was made"+readme.split("## How it was made",1)[1]
open(f"{ROOT}/README.md","w",encoding='utf-8').write(pre+index+"\n\n"+post)
print("README lecture index regenerated")
