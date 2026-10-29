#!/usr/bin/env python3
"""Build an indexed answer book from verified source crops or native solutions."""
from pathlib import Path
import re,json,shutil
import fitz
from build_notes import ROOT, COMMON, cmd, esc, mdtex, collect_assets, read, jwrite, sha, tex_symbols
SUBJECTS={'DS':'数据结构','CO':'计算机组成原理','OS':'操作系统','CN':'计算机网络'}

def label_pages(path):
 return {k:int(v) for k,v in re.findall(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{(\d+)\}',path.read_text())}

def native_latex(e):
 ch=ROOT/'chapters'/e['chapter'];source=e['solution'];collect_assets(ch,source)
 source=re.sub(r'(!\[[^\]]*\]\()([^\s)]+)',lambda m:m[1]+str(ch/'figures'/Path(m[2]).name),source)
 tex=mdtex(source).replace(r'\begin{verbatim}',r'\begin{codeblock}[language={}]').replace(r'\end{verbatim}',r'\end{codeblock}')
 def keep_short_code(match):
  lines=len(match[1].strip().splitlines())
  reserve=(r'\Needspace{'+str(lines+4)+r'\baselineskip}') if lines<=12 else ''
  return reserve+match[0]
 tex=re.sub(r'\\begin\{codeblock\}\[language=\{\}\]([\s\S]*?)\\end\{codeblock\}',keep_short_code,tex)
 tex=re.sub(r'\\begin\{figure\}(?:\[[^]]*\])?',r'\\par\\medskip\\begin{center}',tex)
 tex=tex.replace(r'\end{figure}',r'\end{center}\par\medskip').replace(r'\caption{',r'\captionof{figure}{')
 symbols={'→':r'\to','←':r'\leftarrow','≤':r'\le','≥':r'\ge','≠':r'\ne','×':r'\times','⋯':r'\cdots','−':'-','α':r'\alpha','β':r'\beta','τ':r'\tau','λ':r'\lambda','⊕':r'\oplus'}
 for c,v in symbols.items():tex=tex.replace(c,r'\ensuremath{'+v+'}')
 return tex

def quick_answer(e):
 text=e['answer'].strip()
 # A single-choice item needs only its choice letter in the lookup table.
 if len(re.findall(r'(?:^|\s)A[.．、]',e['question']))==1:
  letters=re.findall(r'(?<![A-Za-z])([A-D])(?![A-Za-z])',text)
  if len(letters)==1 and text.startswith(letters[0]):return letters[0]
 return text

def main():
 examples=read(ROOT/'sources/example_index.json')['examples'];manifest=read(ROOT/'manifest.json')
 starts={r['id']:r['combined_start_page'] for r in manifest['chapters']}
 for ch in {e['chapter'] for e in examples}:
  pages=label_pages(ROOT/'chapters'/ch/'build/main.aux')
  for e in examples:
   if e['chapter']==ch:e['note_local_page']=pages[e['id']];e['note_page']=starts[ch]+pages[e['id']]-1
 out=ROOT/'solutions';(out/'build').mkdir(exist_ok=True)
 for p in COMMON.iterdir():
  dest=out/p.name
  if not dest.exists():dest.symlink_to(Path('../common')/p.name,target_is_directory=p.is_dir())
 pre=r'''\documentclass{sidenotes-simplex}
\geometry{left=24mm,right=24mm,top=28mm,bottom=28mm,marginparwidth=0mm,marginparsep=0mm}
\usepackage{graphicx,longtable,caption,calc}
\providecommand{\tightlist}{\setlength{\itemsep}{1pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\newcommand{\pandocbounded}[1]{#1}
\setkeys{Gin}{width=\linewidth,height=165mm,keepaspectratio}
\setlength{\parindent}{0pt}\setlength{\emergencystretch}{3em}
\setlength{\LTleft}{0pt}\setlength{\LTright}{0pt}
\hypersetup{pdftitle={408强化例题解析},pdfsubject={原解析与答案索引}}
\renewcommand{\sectionmark}[1]{\gdef\SNsectiontitle{\SNchaptertitle}}
\begin{document}
\section*{答案速查}
'''
 parts=[pre];md=['# 408强化例题解析','']
 for subject,name in SUBJECTS.items():
  parts.append(r'\Needspace{6\baselineskip}')
  parts.append(r'\subsection*{'+name+'}')
  parts.append(r'{\fontsize{9.3}{12}\selectfont')
  parts.append(r'\begin{longtable}{@{}p{18mm}p{87mm}p{20mm}p{20mm}@{}}\toprule 题号 & 答案 & 正文页 & 解析页 \\ \midrule\endfirsthead\toprule 题号 & 答案 & 正文页 & 解析页 \\ \midrule\endhead\bottomrule\endfoot')
  for e in examples:
   if e['subject']!=subject:continue
   answer=mdtex(quick_answer(e)).strip()
   parts.append(esc(e['number'])+' & '+answer+' & '+str(e['note_page'])+r' & \hyperref[a:'+e['id']+r']{\pageref*{a:'+e['id']+r'}} \\')
  parts.append(r'\end{longtable}}')
 for subject,name in SUBJECTS.items():
  parts.append(r'\chapter{'+name+'}');md+=['# '+name,''];current=None
  for e in examples:
   if e['subject']!=subject:continue
   keep_mm=30
   if e['solution_mode']=='original_screenshot' and e['crops']:
    first=e['crops'][0];w=min(162,(first['bbox'][2]-first['bbox'][0])*25.4/72*1.05);h=min(180,w*(first['bbox'][3]-first['bbox'][1])/(first['bbox'][2]-first['bbox'][0]));keep_mm=max(30,h+16)
   if e['chapter']!=current:
    current=e['chapter'];title=read(ROOT/'chapters'/current/'map.json')['title']
    parts.append(r'\Needspace{'+f'{min(222,keep_mm+18):.2f}'+r'mm}\section*{'+esc(title)+'}');md+=['## '+title,'']
   parts.append(r'\par\medskip\Needspace{'+f'{keep_mm:.2f}'+r'mm}\noindent\phantomsection\label{a:'+e['id']+r'}\textbf{例 '+esc(e['number'])+r'}\quad '+mdtex(e['answer'])+r'\par\smallskip')
   md+=['<a id="a-'+e['id']+'"></a>','### [例 '+e['number']+'](../books/'+SUBJECTS[e['subject']]+'_强化笔记.md#'+e['id']+')','',e['answer'],'']
   if e['solution_mode']=='original_screenshot':
    for crop in e['crops']:
     width_mm=min(162,(crop['bbox'][2]-crop['bbox'][0])*25.4/72*1.05)
     parts.append(r'\par\medskip\noindent\includegraphics[width='+f'{width_mm:.2f}'+r'mm,height=180mm,keepaspectratio]{../'+crop['png']+r'}\par\smallskip')
     md+=['![原解析](../'+crop['png']+')','']
   else:
    parts.append(native_latex(e));solution_md=re.sub(r'(!\[[^\]]*\]\()([^\s)]+)',lambda m:m[1]+'../chapters/'+e['chapter']+'/figures/'+Path(m[2]).name,e['solution']);md+=[solution_md,'']
 parts.append(r'\end{document}')
 (out/'main.tex').write_text(tex_symbols('\n'.join(parts)))
 quick=['## 答案速查','','| 科目 | 题号 | 答案 | 正文页 |','| --- | --- | --- | --- |']
 for e in examples:quick.append('| '+SUBJECTS[e['subject']]+' | ['+e['number']+'](#a-'+e['id']+') | '+quick_answer(e).replace('\n',' ').replace('|',r'\|')+' | '+str(e['note_page'])+' |')
 md[1:1]=['']+quick+['']
 (out/'notes.md').write_text('\n'.join(md))
 for _ in range(3):cmd(['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex'],cwd=out)
 shutil.copy2(out/'build/main.pdf',ROOT/'books/408强化例题解析.pdf')
 pages=label_pages(out/'build/main.aux')
 for e in examples:e['solution_page']=pages['a:'+e['id']]
 jwrite(ROOT/'sources/navigation.json',{'examples':[{'id':e['id'],'subject':e['subject'],'chapter':e['chapter'],'number':e['number'],'answer':e['answer'],'note_page':e['note_page'],'note_local_page':e['note_local_page'],'solution_page':e['solution_page'],'solution_mode':e['solution_mode']} for e in examples]})
 with fitz.open(ROOT/'books/408强化例题解析.pdf') as d:print('solutions pages',len(d))

if __name__=='__main__':main()
