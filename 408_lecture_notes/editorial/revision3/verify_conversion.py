#!/usr/bin/env python3
"""Check editable code survives conversion; never open or inspect book PDFs."""
from pathlib import Path
import hashlib, json, re, subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
checks=[]
def pandoc(source,target,filtered=False):
    args=['pandoc','-f','markdown+raw_tex+tex_math_dollars+tex_math_single_backslash','-t',target,'--wrap=none','--no-highlight']
    if filtered:args.append('--lua-filter=tools/book_images.lua')
    return subprocess.run(args,input=source,text=True,capture_output=True,check=True,cwd=ROOT).stdout
def check(name,actual,expected,scope):
    assert actual==expected,(name,actual,expected)
    checks.append(dict(id=name,actual=actual,expected=expected,status='PASS',scope=scope))
def nodes(value,tag):
    if isinstance(value,dict):
        if value.get('t')==tag:yield value
        for child in value.values():yield from nodes(child,tag)
    elif isinstance(value,list):
        for child in value:yield from nodes(child,tag)
def pipe_tables(source):
    lines=source.splitlines();fenced=False;i=0;found=[]
    def cells(line):return re.split(r'(?<!\\)\|',line.strip())[1:-1]
    while i<len(lines):
        if re.match(r'^\s*(```|~~~)',lines[i]):fenced=not fenced;i+=1;continue
        if not fenced and i+1<len(lines) and lines[i].lstrip().startswith('|') and lines[i].rstrip().endswith('|'):
            separator=cells(lines[i+1])
            if separator and all(re.fullmatch(r'\s*:?-{3,}:?\s*',part) for part in separator):
                n=len(cells(lines[i]));j=i+1
                while j<len(lines) and lines[j].lstrip().startswith('|') and lines[j].rstrip().endswith('|'):
                    assert len(cells(lines[j]))==n,('source table column mismatch',i+1,j+1,lines[j])
                    j+=1
                found.append(dict(columns=n,data_rows=j-i-2,line=i+1));i=j;continue
        i+=1
    return found

fixture='''| 名称 | 汇编格式 |
| --- | --- |
| 加法 | `ADD Rs, Rd` |
| 取数 | `LOAD Rd, mem` |
| 比较 | `cmp dword ptr [ebp+8], 1` |

正文中的 `long long` 和 `a[i]` 保持原字符。
'''
tex=pandoc(fixture,'latex',True)
check('CONV-01',bool(re.search(r'(?:^|&)\s*\\allowbreak\{\}',tex,re.M)),False,
      '表格单元格首没有垂直模式的裸断点；只核转换源码，不声称成稿版式通过。')
check('CONV-02',r'\texttt{ADD\ Rs,}\allowbreak{}\texttt{\ Rd}' in tex,True,
      '逗号两侧字符和空格保留，断点只在两个代码片段之间。')
check('CONV-03',all(s in tex for s in [r'\texttt{LOAD\ Rd,}',r'\texttt{\ mem}',
       r'\texttt{cmp\ dword\ ptr\ {[}ebp+8{]},}',r'\texttt{\ 1}',
       r'\texttt{long\ long}',r'\texttt{a{[}i{]}}']),True,
      '代表性的助记符、寄存器、方括号、立即数与空格未在源转换中丢失。')
assembly='  16 00401025 E8 D6 FF FF FF  call f1\nI1: LOAD R1, [a]\nI2: ADD R1, R2  // R2 <- R1 + R2'
block_tex=pandoc('```text\n'+assembly+'\n```\n','latex',True)
check('CONV-04','\\begin{verbatim}\n'+assembly+'\n\\end{verbatim}' in block_tex,True,
      '等宽代码块的实际字符、缩进和行序原样进入LaTeX。')

sources={};block_count=0;inline_count=0;table_count=0;table_dimensions=[]
for path in sorted((ROOT/'manuscript').glob('*/[0-9][0-9]_*.md')):
    source=path.read_text();sources[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    ast=json.loads(pandoc(source,'json'))
    converted=pandoc(source,'latex',True)
    blocks=list(nodes(ast,'CodeBlock'));block_count+=len(blocks)
    inline_count+=len(list(nodes(ast,'Code')))
    expected_tables=pipe_tables(source);parsed_tables=list(nodes(ast,'Table'))
    assert len(expected_tables)==len(parsed_tables),(path,'table lost in parse',len(expected_tables),len(parsed_tables))
    for specification,table in zip(expected_tables,parsed_tables):
        content=table['c'];columns=len(content[2])
        data_rows=[row for body in content[4] for row in body[2]+body[3]]+content[5][1]
        assert columns==specification['columns'],(path,specification,columns)
        assert len(data_rows)==specification['data_rows'],(path,specification,len(data_rows))
        assert all(sum(cell[3] for cell in row[1])==columns for row in content[3][1]+data_rows),(path,specification,'cell count')
        table_count+=1;table_dimensions.append(dict(path=str(path.relative_to(ROOT)),**specification))
    for block in blocks:
        literal=block['c'][1]
        assert '\\begin{verbatim}\n'+literal+'\n\\end{verbatim}' in converted,(path,literal[:80])
    assert not re.search(r'(?:^|&)\s*\\allowbreak\{\}\\texttt',converted,re.M),path
check('CONV-05',len(sources),29,'实际转换29章源码；范围为代码保全，不核排版。')
check('CONV-06',block_count>0,True,f'逐一对照全部{block_count}个实际代码块的字符与行序，另扫描{inline_count}处行内代码。')
check('CONV-07',table_count>0,True,f'逐一比较全部{table_count}张管道表的表头、分隔行、数据行列数；与真实Pandoc AST行列交叉，不检查成稿版面。')
out=dict(status='PASS',checks=checks,check_count=len(checks),source_sha256=sources,
         actual_code_blocks=block_count,actual_inline_code_nodes=inline_count,actual_pipe_tables=table_count,table_dimensions=table_dimensions,
         pdf_opened=False,pdf_layout_check_performed=False,
         limitation='这里只检验源字符和模式断点；不得由此宣称PDF视觉、分页或裁切检查通过。')
(HERE/'conversion_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status='PASS',conversion_checks=len(checks),code_blocks=block_count,
                     inline_code_nodes=inline_count,pdf_layout_check_performed=False),ensure_ascii=False))
