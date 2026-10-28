#!/usr/bin/env python3
"""Recreate the two working-set windows shown on course slide 3.2.5+3.2.3 p.10."""
from pathlib import Path
import subprocess

out = Path(__file__).resolve().parents[1] / 'figures'
values = [24, 15, 18, 23, 24, 17, 18, 24, 18, 17, 17, 15]
pieces = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360">', '<rect width="1200" height="360" fill="white"/>', '<g font-family="Noto Sans CJK SC,sans-serif" fill="#203d4b">']
for row, (start, label, group) in enumerate(((0, '访问完第 4 项', '{24, 15, 18, 23}'), (6, '访问完第 10 项', '{18, 24, 17}'))):
    top = 22 + row * 170
    pieces.append(f'<text x="20" y="{top+30}" font-size="29" font-weight="bold">{label}</text>')
    for i, val in enumerate(values):
        x = 20 + i * 94
        fill = '#dcecf6' if start <= i < start + 4 else '#f7f9fa'
        pieces.append(f'<rect x="{x}" y="{top+45}" width="85" height="62" rx="5" fill="{fill}" stroke="#8aa7b6" stroke-width="2"/>')
        pieces.append(f'<text x="{x+42.5}" y="{top+88}" font-size="32" text-anchor="middle">{val}</text>')
    pieces.append(f'<text x="20" y="{top+142}" font-size="27">蓝色为最近 4 次引用；去重后的工作集：{group}</text>')
pieces.append('</g></svg>')
svg = out / 'OS03_working_set_course.svg'
svg.write_text(''.join(pieces), encoding='utf-8')
for kind in ('pdf', 'png'):
    cmd = ['inkscape', str(svg), '--export-type=' + kind, '--export-filename=' + str(out / ('OS03_working_set_course.' + kind))]
    cmd.append('--export-text-to-path' if kind == 'pdf' else '--export-dpi=180')
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
