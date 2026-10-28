#!/usr/bin/env python3
"""Build editable 408 chapters with content-related, collision-checked side notes."""
from pathlib import Path
import argparse, collections, hashlib, html, json, math, os, re, shutil, subprocess, textwrap
import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / 'common'
FIGURES = ROOT / 'figures'
BOXES = {'definition','theorem','proof','methodbox','example','pitfall','takeaway','recallcard','solution','wideblock','proposition','corollary'}
class Splice(list):
    pass

def cmd(args, cwd=None, data=None):
    p = subprocess.run(args, cwd=cwd, input=data, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError(' '.join(map(str,args))+ '\n' + p.stdout[-5000:] + p.stderr[-2000:])
    return p.stdout

def esc(s):
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(s))

def mdtex(s):
    s = cmd(['pandoc','-f','markdown+tex_math_dollars+tex_math_single_backslash','-t','latex','--wrap=none'],data=s).strip()
    for char,macro in {'⋯':r'\cdots','−':'-','→':r'\to','←':r'\leftarrow','≤':r'\le','≥':r'\ge','≠':r'\ne','×':r'\times'}.items():
        s=s.replace(char,r'\ensuremath{'+macro+'}')
    return s.replace('\\tightlist','')

def jwrite(p, obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')

def draw_map(ch):
    m=json.loads((ch/'map.json').read_text()); out=ch/'figures';out.mkdir(exist_ok=True)
    measure=ImageFont.truetype(str(COMMON/'fonts/NotoSansSC-Regular.otf'),16)
    # Split a large chapter tree into panels, keeping every knowledge node legible.
    groups=[];cur=[];weight=0
    for b in m['branches']:
        w=max(2,len(b.get('children',[])))
        if cur and weight+w>18:groups.append(cur);cur=[];weight=0
        cur.append(b);weight+=w
    if cur:groups.append(cur)
    files=[]
    for num,group in enumerate(groups,1):
        heights=[max(60,27+len(b.get('children',[]))*23) for b in group]
        height=sum(heights)+60; width=680
        rooty=height/2
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<g font-family="Noto Sans CJK SC, sans-serif" font-size="16" fill="#223644">',
             f'<rect x="8" y="{rooty-25}" width="140" height="50" rx="7" fill="#DDEFF5"/>',
             f'<text x="78" y="{rooty+5}" text-anchor="middle" font-weight="bold">{html.escape(m["title"][:12])}</text>']
        yy=25
        for b,h in zip(group,heights):
            cy=yy+h/2
            svg.append(f'<path d="M148,{rooty} H166 V{cy} H184" fill="none" stroke="#6F9AAE" stroke-width="1.5"/>')
            svg.append(f'<rect x="184" y="{cy-19}" width="164" height="38" rx="4" fill="#DFEFE6"/>')
            label=b['label']; lines=textwrap.wrap(label,width=10) or ['']
            for z,line in enumerate(lines[:2]):
                svg.append(f'<text x="266" y="{cy+(z-(len(lines[:2])-1)/2)*18+5}" text-anchor="middle" font-weight="bold">{html.escape(line)}</text>')
            children=b.get('children',[])
            for k,child in enumerate(children):
                # Allow child descriptions, but never shrink them to unreadable type.
                child=child.get('label',str(child)) if isinstance(child,dict) else str(child)
                liney=cy+(k-(len(children)-1)/2)*23
                svg.append(f'<path d="M348,{cy} H365 V{liney} H380" fill="none" stroke="#9BB1BA" stroke-width="1"/>')
                svg.append(f'<text x="387" y="{liney+5}">{html.escape(child)}</text>')
                if measure.getlength(child)>283:
                    raise ValueError(f'{m["id"]}: map label too long: {child}; shorten its label, keep conditions in prose')
            yy+=h
        svg+=['</g></svg>']
        name=f'map-{num:02}'; (out/(name+'.svg')).write_text('\n'.join(svg))
        cmd(['inkscape',str(out/(name+'.svg')),'--export-text-to-path','--export-type=pdf','--export-filename='+str(out/(name+'.pdf'))])
        cmd(['inkscape',str(out/(name+'.svg')),'--export-type=png','--export-dpi=180','--export-filename='+str(out/(name+'.png'))])
        files.append(name)
    return files

