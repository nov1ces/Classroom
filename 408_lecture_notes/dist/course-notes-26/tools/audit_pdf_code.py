#!/usr/bin/env python3
"""Check displayed code against its searchable PDF text, without rewriting code."""
from pathlib import Path
import json, re, hashlib
import fitz

ROOT=Path(__file__).resolve().parents[1]

def font_config():
    """Read listing size and mono scale from the active template, not one font name."""
    cls=(ROOT/'common/sidenotes.cls').read_text()
    listing=re.search(r'\\lstdefinestyle\{SNcode\}.*?\\fontsize\{([\d.]+)\}',cls,re.S)
    mono=re.search(r'\\setmonofont\{([^}]+)\}\[(.*?)\]',cls,re.S)
    if not listing or not mono:
        return None
    scale=re.search(r'\bScale\s*=\s*([\d.]+)',mono[2])
    size=float(listing[1])*72/72.27
    return {'name':re.sub(r'[^a-z0-9]','',mono[1].lower()),
            'size':size,'mono_size':size*(float(scale[1]) if scale else 1.0)}

config=font_config()

def normalize(text):
    return re.sub(r'\s+', '', text)

results=[]
for chapter in sorted((ROOT/'chapters').iterdir()):
    if not chapter.is_dir() or not (chapter/'notes.pdf').exists():
        continue
    text=(chapter/'content.md').read_text()
    blocks=re.findall(r'^```[^\n]*\n(.*?)^```\s*$', text,re.M|re.S)
    code_text=[]; mono_spans=0
    doc=fitz.open(chapter/'notes.pdf')
    for page in doc:
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    if not config:
                        continue
                    name=re.sub(r'[^a-z0-9]','',span['font'].lower())
                    is_mono=config['name'] in name
                    if is_mono and abs(span['size']-config['mono_size'])<0.12:
                        mono_spans+=1
                    if ((is_mono and abs(span['size']-config['mono_size'])<0.12) or
                        (not is_mono and abs(span['size']-config['size'])<0.12)):
                        code_text.append(span['text'])
    haystack=normalize(''.join(code_text))
    missing=[]; typographic_changes=[]
    supported=bool(config) and (not blocks or mono_spans>0)
    if supported:
        for number,body in enumerate(blocks,1):
            for line_number,line in enumerate(body.splitlines(),1):
                needle=normalize(line)
                if needle and needle not in haystack:
                    # XeTeX may extract an ellipsis-only placeholder as U+22EF
                    # instead of the source U+2026; keep literal program strings strict.
                    if re.fullmatch(r'[\s…]+',line) and needle.replace('…','⋯') in haystack:
                        typographic_changes.append({'block':number,'line':line_number,
                                                    'source':'…','pdf_text':'⋯'})
                    else:
                        missing.append({'block':number,'line':line_number,'text':line})
    results.append({'chapter':chapter.name,'blocks':len(blocks),
                    'pdf_sha256':hashlib.sha256((chapter/'notes.pdf').read_bytes()).hexdigest(),
                    'font_config':config,'font_spans':mono_spans,
                    'status':'checked' if supported else 'unsupported_font_or_template',
                    'missing_lines':missing,'typographic_changes':typographic_changes,
                    'method':'compare whitespace-normalized source lines with listing text; cross-block matches can mask missing lines, mismatches and unsupported fonts require review'})
report={'chapters':results,'chapters_with_mismatches':[r['chapter'] for r in results if r['missing_lines']]}
(ROOT/'sources/pdf_code_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'chapters':len(results),'blocks':sum(r['blocks'] for r in results),'mismatches':{r['chapter']:len(r['missing_lines']) for r in results if r['missing_lines']}},ensure_ascii=False))
