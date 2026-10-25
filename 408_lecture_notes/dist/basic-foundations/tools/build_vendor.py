#!/usr/bin/env python3
"""Optional: regenerate bundled CTeX-kit support files from unmodified dtx sources."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
vendor = ROOT/'vendor'
subprocess.run(['xetex', '-interaction=nonstopmode', '-halt-on-error', 'extract.ins'],
               cwd=vendor, check=True)
for src in vendor.iterdir():
    if src.suffix not in ('.sty','.cfg','.def'):
        continue
    name = 'ctex' if src.name == 'ctexhook.sty' else 'xeCJK'
    version, date = ('2.5.10', '2022-07-14') if name == 'ctex' else ('3.9.1', '2022-08-05')
    text = src.read_text(encoding='utf-8').replace(
        r'\GetIdInfo$Id$',
        f'\\GetIdInfo$Id: {name}.dtx {version} {date} 00:00:00 +0000 $')
    (ROOT/src.name).write_text(text, encoding='utf-8')
    src.unlink()
print('Regenerated the six local support files; upstream source code was not edited.')
