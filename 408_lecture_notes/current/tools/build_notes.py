#!/usr/bin/env python3
"""Build reinforcement notes from one editable Markdown source and example registry."""
from pathlib import Path
import argparse, collections, hashlib, json, math, re, shutil, subprocess
import fitz

ROOT=Path(__file__).resolve().parents[1]
COMMON=ROOT/'common'
BASE=ROOT.parent/'baselines/course-notes-26'
FORMAT='markdown+fenced_divs+raw_tex+tex_math_dollars+tex_math_single_backslash'

def cmd(args,cwd=None,data=None):
 p=subprocess.run(args,cwd=cwd,input=data,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if p.returncode: raise RuntimeError(p.stdout[-7000:])
 return p.stdout

def jwrite(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def esc(s):return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(s))
def mdtex(s):return cmd(['pandoc','-f',FORMAT,'-t','latex','--wrap=none','--no-highlight'],data=s).replace('\\tightlist','')

def expand(ch):
 text=(ch/'content.md').read_text(); examples=read(ch/'examples.json')
 text=re.sub(r'^# [^\n]+', '# '+read(ch/'map.json')['title']+' {#'+ch.name+'}',text,count=1,flags=re.M)
 byid={e['id']:e for e in examples}
 def replace(m):
  e=byid[m[1]]
  question=re.sub(r"^(?:【(?:\d{4}|配套例题)】|〖[^〗]+〗|配套例题[：:])\s*", "", e["question"].strip())
  return f"### 例 {e['number']} {{#{e['id']}}}\n\n{question}"
 text=re.sub(r'\{\{example:([^}]+)\}\}',replace,text)
 if '{{example:' in text:raise ValueError('Unexpanded example')
 return text

def collect_assets(ch,text):
 assets=[]
 for url in re.findall(r'!\[[^\]]*\]\(([^)\s]+)\)',text):
  if re.match(r'https?:|data:',url):raise ValueError('Nonlocal image')
  name=Path(url).name;stem=Path(name).stem
  src=next((p for p in [ch/'figures'/name,BASE/'chapters'/ch.name/'figures'/name,BASE/'figures'/name] if p.exists()),None)
  if src is None:raise FileNotFoundError(f'{ch.name}: {url}')
  for ext in {src.suffix,'.pdf','.png','.svg'}:
   sibling=src.with_suffix(ext);dest=ch/'figures'/sibling.name
   if sibling.exists() and not dest.exists():shutil.copy2(sibling,dest)
  assets.append({'reference':url,'sha256':sha(ch/'figures'/name)})
 jwrite(ch/'sources/assets.json',assets)

def inline_text(obj):
 if isinstance(obj,list):return ''.join(inline_text(v) for v in obj)
 if not isinstance(obj,dict):return ''
 t=obj.get('t');c=obj.get('c')
 if t in ('Str','Math','Code'):return c if isinstance(c,str) else c[1]
 if t in ('Space','SoftBreak','LineBreak'):return ' '
 return inline_text(c)

def visual_units(s):
 s=re.sub(r'\\[A-Za-z]+','x',s)
 return sum(1 if ord(c)>255 else .52 for c in s)

def table_tex(obj,api):
 c=obj['c'];cols=len(c[2]);head=c[3][1];rows=[r for b in c[4] for r in b[2]+b[3]];foot=c[5][1]
 allrows=head+rows+foot
 measures=[[] for _ in range(cols)]
 for row in allrows:
  for i,cell in enumerate(row[1]):
   if i<cols: measures[i].append(visual_units(inline_text(cell[4])))
 preferred=[max(4,min(30,max(v,default=4))) for v in measures]
 # A long-text column receives more width; short identifiers keep a narrow measure.
 weights=[max(3.5,math.sqrt(v)*2.2) for v in preferred]
 wide=sum(preferred)>38 or (cols>=4 and sum(preferred)>28)
 usable=162 if wide else 108
 total=sum(weights);fractions=[w/total for w in weights]
 spec='@{}'+''.join(r'>{\raggedright\arraybackslash}p{\dimexpr'+f'{f:.5f}'+r'\linewidth-2\tabcolsep\relax}' for f in fractions)+'@{}'
 def celltex(cell):
  doc={'pandoc-api-version':api,'meta':{},'blocks':cell[4]}
  return cmd(['pandoc','-f','json','-t','latex','--wrap=none'],data=json.dumps(doc,ensure_ascii=False)).strip().replace('\\tightlist','')
 def rowtex(row):return ' & '.join(celltex(cell) for cell in row[1])+r' \\'+'\n'
 ret=[r'\par\smallskip']
 if wide:ret.append(r'\begin{wideblock}')
 ret.append(r'{\fontsize{9.3}{12}\selectfont\setlength{\tabcolsep}{2.5pt}\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}')
 ret.append(r'\begin{longtable}{'+spec+'}\n'+r'\toprule')
 ret.extend(rowtex(r) for r in head)
 ret.append(r'\midrule\endfirsthead\toprule')
 ret.extend(rowtex(r) for r in head)
 ret.append(r'\midrule\endhead\bottomrule\endfoot')
 ret.extend(rowtex(r) for r in rows+foot)
 ret.append(r'\end{longtable}}')
 if wide:ret.append(r'\end{wideblock}')
 ret.append(r'\par\smallskip')
 return '\n'.join(ret)

def tex_symbols(text):
 for char,roman in zip('ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ',['I','II','III','IV','V','VI','VII','VIII','IX','X']):text=text.replace(char,r'\ensuremath{\mathrm{'+roman+'}}')
 for char in '①②③④⑤⑥⑦⑧⑨⑩':text=text.replace(char,r'{\SNsymbolfont '+char+'}')
 return text

def prepare(ch):
 (ch/'build').mkdir(exist_ok=True)
 for p in COMMON.iterdir():
  dest=ch/p.name
  if not dest.exists():dest.symlink_to(Path('../../common')/p.name,target_is_directory=p.is_dir())
 text=expand(ch);collect_assets(ch,text)
 doc=json.loads(cmd(['pandoc','-f',FORMAT,'-t','json'],data=text));api=doc['pandoc-api-version'];titles={}
 def walk(x):
  if isinstance(x,list):return [walk(v) for v in x]
  if not isinstance(x,dict):return x
  t=x.get('t');c=x.get('c')
  if t=='Header':
   level,attr,inlines=c;title=inline_text(inlines);titles[attr[0]]=title
   if re.fullmatch(r'[A-Z]{2}\d{2}-E\d+',attr[0]):
    return {'t':'RawBlock','c':['latex',r'\par\medskip\Needspace{4\baselineskip}\noindent\hypertarget{'+attr[0]+r'}{}\label{'+attr[0]+r'}\textbf{'+esc(title)+r'}\par\nobreak\smallskip']}
  if t=='Table':return {'t':'RawBlock','c':['latex',table_tex(x,api)]}
  if t=='Code':
   body=re.sub(r'([;=+*/(),<>:.\[\]])',lambda m:esc(m[1])+r'\allowbreak{}',c[1])
   body=esc(c[1])
   body=re.sub(r'([;=+*/(),<>:.\[\]])',lambda m:m[1]+r'\allowbreak{}',body)
   return {'t':'RawInline','c':['latex',r'\texttt{'+body+'}']}
  if t=='Str' and any(z in c for z in '→←≤≥≠×⋯−αβτλ⊕∈'):
   symbols={'→':r'\to','←':r'\leftarrow','≤':r'\le','≥':r'\ge','≠':r'\ne','×':r'\times','⋯':r'\cdots','−':'-','α':r'\alpha','β':r'\beta','τ':r'\tau','λ':r'\lambda','⊕':r'\oplus','∈':r'\in'}
   return {'t':'RawInline','c':['latex',''.join(r'\ensuremath{'+symbols[z]+'}' if z in symbols else esc(z) for z in c)]}
  if t=='Image':
   attr,alt,target=c;name=Path(target[0]).name;pdf=ch/'figures'/Path(name).with_suffix('.pdf')
   path='figures/'+(pdf.name if pdf.exists() else name)
   caption=inline_text(alt)
   return {'t':'RawInline','c':['latex',r'\includegraphics[width=\linewidth,height=108mm,keepaspectratio]{'+path+'}']}
  if t=='Para' and len(c)==1 and c[0].get('t')=='Image':
   img=walk(c[0])['c'][1]
   name=Path(c[0]['c'][2][0]).name;asset=ch/'figures'/name
   if asset.suffix.lower()=='.pdf':
    with fitz.open(asset) as f:ratio=f[0].rect.width/f[0].rect.height
   else:
    from PIL import Image
    with Image.open(asset) as im:ratio=im.width/im.height
   begin=r'\begin{wideblock}' if ratio>1.6 else ''
   end=r'\end{wideblock}' if ratio>1.6 else ''
   return {'t':'RawBlock','c':['latex',r'\par\medskip'+begin+r'\noindent\begin{minipage}{\linewidth}\centering '+img+r'\end{minipage}'+end+r'\par\medskip']}
  if t=='CodeBlock':
   attr,body=c;lang='C++' if any(s in attr[1] for s in ['cpp','c++']) else ('C' if 'c' in attr[1] else '')
   code=r'\begin{codeblock}[language={'+lang+'}]\n'+body+'\n'+r'\end{codeblock}'
   if len(body.splitlines())<=28:code=r'\par\smallskip\noindent\begin{minipage}{\linewidth}'+'\n'+code+'\n'+r'\end{minipage}\par\smallskip'
   return {'t':'RawBlock','c':['latex',code]}
  if 'c' in x:x['c']=walk(c)
  return x
 doc['blocks']=walk(doc['blocks'])
 latex=cmd(['pandoc','-f','json','-t','latex','--top-level-division=chapter','--wrap=none','--no-highlight'],data=json.dumps(doc,ensure_ascii=False))
 latex=re.sub(r'\\begin\{figure\}(?:\[[^]]*\])?',lambda m:r'\begin{figure}[H]',latex)
 latex=tex_symbols(latex)
 (ch/'chapter.tex').write_text(latex)
 jwrite(ch/'sources/anchor_titles.json',titles)
 meta=read(ch/'map.json');title=meta['title'];num=int(ch.name[2:])-1
 main=r'''\documentclass{sidenotes-simplex}
\usepackage{graphicx,longtable,calc,etoolbox,caption,float}
\RenewDocumentEnvironment{wideblock}{}{\begin{adjustwidth}{0mm}{-54mm}\setlength{\hsize}{\linewidth}\setlength{\columnwidth}{\linewidth}}{\end{adjustwidth}}
\providecommand{\tightlist}{\setlength{\itemsep}{1pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\newcommand{\pandocbounded}[1]{#1}
\newdimen\SNsideheight
\setcounter{secnumdepth}{1}
\setlength{\parindent}{0pt}
\setlength{\emergencystretch}{3em}
\setlength{\LTpre}{2mm}\setlength{\LTpost}{2mm}
\hypersetup{pdftitle={@@TITLE@@ · 强化笔记},pdfsubject={@@ID@@}}
\renewcommand{\sectionmark}[1]{\gdef\SNsectiontitle{\SNchaptertitle}}
\InputIfFileExists{sidebars.tex}{}{}
\begin{document}
\setcounter{chapter}{@@NUMBER@@}
\input{chapter}
\end{document}
'''.replace('@@TITLE@@',esc(title)).replace('@@ID@@',ch.name).replace('@@NUMBER@@',str(num))
 (ch/'main.tex').write_text(main)
 reader=re.sub(r'(!\[[^\]]*\]\()([^/\s)]+\.(?:png|svg|pdf))',r'\1figures/\2',text)
 reader=re.sub(r'^(#{1,6} .+?)\s*\{#([^}\s]+)\}\s*$',lambda m:'<a id="'+m[2]+'"></a>\n'+m[1],reader,flags=re.M)
 reader=re.sub(r'\s*\{#[^}\s]+\}(?=\n|$)','',reader)
 for e in read(ch/'examples.json'):
  reader=reader.replace('### 例 '+e['number']+'\n','### [例 '+e['number']+'](../../solutions/notes.md#a-'+e['id']+')\n')
 (ch/'notes.md').write_text(reader)
 jwrite(ch/'sources/content-sync.json',{'canonical_sha256':sha(ch/'content.md'),'markdown_sha256':sha(ch/'notes.md'),'latex_sha256':sha(ch/'chapter.tex'),'examples_sha256':sha(ch/'examples.json'),'printed_map_panels':0})

def compile_chapter(ch):
 for _ in range(2):cmd(['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex'],cwd=ch)

def build_sidebars(ch,measured=None):
 doc=fitz.open(ch/'build/main.pdf');items=read(ch/'sidebars.json');aux=(ch/'build/main.aux').read_text()
 pages={k:int(v) for k,v in re.findall(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{(\d+)\}',aux)}
 records=[];output=[];used=set()
 for pg,page in enumerate(doc,1):
  occupied=[]
  for typ,bb in page.get_bboxlog():
   if bb[2]>390 and bb[0]<535 and bb[3]>82 and bb[1]<775:occupied.append((max(82,bb[1]-7),min(775,bb[3]+7)))
  free=[(155 if pg==1 else 95,765)]
  for a,b in occupied:
   new=[]
   for l,r in free:
    if b<=l or a>=r:new.append((l,r))
    else:
     if l<a:new.append((l,a))
     if b<r:new.append((b,r))
   free=new
  placed=[]
  for idx,s in enumerate(items):
   if idx in used or pages.get(s['anchor'])!=pg:continue
   body=mdtex(s['body']);title=s.get('title','');height=max(28,17+math.ceil(visual_units(s['body'])/15)*10.7)
   height=max(height,(measured or {}).get((pg,idx),0)+4)
   slot=next(((a,b) for a,b in free if b-a>=height+8),None)
   if slot is None:continue
   y=slot[0];payload=(r'\textbf{'+esc(title)+r'}\par\smallskip ' if title else '')+body
   output.append(r'\expandafter\gdef\csname SNside'+str(pg)+r'\endcsname{\node[anchor=north west,inner sep=0pt,text width=48mm,font=\SideFont,align=left] (SNsidebox) at ([xshift=138mm,yshift=-'+f'{y:.2f}'+r'pt]current page.north west) {'+payload+r'};\pgfextracty{\SNsideheight}{\pgfpointdiff{\pgfpointanchor{SNsidebox}{south}}{\pgfpointanchor{SNsidebox}{north}}}\typeout{SNHEIGHT:'+str(pg)+':'+str(idx)+r':\the\SNsideheight}}')
   placed.append({'index':idx,'anchor':s['anchor'],'y':y,'estimated_height':height});used.add(idx);break
  records.append({'page':pg,'sidebars':placed,'occupied_margin_intervals':occupied})
 output.append(r'\AddToShipoutPictureFG{\begin{tikzpicture}[remember picture,overlay]\ifcsname SNside\thepage\endcsname\csname SNside\thepage\endcsname\fi\end{tikzpicture}}')
 (ch/'sidebars.tex').write_text('\n'.join(output));jwrite(ch/'sources/sidebar-placement.json',records)

def measured_sidebar_heights(ch):
 return {(int(p),int(i)):float(h) for p,i,h in re.findall(r'SNHEIGHT:(\d+):(\d+):([\d.]+)pt',(ch/'build/main.log').read_text(errors='replace'))}

def build_input_fingerprint(ch):
 paths=[Path(__file__).resolve(),ch/'map.json',ch/'content.md',ch/'examples.json',ch/'sidebars.json',COMMON/'sidenotes.cls',COMMON/'sidenotes-simplex.cls']+list((ch/'figures').glob('*'))
 return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}

def build(ch):
 prepare(ch);inputs=build_input_fingerprint(ch);(ch/'sidebars.tex').write_text('');compile_chapter(ch)
 build_sidebars(ch);compile_chapter(ch)
 measured=measured_sidebar_heights(ch)
 build_sidebars(ch,measured);compile_chapter(ch)
 if inputs!=build_input_fingerprint(ch):raise RuntimeError('Source changed during build')
 shutil.copy2(ch/'build/main.pdf',ch/'notes.pdf')
 with fitz.open(ch/'notes.pdf') as pdf:pages=len(pdf)
 jwrite(ch/'sources/build-inputs.json',inputs)
 jwrite(ch/'sources/qa.json',{'id':ch.name,'pages':pages,'visual_review':'pending_after_github_push'})
 print(json.dumps({'id':ch.name,'pages':pages,'visual_review':'pending_after_github_push'}),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('ids',nargs='+');args=ap.parse_args()
 for ident in args.ids:build(ROOT/'chapters'/ident)
