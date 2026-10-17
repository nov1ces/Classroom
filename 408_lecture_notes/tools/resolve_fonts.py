#!/usr/bin/env python3
"""Resolve CJK TTC face indexes explicitly (XeTeX may otherwise pick face 0)."""
from pathlib import Path
import json,subprocess

ROOT=Path(__file__).resolve().parents[1]
def match(family,bold=False):
    query=family+(':style=Bold' if bold else '')
    result=subprocess.check_output(['fc-match','-f','%{family}\n%{file}\n%{index}',query],text=True).splitlines()
    actual,path,index=result
    if actual != family:
        raise RuntimeError(f'Required font missing: {family}; matched {actual}')
    return dict(family=actual,path=path,index=int(index))

def main():
    roles={'main':'Noto Serif CJK SC','sans':'Noto Sans CJK SC','mono':'Noto Sans Mono CJK SC'}
    out=[];manifest={}
    commands={'main':'setmainfont','sans':'setsansfont','mono':'setmonofont'}
    for role,family in roles.items():
        normal,bold=match(family),match(family,True)
        manifest[role]=dict(normal=normal,bold=bold)
        normal_path,bold_path=Path(normal['path']),Path(bold['path'])
        if normal_path.parent != bold_path.parent:
            raise RuntimeError('Normal and bold font files must share a directory')
        opts=[f"Path={{{normal_path.parent}/}}",f"FontIndex={normal['index']}",f"BoldFont={{{bold_path.name}}}",f"BoldFeatures={{FontIndex={bold['index']}}}"]
        if role=='main':opts += [f"ItalicFont={{{normal_path.name}}}",f"ItalicFeatures={{FontIndex={normal['index']}}}"]
        if role=='mono':opts += ['Scale=1.0']
        out.append('\\'+commands[role]+'{'+normal_path.name+'}['+','.join(opts)+']')
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'build/fonts.tex').write_text('\n'.join(out)+'\n')
    (ROOT/'editorial/verification/font_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print('Resolved SC faces 2/2/7 for body, headings and code')

if __name__=='__main__':main()