def draw_overview(ch):
    """A readable first-level chapter navigator; detailed trees stay in chapter-map.pdf."""
    m=json.loads((ch/'map.json').read_text())
    branches=m['branches'];height=max(160,48*len(branches)+40);width=680
    cy=height/2
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<g font-family="Noto Sans CJK SC,sans-serif" fill="#223644" font-size="18">',
         f'<rect x="8" y="{cy-35}" width="174" height="70" rx="7" fill="#DDEFF5"/>']
    title=m['title'];title_lines=[title[i:i+9] for i in range(0,len(title),9)]
    for i,line in enumerate(title_lines):
        svg.append(f'<text x="95" y="{cy+(i-(len(title_lines)-1)/2)*22+6}" text-anchor="middle" font-weight="bold">{html.escape(line)}</text>')
    for i,branch in enumerate(branches):
        y=20+i*48
        svg.extend([f'<path d="M182,{cy} H206 V{y+19} H230" fill="none" stroke="#7C9AA9" stroke-width="1.5"/>',
                    f'<rect x="230" y="{y}" width="430" height="38" rx="4" fill="#DFEFE6"/>',
                    f'<text x="248" y="{y+25}">{html.escape(branch["label"])}</text>'])
    svg.append('</g></svg>')
    out=ch/'figures';(out/'overview.svg').write_text('\n'.join(svg))
    cmd(['inkscape',str(out/'overview.svg'),'--export-text-to-path','--export-type=pdf','--export-filename='+str(out/'overview.pdf')])
    cmd(['inkscape',str(out/'overview.svg'),'--export-type=png','--export-dpi=180','--export-filename='+str(out/'overview.png')])

