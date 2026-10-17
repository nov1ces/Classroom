#!/usr/bin/env python3
"""Build the editable manuscripts, navigation indexes and four print PDFs.

No source books or network access are required to rebuild the lecture notes.
The source/verification ledgers are maintained separately from typesetting.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = {'DS': ('数据结构', 8), 'CO': ('计算机组成原理', 8),
            'OS': ('操作系统', 7), 'CN': ('计算机网络', 6)}

def run(args, **kw):
    return subprocess.run(args, cwd=ROOT, check=True, **kw)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(sub, partial=False, chapters=None, review=False, review_edition='revision3'):
    title, wanted = SUBJECTS[sub]
    paths = sorted((ROOT / 'manuscript' / sub).glob('[0-9][0-9]_*.md'))
    if chapters:
        paths = [p for p in paths if int(p.name[:2]) in chapters]
    if not paths:
        raise ValueError(f'{sub}: no chapters found')
    nums = [int(p.name[:2]) for p in paths]
    if not partial and nums != list(range(1, wanted + 1)):
        raise ValueError(f'{sub}: expected chapters 1..{wanted}, found {nums}')
    if not re.fullmatch(r'revision[1-9][0-9]*',review_edition):
        raise ValueError('Invalid review edition: ' + review_edition)
    out = ROOT / 'build' / review_edition / sub if review else ROOT / 'build' / sub
    out.mkdir(parents=True, exist_ok=True)
    headings, sources, chunks, anchors = [], [], [], set()
    for path in paths:
        chapter = int(path.name[:2])
        section = 0
        block = False
        lines = []
        original_lines = path.read_text().splitlines()
        for ln, line in enumerate(original_lines, 1):
            if re.match(r'^\s*(```|~~~)', line):
                block = not block
            m = None if block else re.match(r'^(#{1,4})\s+(.+?)\s*$', line)
            if m:
                level, text = len(m[1]), m[2]
                am = re.search(r'\s*\{#([^}\s]+)[^}]*\}\s*$', text)
                anchor = am[1] if am else f'{sub.lower()}-c{chapter:02d}-h{ln}'
                clean = re.sub(r'\s*\{#[^}]+\}\s*$', '', text)
                if anchor in anchors:
                    raise ValueError(f'Duplicate anchor {anchor}: {path}:{ln}')
                anchors.add(anchor)
                if level == 2: section += 1
                if not am: line += f' {{#{anchor}}}'
                headings.append(dict(level=level, title=clean, anchor=anchor,
                    chapter=chapter, section=f'{chapter}.{section}',
                    path=str(path.relative_to(ROOT)), line=ln))
                if re.search(r'(^例\s*[A-Z]*\s*\d|^例题\s*\d)', clean):
                    label = re.search(r'【\d{4}】(?:\s*(?:（改编）|\(改编\)|改编))?|〖[^〗]+〗', clean)
                    if not label:
                        for following in original_lines[ln:ln+5]:
                            label = re.match(r'^\s*(【\d{4}】(?:\s*(?:（改编）|\(改编\)|改编))?|〖[^〗]+〗)', following)
                            if label: break
                            if following.startswith('#'): break
                    if label:
                        headings[-1]['marker'] = label[0].strip()
            lines.append(line)
        if not re.search(r'^# ', '\n'.join(lines), re.M):
            raise ValueError(f'{path}: no chapter heading')
        chunks.append('\n'.join(lines) + '\n')
        sources.append(dict(path=str(path.relative_to(ROOT)), sha256=sha(path),
                            characters=len(path.read_text()), chapter=chapter))
    body = '\n\n'.join(chunks)
    (out / 'body.md').write_text(body)
    # A merged Markdown file has relative, working image links for editing.
    merged = re.sub(r'(!\[[^\]]*\]\()([^\s)]+\.png)',
        lambda m: m[1] + '../figures/' + Path(m[2]).name, body)
    if not partial:
        (ROOT / 'manuscript' / f'{title}_合并稿.md').write_text(merged)
    questions = [h for h in headings if re.search(r'(^例\s*[A-Z]*\s*\d|^例题\s*\d)', h['title'])
                 or (re.search(r'自测',h['title']) and not re.search(r'^自测答案',h['title']))]
    methods = [h for h in headings if h['level'] in (2, 3)
        and h not in questions and not re.search(r'自测|答案|索引|练习|回顾', h['title'])
        and (h['level'] == 2 or re.search(r'如何|怎样|何时|算法|计算|判断|方法|过程|步骤|转换|推导|地址|轨迹|次序', h['title']))]
    indexes = []
    for name, entries in [('题目索引', questions), ('方法索引', methods)]:
        indexes.append('\\clearpage\n\\phantomsection\n\\chapter*{' + name +
            '}\n\\addcontentsline{toc}{chapter}{' + name + '}\n')
        prev = None
        for h in entries:
            if h['chapter'] != prev:
                indexes.append(f"\\par\\medskip\\noindent\\textbf{{第{h['chapter']}章}}\\par\n")
                prev = h['chapter']
            label = h['title']
            if h.get('marker') and h['marker'] not in label:
                label += ' ' + h['marker']
            # Pandoc handles mathematical expressions and code in index titles.
            fragment = subprocess.run(['pandoc', '-f', 'markdown+tex_math_dollars+tex_math_single_backslash', '-t', 'latex'],
                input=label, text=True, capture_output=True, check=True).stdout.strip()
            indexes.append('\\BookIndexEntry{' + h['anchor'] + '}{' + fragment + '}\n')
    (out / 'indexes.tex').write_text(''.join(indexes))
    return title, out, sources, headings, questions, methods

def build(sub, partial=False, passes=3, chapters=None, review=False, review_edition='revision3'):
    title, out, sources, headings, questions, methods = prepare(sub, partial, chapters, review, review_edition)
    missing = []
    for img in re.findall(r'!\[[^\]]*\]\(([^\s)]+\.png)', (out / 'body.md').read_text()):
        pdf_image = ROOT / 'figures' / (Path(img).stem + '.pdf')
        if not pdf_image.exists(): missing.append(str(pdf_image.relative_to(ROOT)))
    if missing:
        raise FileNotFoundError('Figures are not ready: ' + ', '.join(sorted(set(missing))))
    rel = out.relative_to(ROOT).as_posix()
    run(['pandoc', str(out / 'body.md'), '--from=markdown+raw_tex+tex_math_dollars+tex_math_single_backslash',
        '--to=latex', '--top-level-division=chapter', '--number-sections',
        '--lua-filter=tools/book_images.lua', '--resource-path=figures',
        '--wrap=none', '--no-highlight', '--output=' + str(out / 'body.tex')])
    start = int(sources[0]['chapter']) - 1
    document = r'''\input{tools/book_preamble.tex}
\newcommand{\BookTitle}{@@TITLE@@}
\hypersetup{pdftitle={@@TITLE@@·408自学讲义},pdfsubject={概念、方法与代表题}}
\begin{document}
\pagenumbering{alph}
\begin{titlepage}
\thispagestyle{empty}
\vspace*{25mm}
{\sffamily\color{accent}\fontsize{16}{24}\selectfont 408 自学讲义}\par
\vspace{15mm}
{\sffamily\bfseries\color{ink}\fontsize{32}{45}\selectfont @@TITLE@@}\par
\vspace{15mm}
\noindent\rule{\textwidth}{0.5pt}\par
\vspace{5mm}
\noindent 例题就近解析，自测题在章末给出答案。\par
@@EDITION_NOTICE@@
\vfill
\noindent A4 单栏 · 2026 年 10 月\par
\end{titlepage}
\pagenumbering{roman}
\tableofcontents
\clearpage
\phantomsection\chapter*{阅读约定}
\addcontentsline{toc}{chapter}{阅读约定}
例题中的【年份】表示 408 真题；〖节号-题号〗表示王道书相应节的习题编号。
改动原题条件时标为“改编”；补充题另标“原创”。先根据题目条件辨认模型，再阅读连续的计算或执行过程。

本讲义默认下标、指针、位数和计量单位在初次使用处定义。
同一个字母在不同主题中可能表示不同的量，以当前定义为准。
并发过程、地址转换和通信时序中的结论都依赖给定假设；题目改变条件时，应重新检查解法成立的前提。

正文末尾附题目索引与方法索引，可从目录或书签跳转；索引右侧为正文页码。
\clearpage
\pagenumbering{arabic}
\setcounter{chapter}{@@START@@}
\input{@@REL@@/body.tex}
\input{@@REL@@/indexes.tex}
\end{document}
'''
    document = document.replace('@@TITLE@@', title).replace('@@REL@@', rel).replace('@@START@@', str(start))
    notice = r'\vspace{5mm}\noindent 正文内容审阅稿：本轮尚未进行版式检查。\par' if review else ''
    document = document.replace('@@EDITION_NOTICE@@', notice)
    (out / 'book.tex').write_text(document)
    begun = time.time()
    for n in range(1, passes + 1):
        with (out / f'xelatex-{n}.log').open('w') as log:
            try:
                run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
                    '-output-directory=' + str(out), '-jobname=' + sub, str(out / 'book.tex')],
                    stdout=log, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                print((out / f'xelatex-{n}.log').read_text(errors='replace')[-8000:])
                raise
    pdf = out / (sub + '.pdf')
    if review:
        target = ROOT / 'dist' / review_edition / (title + '_正文审阅稿.pdf')
    else:
        target = (out / (title + '_预览.pdf')) if partial else ROOT / 'dist' / (title + '_讲义.pdf')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(pdf.read_bytes())
    metadata = dict(subject=sub, title=title, partial=partial, sources=sources,
        heading_count=len(headings), questions=questions, methods=methods,
        headings=headings, pdf=str(target.relative_to(ROOT)), sha256=sha(target),
        elapsed_seconds=round(time.time() - begun, 2),
        edition='content_review' if review else ('preview' if partial else 'release'),
        review_edition=review_edition if review else None,
        layout_review_status='本轮未进行，按用户要求待内容审阅后执行' if review else '检查记录另存，构建不自动授予通过')
    (out / 'build_manifest.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    print(json.dumps({k:metadata[k] for k in ['subject','pdf','heading_count','elapsed_seconds']},ensure_ascii=False), flush=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--subjects', nargs='+', choices=list(SUBJECTS), default=list(SUBJECTS))
    p.add_argument('--partial', action='store_true')
    p.add_argument('--passes', type=int, default=3)
    p.add_argument('--chapters', nargs='+', type=int, help='Preview specific chapters; implies --partial')
    p.add_argument('--review', action='store_true', help='Export content-review PDFs without replacing the approved release or running layout checks')
    p.add_argument('--review-edition',default='revision3',help='Separate review output directory, e.g. revision3')
    args = p.parse_args()
    run(['python', 'tools/resolve_fonts.py'])
    for subject in args.subjects:
        build(subject, args.partial or bool(args.chapters), args.passes, args.chapters, args.review, args.review_edition)

if __name__ == '__main__': main()
