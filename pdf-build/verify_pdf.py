import json
import fitz
from PIL import Image

from config import BUILD, OUT as PDF, read_items

nav = json.loads((BUILD / 'navigation.json').read_text(encoding='utf-8'))
items = read_items()
doc = fitz.open(PDF)
assert len(doc) == nav['pages']
assert {k: len(v) for k, v in items.items()} == {'old': 457, 'big': 34, 'relax': 80}
assert len(nav['positions']) == 571
assert len({x['id'] for group in items.values() for x in group}) == 571
all_links = [p.get_links() for p in doc]
for dot in nav['dots']:
    target_side = 'answer' if dot['side'] == 'question' else 'question'
    target = nav['positions'][dot['id']][target_side]
    rect = fitz.Rect(dot['rect'])
    matching = [l for l in all_links[dot['page']] if fitz.Rect(l['from']).intersects(rect) and l['kind'] == fitz.LINK_GOTO and l['page'] == target['page']]
    assert matching, (dot['id'], dot['side'], dot['page'])
for item_id, sides in nav['positions'].items():
    assert set(sides) == {'question', 'answer'}
    assert sides['question']['page'] < nav['map']['answer_start'] < sides['answer']['page']
    for side, pos in sides.items():
        # The added identifier is searchable on both the question and answer page.
        assert item_id in doc[pos['page']].get_text(), (item_id, side)
for links in all_links:
    assert all(0 <= l['page'] < len(doc) for l in links if l['kind'] == fitz.LINK_GOTO)
assert all(1 <= p <= len(doc) for _, _, p in doc.get_toc())
assert '知识与旧题' in doc[1].get_text()
assert '操作系统' in doc[2].get_text()
assert '综合题' in doc[3].get_text()
assert 'relax' in doc[4].get_text()
fitz.TOOLS.mupdf_warnings(reset=True)
blank = []
for i, p in enumerate(doc):
    pix = p.get_pixmap(matrix=fitz.Matrix(.5, .5), colorspace=fitz.csGRAY, alpha=False)
    im = Image.frombytes('L', (pix.width, pix.height), pix.samples)
    region = im.crop((20, 53, im.width - 20, im.height - 25))
    if sum(v < 225 for v in region.getdata()) < 25:
        blank.append(i + 1)
assert not blank, blank
warnings = fitz.TOOLS.mupdf_warnings(reset=True)
report = {
    'pdf': str(PDF), 'pages': len(doc), 'bytes': PDF.stat().st_size,
    'counts': {k: len(v) for k, v in items.items()},
    'question_answer_pairs': len(nav['positions']),
    'micro_dot_links': len(nav['dots']),
    'all_internal_links': sum(len(v) for v in all_links),
    'bookmarks': len(doc.get_toc()),
    'answers_start_page': nav['map']['answer_start'] + 1,
    'blank_pages': blank, 'render_warnings': warnings,
}
(BUILD / 'final_validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