def prepare(ch):
    for p in COMMON.iterdir():
        dest=ch/p.name
        if not dest.exists():dest.symlink_to(Path('../../common')/p.name,target_is_directory=p.is_dir())
    (ch/'sources').mkdir(exist_ok=True); (ch/'build').mkdir(exist_ok=True)
    for name in ['map.json','sidebars.json']:
        if (ch/name).exists():shutil.copy2(ch/name,ch/'sources'/name)
    jwrite(ch/'sources/layout.json',{'template_version':'1.1','print_mode':'simplex','document_class':'sidenotes-simplex','sidebar':'fixed-right','sidebar_policy':'1–3, matched to actual source anchors and placed after measuring the page','source':'project sidenotes-simplex v1.1; full course notes edition'})
    maps=draw_map(ch)
    draw_overview(ch)
    orig=(ch/('content.md' if (ch/'content.md').exists() else 'notes.md')).read_text()
    # Keep the editable Markdown and the TeX tree sourced from the exact same AST.
    doc=json.loads(cmd(['pandoc','-f','markdown+fenced_divs+raw_tex+tex_math_dollars+tex_math_single_backslash','-t','json'],data=orig))
    anchor_order=[]
    wide_depth=0
    def walk(x):
        nonlocal wide_depth
        if isinstance(x,list):
            res=[]
            for item in x:
                v=walk(item)
                res.extend(v if isinstance(v,Splice) else [v])
            return res
        if not isinstance(x,dict):return x
        t=x.get('t');c=x.get('c')
        if t=='Header':
            level,attr,inlines=c
            if attr[0]:anchor_order.append(attr[0])
            x['c']=[level,attr,walk(inlines)]
            if level==1:
                # Chapter names stay complete in the metadata; opening title uses the textbook name.
                m=json.loads((ch/'map.json').read_text());x['c'][2]=[{'t':'Str','c':m['title']}]
                add=[{'t':'RawBlock','c':['latex',r'\par\medskip\noindent\textbf{章节脉络}\par\smallskip'+'\n'+r'\begin{wideblock}\centering\includegraphics[width=\linewidth,height=92mm,keepaspectratio]{figures/overview.pdf}\end{wideblock}\par\medskip']}]
                return Splice([x]+add)
            return x
        if t=='Div':
            attr,blocks=c; env=next((v for v in attr[1] if v in BOXES),None)
            if env:
                if env=='wideblock' and wide_depth:
                    return Splice(walk(blocks))
                title=dict(attr[2]).get('title','')
                keep='keep' in attr[1] and env not in {'wideblock','solution','proof'}
                begin=(r'{\tcbset{SNbase/.append style={breakable=false}}' if keep else '')+r'\begin{'+env+'}'+('['+esc(title)+']' if title and env not in {'wideblock'} else '')
                if env=='wideblock':wide_depth+=1
                transformed=walk(blocks)
                if env=='wideblock':wide_depth-=1
                return Splice([{'t':'RawBlock','c':['latex',begin]}]+transformed+[{'t':'RawBlock','c':['latex',r'\end{'+env+'}'+('}' if keep else '')]}])
        if t=='Table':
            # Keep comparison dimensions, repeat the actual header, and permit page breaks
            # between chunks instead of placing a whole multi-page table in a minipage.
            bodies=c[4]
            if len(bodies)==1 and len(bodies[0][3])>7:
                import copy
                rows=bodies[0][3]; result=[]
                for start in range(0,len(rows),7):
                    part=copy.deepcopy(x);part['c'][4][0][3]=rows[start:start+7]
                    result.append(walk(part))
                return Splice(result)
            transformed={'t':'Table','c':walk(c)}
            cell_doc={'pandoc-api-version':doc['pandoc-api-version'],'meta':{},'blocks':[transformed]}
            table=cmd(['pandoc','-f','json','-t','latex','--wrap=none','--no-highlight'],data=json.dumps(cell_doc,ensure_ascii=False))
            body=table[table.index('\\toprule'):]
            body=re.sub(r'\\endfirsthead.*?\\endhead','',body,flags=re.S)
            body=body.replace('\\endhead','')
            body=re.sub(r'\\bottomrule\\noalign\{\}\s*\\endlastfoot','',body)
            body=body.replace('\\endlastfoot','')
            body=body.replace('\\end{longtable}',r'\bottomrule\end{tabularx}')
            cols=len(c[2])
            table=r'\par\medskip\noindent\begin{minipage}{\linewidth}\fontsize{9.3}{12}\selectfont\begin{tabularx}{\linewidth}{@{}'+'Y'*cols+r'@{}}'+'\n'+body+r'\end{minipage}\par\medskip'
            if cols>=4 and wide_depth==0:table=r'\begin{wideblock}'+table+r'\end{wideblock}'
            return {'t':'RawBlock','c':['latex',table]}
        if t=='CodeBlock':
            attr,body=c; lang='C++' if any(v in ('cpp','c++') for v in attr[1]) else ('C' if 'c' in attr[1] else '')
            critical=[str(i) for i,line in enumerate(body.splitlines(),1) if re.search(r'\b(if|while|return|P\(|V\()',line)][:3]
            code=(r'\BlueLines{'+','.join(critical)+'}\n' if critical else '')+r'\begin{codeblock}'+('[language='+lang+']' if lang else '[language={}]')+'\n'+body+'\n'+r'\end{codeblock}'
            if len(body.splitlines())<=35:
                code=r'\par\medskip\noindent\begin{minipage}{\linewidth}'+'\n'+code+'\n'+r'\end{minipage}\par\medskip'
            return {'t':'RawBlock','c':['latex',code]}
        if t=='Code':
            # Inline programs must wrap in the narrower main column.
            body=esc(c[1])
            body=re.sub(r'([;=+*/(),<>:.\[\]])',lambda z:z[1]+r'\allowbreak{}',body)
            return {'t':'RawInline','c':['latex',r'\texttt{'+body+'}']}
        if t=='Str' and any(v in c for v in ['⋯','→','←','⇄','↔','≤','≥','≠','−','×','∈','⊕','α','β','τ','λ','Ⅰ','Ⅱ','Ⅲ','Ⅳ']):
            symbols={'⋯':r'\cdots','→':r'\to','←':r'\leftarrow','⇄':r'\rightleftarrows','↔':r'\leftrightarrow','≤':r'\le','≥':r'\ge','≠':r'\ne','−':'-','×':r'\times','∈':r'\in','⊕':r'\oplus','α':r'\alpha','β':r'\beta','τ':r'\tau','λ':r'\lambda','Ⅰ':r'\mathrm{I}','Ⅱ':r'\mathrm{II}','Ⅲ':r'\mathrm{III}','Ⅳ':r'\mathrm{IV}'}
            return {'t':'RawInline','c':['latex',''.join(r'\ensuremath{'+symbols[z]+'}' if z in symbols else esc(z) for z in c)]}
        if t=='Para' and len(c)==1 and c[0].get('t')=='Image':
            return Splice([{'t':'RawBlock','c':['latex',r'\begin{wideblock}']},{'t':'Para','c':walk(c)},{'t':'RawBlock','c':['latex',r'\end{wideblock}']}])
        if t=='Image':
            attr,alt,target=c;url,title=target
            if not url.startswith(('http:','https:','data:')):
                name=Path(url).name;stem=Path(name).stem
                src=next((p for p in [ch/'figures'/(stem+'.pdf'),ch/'figures'/name,FIGURES/(stem+'.pdf'),FIGURES/name,ch/url] if p.exists()),None)
                if src:
                    dest=ch/'figures'/src.name
                    if not dest.exists():shutil.copy2(src,dest)
                    # Save editable originals and PNG companions alongside the vector asset.
                    for ext in ['.svg','.png']:
                        sibling=FIGURES/(stem+ext)
                        if sibling.exists() and not (ch/'figures'/sibling.name).exists():shutil.copy2(sibling,ch/'figures'/sibling.name)
                    x['c'][2]=['figures/'+src.name,title]
                    x['c'][0][2].append(['width','100%'])
            return x
        if 'c' in x:x['c']=walk(c)
        return x
    doc['blocks']=walk(doc['blocks'])
    jwrite(ch/'sources/content_ast.json',doc)
    latex=cmd(['pandoc','-f','json','-t','latex','--top-level-division=chapter','--number-sections','--wrap=none','--no-highlight'],data=json.dumps(doc,ensure_ascii=False))
    latex=latex.replace('\\columnwidth','\\linewidth')
    for n,char in enumerate('①②③④⑤⑥⑦⑧⑨⑩',1):
        latex=latex.replace(char,'{\\SNsymbolfont '+char+'}')
    # Images are native fixed blocks, so they can appear inside a case box.
    latex=re.sub(r'\\begin\{figure\}(?:\[[^\]]*\])?',r'\\par\\medskip\\noindent\\begin{minipage}{\\linewidth}',latex)
    latex=latex.replace('\\end{figure}',r'\end{minipage}\par\medskip')
    latex=latex.replace('\\caption{',r'\captionof{figure}{')
    latex=re.sub(r'\\includegraphics\[[^\]]*\](\{figures/(?!(?:map-|overview))[^}]+\})',r'\\includegraphics[width=\\linewidth,height=125mm,keepaspectratio]\1',latex)
    # Pandoc uses \real in proportional table calculations.
    (ch/'chapter.tex').write_text(latex)
    (ch/'sources/anchor_order.json').write_text(json.dumps(anchor_order,ensure_ascii=False))
    m=json.loads((ch/'map.json').read_text()); chapter_number=int(m['id'][2:])-1
    main=r'''\documentclass{sidenotes-simplex}
\usepackage{graphicx,longtable,calc,etoolbox,caption}
\newfontfamily\SNsymbolfont{NotoSerifSC-Regular.otf}[Path=fonts/]
\RenewDocumentEnvironment{wideblock}{}{\begin{adjustwidth}{0mm}{-54mm}\setlength{\hsize}{\linewidth}\setlength{\columnwidth}{\linewidth}}{\end{adjustwidth}}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\newcommand{\pandocbounded}[1]{#1}
\setlength{\LTpre}{3mm}\setlength{\LTpost}{3mm}
\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}
\setlength{\parskip}{2pt plus .5pt}
\setlength{\emergencystretch}{3em}
\newdimen\SNsideheight
\renewcommand{\sectionmark}[1]{\gdef\SNsectiontitle{\thesection\enspace\SNchaptertitle}}
\hypersetup{pdftitle={@@TITLE@@ · 408完整课程笔记},pdfsubject={@@ID@@ · 单面边栏版},pdfauthor={}}
\InputIfFileExists{sidebars.tex}{}{}
\begin{document}
\setcounter{chapter}{@@NUMBER@@}
\input{chapter}
\end{document}
'''.replace('@@TITLE@@',esc(m['title'])).replace('@@ID@@',m['id']).replace('@@NUMBER@@',str(chapter_number))
    (ch/'main.tex').write_text(main)
    # Export a standalone map PDF without rasterising text or formulas in the notes.
    mapdoc=fitz.open()
    for name in maps:
        d=fitz.open(ch/'figures'/(name+'.pdf'));mapdoc.insert_pdf(d);d.close()
    mapdoc.save(ch/'chapter-map.pdf');mapdoc.close()

def compile_chapter(ch):
    for n in range(2):
        p=subprocess.run(['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=build','main.tex'],cwd=ch,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (ch/'build'/f'pass-{n+1}.txt').write_text(p.stdout)
        if p.returncode:raise RuntimeError(f'{ch.name}: XeLaTeX failed\n'+p.stdout[-5000:])

def mini_tex(m):
    labels=m.get('labels',[])[:4]; edges=m.get('edges',[])
    if not labels:return ''
    # Vertical sequence avoids microscopic type in a 48 mm margin.
    ret=[r'\par\smallskip\begin{tikzpicture}[x=1mm,y=1mm,>=Stealth,node distance=5mm]']
    for i,label in enumerate(labels):
        ret.append(r'\node[draw=SNink!50,fill=SNblue,rounded corners=1mm,text width=34mm,align=center,inner sep=1.2mm,font=\fontsize{7.5}{9}\selectfont] (m'+str(i)+') at (0,'+str(-i*11)+') {'+esc(label)+'};')
    for edge in edges:
        a,b=edge[:2]
        if 0<=a<len(labels) and 0<=b<len(labels):
            ret.append(r'\draw[->,SNink] (m'+str(a)+') '+('edge[bend left=40]' if abs(a-b)>1 else '--')+' (m'+str(b)+');')
    ret.append(r'\end{tikzpicture}')
    if m.get('caption'):ret.append(r'\par{\fontsize{7.5}{9}\selectfont '+esc(m['caption'])+'}')
    return '\n'.join(ret)

def build_sidebars(ch, measured=None):
    doc=fitz.open(ch/'build/main.pdf');sidebars=json.loads((ch/'sidebars.json').read_text())
    aux=(ch/'build/main.aux').read_text()
    pages={k:int(v) for k,v in re.findall(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{(\d+)\}',aux)}
    # Reserve only the actual wide material. Running headers are outside the body.
    out=[];records=[];used=collections.Counter()
    for i,page in enumerate(doc):
        occupied=[]
        for block in page.get_text('dict')['blocks']:
            bb=block['bbox']
            if bb[2]>390 and bb[0]<535 and bb[3]>80 and bb[1]<780:
                occupied.append((max(80,bb[1]-8),min(780,bb[3]+8)))
        for img in page.get_images(full=True):
            for bb in page.get_image_rects(img[0]):
                if bb.x1>390:occupied.append((bb.y0-8,bb.y1+8))
        # SVG-to-PDF outlines are paths. Measure transformed page coordinates.
        for typ,bb in page.get_bboxlog():
            if typ in ('fill-path','stroke-path') and bb[2]>390 and bb[0]<535 and bb[3]>80 and bb[1]<780:
                occupied.append((max(80,bb[1]-6),min(780,bb[3]+6)))
        free=[(135 if i==0 else 95,765)]
        for a,b in occupied:
            nxt=[]
            for l,r in free:
                if b<=l or a>=r:nxt.append((l,r))
                else:
                    if a>l:nxt.append((l,a))
                    if b<r:nxt.append((b,r))
            free=nxt
        free=[x for x in free if x[1]-x[0]>55]
        if not free:raise RuntimeError(f'{ch.name} page {i+1}: no room for a useful sidebar')
        # Stay within the latest started section. Repetition can only break a
        # tie within that section; it must not pull a later topic onto this page.
        candidates=[(j,s) for j,s in enumerate(sidebars) if s['anchor'] in pages]
        if not candidates:
            raise RuntimeError(f'{ch.name}: no sidebar anchor exists in the built document')
        def rank(item):
            idx,s=item; anchor_page=pages[s['anchor']];current=i+1
            return (0 if anchor_page<=current else 1,
                    -anchor_page if anchor_page<=current else anchor_page,
                    used[idx],0 if s.get('mini') and not used[idx] else 1,idx)
        ranked=sorted(candidates,key=rank)
        placed=[]
        for idx,s in ranked:
            body=mdtex(s['body']); mini=mini_tex(s.get('mini',{}))
            count=len(re.sub(r'\$.*?\$','xxxxxxxx',s['body']))
            lines=math.ceil(count/15.5)
            h=25+lines*10.7+(len(s.get('mini',{}).get('labels',[]))*31+24 if mini else 0)
            h=max(h,(measured or {}).get((i+1,idx),0)+3)
            slot=next(((l,r) for l,r in free if r-l>h+8),None)
            if not slot:continue
            y=slot[0]
            payload=r'\textcolor{SNink}{\textbf{'+esc(s['kind'])+r' · '+esc(s['title'])+r'}}\par\vspace{1.5mm}'+body+mini
            out.append(r'\expandafter\gdef\csname SNside'+str(i+1)+r'\endcsname{'+r'\node[anchor=north west,inner sep=0pt,text width=48mm,font=\SideFont,align=left] (SNsidebox) at ([xshift=138mm,yshift=-'+f'{y:.2f}'+r'pt]current page.north west) {'+payload+r'};'+r'\pgfextracty{\SNsideheight}{\pgfpointdiff{\pgfpointanchor{SNsidebox}{south}}{\pgfpointanchor{SNsidebox}{north}}}'+r'\typeout{SNHEIGHT:'+str(i+1)+':'+str(idx)+r':\the\SNsideheight}}')
            placed.append({'index':idx,'anchor':s['anchor'],'kind':s['kind'],'title':s['title'],'y':y,'estimated_height':h,'mini':bool(mini)})
            used[idx]+=1
            # One substantive sidebar per page; add a second only where both are local and brief.
            break
        if not placed:raise RuntimeError(f'{ch.name} page {i+1}: no sidebar fits {free}')
        records.append({'page':i+1,'sidebars':placed,'occupied_margin_intervals':occupied})
    out.append(r'\AddToShipoutPictureFG{\begin{tikzpicture}[remember picture,overlay]\ifcsname SNside\thepage\endcsname\csname SNside\thepage\endcsname\fi\end{tikzpicture}}')
    (ch/'sidebars.tex').write_text('\n'.join(out));jwrite(ch/'sources/sidebar-placement.json',records)

def measured_sidebar_heights(ch):
    log=(ch/'build/main.log').read_text(errors='replace')
    return {(int(pg),int(idx)):float(height) for pg,idx,height in
            re.findall(r'SNHEIGHT:(\d+):(\d+):([\d.]+)pt',log)}

def sidebar_collisions(ch, measured):
    problems=[]
    records=json.loads((ch/'sources/sidebar-placement.json').read_text())
    for record in records:
        for item in record['sidebars']:
            key=(record['page'],item['index'])
            if key not in measured:
                problems.append({'page':record['page'],'reason':'missing measured sidebar height'})
                continue
            top=item['y'];bottom=top+measured[key]
            item['measured_height']=measured[key]
            if bottom>765:
                problems.append({'page':record['page'],'reason':'sidebar below safe bottom'})
            for start,end in record['occupied_margin_intervals']:
                if min(bottom,end)-max(top,start)>1:
                    problems.append({'page':record['page'],'reason':'sidebar overlaps wide content'})
                    break
    jwrite(ch/'sources/sidebar-placement.json',records)
    jwrite(ch/'sources/sidebar-measurement.json',{'method':'actual TikZ node heights emitted by XeLaTeX',
          'measurements':[{'page':p,'index':idx,'height_pt':height} for (p,idx),height in measured.items()],
          'collisions':problems})
    return problems

def qa(ch, render=True):
    d=fitz.open(ch/'build/main.pdf');log=(ch/'build/main.log').read_text(errors='replace')
    warnings=[]
    for issue in ['Missing character:','Overfull \\hbox','Overfull \\vbox','undefined references','Label(s) may have changed']:
        if issue in log:warnings.append(issue)
    placements=json.loads((ch/'sources/sidebar-placement.json').read_text())
    if len(placements)!=len(d):warnings.append('Pagination changed after sidebar insertion')
    for i,p in enumerate(d):
        if abs(p.rect.width-595.276)>1 or abs(p.rect.height-841.89)>1:warnings.append(f'page {i+1}: not A4')
        for f in p.get_fonts():
            if not d.extract_font(f[0])[3]:warnings.append(f'page {i+1}: unembedded font {f[3]}')
        for w in p.get_text('words'):
            if min(w[0],w[1])<-1 or w[2]>596 or w[3]>843:warnings.append(f'page {i+1}: out of page text {w[4]}')
        if not any(w[0]>388 and w[1]>80 for w in p.get_text('words')):warnings.append(f'page {i+1}: no sidebar text')
    shutil.copy2(ch/'build/main.pdf',ch/'notes.pdf')
    jwrite(ch/'sources/qa.json',{'id':ch.name,'pages':len(d),'print_mode':'simplex','sidebar_count_per_page':[len(v['sidebars']) for v in placements],'all_fonts_embedded':not any('unembedded' in w for w in warnings),'warnings':sorted(set(warnings)),'human_visual_review':'pending'})
    if render:
        previews=ROOT/'previews'/ch.name
        if previews.exists():shutil.rmtree(previews)
        previews.mkdir(parents=True,exist_ok=True)
        thumbs=[]
        for i,p in enumerate(d):
            pix=p.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False);pix.save(previews/f'page-{i+1:03}.png')
            im=Image.open(previews/f'page-{i+1:03}.png');im.thumbnail((298,421))
            tile=Image.new('RGB',(320,450),'#EEEEEE');tile.paste(im,((320-im.width)//2,5));ImageDraw.Draw(tile).text((12,430),f'{ch.name} / {i+1}',fill='#222222');thumbs.append(tile)
        for start in range(0,len(thumbs),9):
            group=thumbs[start:start+9];sheet=Image.new('RGB',(960,450*math.ceil(len(group)/3)),'#D8D8D8')
            for j,tile in enumerate(group):sheet.paste(tile,((j%3)*320,(j//3)*450))
            sheet.save(previews/f'contact-{start//9+1:02}.png')
    export_markdown(ch)
    print(json.dumps({'id':ch.name,'pages':len(d),'warnings':sorted(set(warnings))},ensure_ascii=False),flush=True)
    return warnings

def export_markdown(ch):
    """A readable view with the exact printed maps and side notes; content.md is editable."""
    source=ch/'content.md'
    if not source.exists():shutil.copy2(ch/'notes.md',source)
    text=source.read_text()
    text=re.sub(r'(!\[[^\]]*\]\()([^/\s)]+\.(?:png|svg|pdf))',r'\1figures/\2',text)
    match=re.search(r'^# .+$',text,re.M)
    pictures=[]
    pictures.append('![章节脉络](figures/overview.png)\n\n[可编辑SVG](figures/overview.svg) · [完整知识导图](chapter-map.pdf)')
    if match:text=text[:match.end()]+'\n\n'+'\n\n'.join(pictures)+text[match.end():]
    sidebars=json.loads((ch/'sidebars.json').read_text())
    placed=json.loads((ch/'sources/sidebar-placement.json').read_text())
    selected=list(dict.fromkeys(v['index'] for pg in placed for v in pg['sidebars']))
    by_anchor=collections.defaultdict(list)
    for idx in selected:
        item=sidebars[idx]
        lines=[f'> **{item["kind"]} · {item["title"]}**','>', '> '+item['body']]
        mini=item.get('mini')
        if mini:
            labels=mini.get('labels',[])[:4];height=90*len(labels)+35
            svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{height}" viewBox="0 0 400 {height}">',
                 '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#466C82"/></marker></defs>',
                 '<rect width="100%" height="100%" fill="white"/>']
            for n,label in enumerate(labels):
                y=30+n*90
                svg += [f'<rect x="55" y="{y}" width="290" height="44" rx="8" fill="#DDEFF5" stroke="#7C9AA9"/>',f'<text x="200" y="{y+28}" text-anchor="middle" font-family="Noto Sans CJK SC,sans-serif" font-size="19">{html.escape(label)}</text>']
            for a,b in mini.get('edges',[]):
                if not (0<=a<len(labels) and 0<=b<len(labels)):continue
                ya=52+a*90;yb=52+b*90
                if b==a+1:path=f'M200,{ya+22} V{yb-22}'
                else:path=f'M345,{ya} C390,{ya} 390,{yb} 345,{yb}'
                svg.append(f'<path d="{path}" fill="none" stroke="#466C82" stroke-width="2" marker-end="url(#a)"/>')
            svg.append('</svg>');stem=f'mini-{idx+1:02}'
            (ch/'figures'/(stem+'.svg')).write_text('\n'.join(svg))
            cmd(['inkscape',str(ch/'figures'/(stem+'.svg')),'--export-type=png','--export-dpi=160','--export-filename='+str(ch/'figures'/(stem+'.png'))])
            lines += ['>',f'> ![最小反例微图](figures/{stem}.png)']
            if mini.get('caption'):lines+=['>','> '+mini['caption']]
        by_anchor[item['anchor']].append('\n'.join(lines))
    for anchor,cards in by_anchor.items():
        pattern=r'(^#{2,4} [^\n]*\{#'+re.escape(anchor)+r'\}[^\n]*$)'
        addition='\n\n'+'\n\n'.join(cards)
        text=re.sub(pattern,lambda m:m[0]+addition,text,count=1,flags=re.M)
    # Export a regular Markdown reading edition. Semantic Pandoc fences remain
    # in content.md for editing, while ordinary readers get native headings.
    labels={'definition':'定义','theorem':'定理','proof':'推导','methodbox':'方法',
            'example':'例题','pitfall':'辨析','takeaway':'结论','recallcard':'主动回忆',
            'solution':'解答','proposition':'命题','corollary':'推论'}
    output=[];in_code=False
    for line in text.splitlines():
        if line.startswith('```'):
            in_code=not in_code
        if not in_code:
            if re.fullmatch(r'\s*\\Needspace\{[^}]+\}\s*',line):
                continue
            div=re.fullmatch(r'\s*:::\s*(?:\{(.*?)\})?\s*',line)
            if div:
                attrs=div[1] or ''
                env=next((key for key in labels if '.'+key in attrs),None)
                title=re.search(r'title="([^"]*)"',attrs)
                if env:
                    output.append('**'+labels[env]+(' · '+title[1] if title else '')+'**')
                continue
            header=re.match(r'^(#{1,6} .+?)\s*\{#([^}\s]+)\}\s*$',line)
            if header:
                output.extend([f'<a id="{html.escape(header[2])}"></a>',header[1]])
                continue
            im=re.match(r'^(!\[[^\]]*\]\([^)]*\))\s*\{([^}]*)\}\s*$',line)
            if im:
                anchor=re.search(r'#([^\s]+)',im[2])
                if anchor:output.append(f'<a id="{html.escape(anchor[1])}"></a>')
                output.append(im[1]);continue
        output.append(line)
    text='\n'.join(output)+'\n'
    (ch/'notes.md').write_text(text)
    jwrite(ch/'sources/content-sync.json',{'canonical_markdown':'content.md','readable_markdown':'notes.md','latex':'chapter.tex','printed_map_panels':len(pictures),'printed_unique_sidebars':selected,'canonical_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'markdown_sha256':hashlib.sha256((ch/'notes.md').read_bytes()).hexdigest(),'latex_sha256':hashlib.sha256((ch/'chapter.tex').read_bytes()).hexdigest(),'note':'notes.md inserts the already printed map panels and unique printed sidebars, with valid relative image links; body/knowledge IDs derive from content.md.'})

def build_input_fingerprint(ch):
    paths=[ch/'content.md', ch/'map.json', ch/'sidebars.json', COMMON/'sidenotes.cls', COMMON/'sidenotes-simplex.cls']
    paths += [p for p in (ch/'figures').iterdir()
              if p.is_file() and p.suffix.lower() in {'.png','.svg','.pdf'}
              and not p.name.startswith(('map-', 'overview.', 'mini-'))]
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()}

def build(ch, render=True):
    inputs=build_input_fingerprint(ch)
    prepare(ch)
    (ch/'sidebars.tex').write_text('')
    compile_chapter(ch)
    build_sidebars(ch)
    compile_chapter(ch)
    measured=measured_sidebar_heights(ch)
    for attempt in range(3):
        problems=sidebar_collisions(ch,measured)
        if not problems:break
        (ch/'sidebars.tex').write_text('')
        compile_chapter(ch)
        build_sidebars(ch,measured)
        compile_chapter(ch)
        measured.update(measured_sidebar_heights(ch))
    if sidebar_collisions(ch,measured):
        raise RuntimeError(f'{ch.name}: measured sidebar collision remains')
    if inputs != build_input_fingerprint(ch):
        raise RuntimeError(f'{ch.name}: source or figure changed during compilation; rerun after edits finish')
    warnings=qa(ch,render)
    if inputs != build_input_fingerprint(ch):
        raise RuntimeError(f'{ch.name}: source or figure changed during export; rerun after edits finish')
    jwrite(ch/'sources/build-inputs.json',inputs)
    return warnings

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('ids',nargs='+');ap.add_argument('--no-render',action='store_true');a=ap.parse_args()
    for ident in a.ids:
        try:build(ROOT/'chapters'/ident,not a.no_render)
        except Exception as e:print(f'ERROR {ident}: {e}',flush=True);raise
