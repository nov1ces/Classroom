import hashlib, json
import fitz
from PIL import Image
from topics import TOPICS
from pdf_sources import document
from config import BUILD, OUT, load_manifest, load_sources

ASSETS = BUILD / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
RASTER_SOURCES = {s['path'] for s in load_sources().values() if s['rasterize']}
SOURCE_HASHES = {s['path']: s['sha256'] for s in load_sources().values()}
NAMES = {'DS': '数据结构', 'CO': '计算机组成原理', 'OS': '操作系统', 'CN': '计算机网络'}
COLORS = {'navy': (0.075, 0.17, 0.29), 'teal': (0.0, 0.40, 0.44), 'muted': (0.39, 0.44, 0.48), 'line': (0.82, 0.86, 0.88), 'pale': (0.95, 0.97, 0.98)}
FONT_PATH = BUILD / 'HeaderCJK-subset.ttf'
FONT = fitz.Font(fontfile=str(FONT_PATH))
DOC = fitz.open()
TOC = []
POSITIONS = {}
DOTS = []
MAP = {'topics': {}, 'big': {}, 'relax': {}, 'answers': {}, 'subjects': {}}
W, H = 595.276, 841.89
LEFT, RIGHT, TOP, BOTTOM = 54, 541, 114, 785
CURRENT = None
Y = TOP
PAGE_TITLE = ''
PAGE_SUBTITLE = ''


def write(page, text, x, y, size=10, color='navy'):
    page.insert_font(fontname='sc', fontfile=str(FONT_PATH))
    page.insert_text((x, y), text, fontname='sc', fontsize=size, color=COLORS.get(color, color))


def wrap(text, width, size):
    output = []
    for paragraph in text.split('\n'):
        line = ''
        for ch in paragraph:
            if line and FONT.text_length(line + ch, fontsize=size) > width:
                output.append(line)
                line = ch
            else:
                line += ch
        output.append(line)
    return output


def paragraph(page, text, x, y, width=487, size=10, leading=16, color='navy'):
    for line in wrap(text, width, size):
        write(page, line, x, y, size, color)
        y += leading
    return y


def new_page(title, subtitle):
    global CURRENT, Y, PAGE_TITLE, PAGE_SUBTITLE
    CURRENT = DOC.new_page(width=W, height=H)
    PAGE_TITLE, PAGE_SUBTITLE = title, subtitle
    write(CURRENT, '408 / 薄弱点精读与练习册', LEFT, 33, 8.5, 'muted')
    write(CURRENT, '回顾 · 原题 · 迁移', 425, 33, 8.5, 'muted')
    write(CURRENT, title, LEFT, 71, 20, 'navy')
    write(CURRENT, subtitle, LEFT, 92, 9, 'teal')
    CURRENT.draw_line((LEFT, 102), (RIGHT, 102), color=COLORS['line'], width=0.6)
    Y = TOP
    return CURRENT


def continuation():
    return new_page(PAGE_TITLE, PAGE_SUBTITLE)


def reset_flow(title, subtitle):
    global CURRENT, PAGE_TITLE, PAGE_SUBTITLE, Y
    CURRENT = None
    PAGE_TITLE, PAGE_SUBTITLE, Y = title, subtitle, TOP


def bookmark(level, title, page=None):
    TOC.append([level, title, len(DOC) if page is None else page])


def dot(item_id, side, baseline):
    cx, cy = RIGHT - 4, baseline - 3.2
    CURRENT.draw_circle((cx, cy), 1.7, color=(0.59, 0.68, 0.70), fill=(0.59, 0.68, 0.70), width=0.1)
    page = len(DOC) - 1
    POSITIONS.setdefault(item_id, {}).setdefault(side, {'page': page, 'y': baseline - 12})
    DOTS.append({'id': item_id, 'side': side, 'page': page, 'rect': [cx - 6, cy - 6, cx + 6, cy + 6]})


def raster_asset(path, crop):
    key = 'c85-' + hashlib.sha256((path + SOURCE_HASHES[path] + json.dumps(crop, sort_keys=True)).encode()).hexdigest()[:24]
    jpg, meta = ASSETS / (key + '.jpg'), ASSETS / (key + '.json')
    if jpg.exists() and meta.exists():
        return jpg, json.loads(meta.read_text())
    box = fitz.Rect(crop['bbox'])
    pix = document(path)[crop['page'] - 1].get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72), clip=box, alpha=False)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    # Only remove empty vertical margins. Ink, figures, equations and code remain unchanged.
    ink = im.convert('L').point(lambda v: 255 if v < 185 else 0)
    bound = ink.getbbox()
    top, bottom = 0, im.height
    if bound:
        top, bottom = max(0, bound[1] - 7), min(im.height, bound[3] + 7)
    im = im.crop((0, top, im.width, bottom))
    im.save(jpg, quality=85, optimize=True, subsampling=1)
    info = {'width': box.width, 'height': box.height * im.height / pix.height}
    meta.write_text(json.dumps(info))
    return jpg, info


def assets(item, side):
    path = item[side + '_path']
    result = []
    for crop in item[side + '_crops']:
        box = fitz.Rect(crop['bbox'])
        if path in RASTER_SOURCES:
            jpg, info = raster_asset(path, crop)
            result.append({'raster': str(jpg), 'width': info['width'], 'height': info['height'], 'crop': crop})
        else:
            result.append({'path': path, 'width': box.width, 'height': box.height, 'crop': crop})
    return result


def asset_size(a):
    scale = min(1.12, (RIGHT - LEFT) / a['width'])
    return a['width'] * scale, a['height'] * scale


def place_asset(a, y):
    width, height = asset_size(a)
    rect = fitz.Rect(LEFT + (RIGHT - LEFT - width) / 2, y, LEFT + (RIGHT - LEFT + width) / 2, y + height)
    if 'raster' in a:
        CURRENT.insert_image(rect, filename=a['raster'])
    else:
        CURRENT.show_pdf_page(rect, document(a['path']), a['crop']['page'] - 1, clip=fitz.Rect(a['crop']['bbox']), keep_proportion=True)
    return y + height


def heading(item, side, continued=False):
    global Y
    prefix = '解析 / ' if side == 'answer' else ''
    label = prefix + item['label'] + (' · 续' if continued else '')
    write(CURRENT, label, LEFT, Y + 10, 9, 'teal')
    dot(item['id'], side, Y + 10)
    Y += 19
    if side == 'answer' and not continued:
        note = item.get('note', '')
        if note:
            Y = paragraph(CURRENT, note, LEFT, Y + 2, size=8.5, leading=13, color='muted') + 2


def put_item(item, side, level=4, force_page=False):
    global CURRENT, Y
    aa = assets(item, side)
    note_lines = len(wrap(item.get('note', ''), 487, 8.5)) if side == 'answer' and item.get('note') else 0
    head_height = 19 + note_lines * 13 + (4 if note_lines else 0)
    heights = [asset_size(a)[1] for a in aa]
    total = head_height + sum(heights) + max(0, len(aa) - 1) * 8
    if CURRENT is None or force_page or (Y > TOP and total > BOTTOM - TOP) or (Y > TOP and total <= BOTTOM - TOP and Y + total > BOTTOM) or Y + head_height + min(heights[0], 90) > BOTTOM:
        continuation()
    first_page = len(DOC)
    bookmark(level, ('解析 ' if side == 'answer' else '') + item['bookmark'], first_page)
    heading(item, side)
    for i, a in enumerate(aa):
        height = heights[i]
        if Y + height > BOTTOM + 0.2:
            if height > BOTTOM - TOP - 19:
                # The longest source region fits an A4 page at a readable, bounded scale.
                if i > 0 or Y > TOP + head_height + 1:
                    continuation()
                    heading(item, side, True)
                width, natural_height = asset_size(a)
                factor = min(1, (BOTTOM - Y) / natural_height)
                assert factor >= 0.86, (item['id'], side, natural_height)
                rect = fitz.Rect(LEFT + (487 - width * factor) / 2, Y, LEFT + (487 + width * factor) / 2, Y + natural_height * factor)
                if 'raster' in a:
                    CURRENT.insert_image(rect, filename=a['raster'])
                else:
                    CURRENT.show_pdf_page(rect, document(a['path']), a['crop']['page'] - 1, clip=fitz.Rect(a['crop']['bbox']))
                Y = rect.y1 + 8
                continue
            if Y > TOP + head_height + 1 or i > 0:
                continuation()
                heading(item, side, True)
        Y = place_asset(a, Y) + 8
    Y += 9
    assert Y < H - 28, (item['id'], side, Y)


def build_manifest():
    # Question text stays in the external PDFs; the index stores only placement metadata.
    return load_manifest()


def table_row(page, title, baseline, links, title_size=10):
    write(page, title, LEFT, baseline, title_size)
    for x, label, dest in links:
        write(page, label, x, baseline, 9, 'teal')
        page.insert_link({'kind': fitz.LINK_GOTO, 'from': fitz.Rect(x - 4, baseline - 11, x + 39, baseline + 4), 'page': dest, 'to': fitz.Point(54, 40)})
    page.draw_line((LEFT, baseline + 7), (RIGHT, baseline + 7), color=COLORS['line'], width=0.25)


def fill_contents(toc_pages, manifest):
    for pi, ts in enumerate([TOPICS[:22], TOPICS[22:]]):
        p = DOC[toc_pages[pi]]
        write(p, '知识回顾 / 完整旧题 / 集中解析', LEFT, 132, 10, 'muted')
        write(p, '回顾', 408, 132, 9, 'muted'); write(p, '题目', 452, 132, 9, 'muted'); write(p, '解析', 496, 132, 9, 'muted')
        y = 157
        for t in ts:
            d = MAP['topics'][t['code']]
            table_row(p, t['code'] + '  ' + t['title'], y, [(408, str(d['knowledge'] + 1), d['knowledge']), (452, str(d['question'] + 1), d['question']), (496, str(d['answer'] + 1), d['answer'])], 9.5)
            y += 25
        paragraph(p, '页码可点击。题目与对应解析之间另用淡色小圆点双向跳转；小圆点的可点击范围略大于外观，便于点选。', LEFT, 745, size=9, leading=14, color='muted')
    p = DOC[toc_pages[2]]
    write(p, '34 道综合题：29 道历年真题 + 5 道专项补充', LEFT, 132, 10, 'muted')
    y = 155
    for b in manifest['big']:
        d = POSITIONS[b['id']]
        origin = str(b['year']) + '·' + str(b['exam_num']) if b['year'] else '补充'
        table_row(p, f'{b["id"]}  {origin}  {b["title"]}', y, [(452, str(d['question']['page'] + 1), d['question']['page']), (496, str(d['answer']['page'] + 1), d['answer']['page'])], 9)
        y += 18
    p = DOC[toc_pages[3]]
    y = paragraph(p, '80 道 relax 选择题完整收录，按学科与章节排序。题目的微型圆点跳向本题解析，解析的圆点跳回题目；多页题也保留跳转点。', LEFT, 136, size=11, leading=19) + 20
    for sub in NAMES:
        group = [r for r in manifest['relax'] if r['subject'] == sub]
        d = POSITIONS[group[0]['id']]
        table_row(p, f'{NAMES[sub]} / {len(group)} 道 relax', y, [(452, str(d['question']['page'] + 1), d['question']['page']), (496, str(d['answer']['page'] + 1), d['answer']['page'])], 11)
        y += 40
    y += 22
    y = paragraph(p, '集中解析从第 ' + str(MAP['answer_start'] + 1) + ' 页开始。所有旧题、综合题和 relax 的解析均在练习之后。原错选只出现在解析区，重做时不会在题头提示答案。', LEFT, y, size=11, leading=19) + 23
    paragraph(p, '知识部分含定义、推导、例外与过程示例。冷门知识不会省略；具体题目能否归为知识缺口或执行失误，应结合本题解析与陌生变式结果判断。', LEFT, y, size=11, leading=19)


def main():
    manifest = build_manifest()
    review = fitz.open(BUILD / 'review.pdf')
    knowledge_end = 5 + sum(len(t['bodies']) for t in TOPICS)
    assert len(review) == knowledge_end + 1, len(review)
    DOC.insert_pdf(review, from_page=0, to_page=0, final=0)
    bookmark(1, '408 / 薄弱点精读与练习册', 1)
    toc_pages = []
    for title in ['目录 / 知识与旧题 1', '目录 / 知识与旧题 2', '目录 / 综合题', '目录 / relax 与解析']:
        new_page(title, '点击页码进入对应内容')
        toc_pages.append(len(DOC) - 1)
        bookmark(1, title)
    DOC.insert_pdf(review, from_page=1, to_page=4, final=0)
    for n, title in enumerate(['这次应先补什么', '冷门知识与粗心怎样处理', '继续挖掘的细节补课点', '怎样使用这一册'], start=6):
        bookmark(1, title, n)
    review_page = 5
    last_subject = None
    for t in TOPICS:
        if t['subject'] != last_subject:
            bookmark(1, NAMES[t['subject']] + ' / 回顾与完整旧题', len(DOC) + 1)
            last_subject = t['subject']
        bookmark(2, t['code'] + ' / ' + t['title'], len(DOC) + 1)
        MAP['topics'][t['code']] = {'knowledge': len(DOC)}
        DOC.insert_pdf(review, from_page=review_page, to_page=review_page + len(t['bodies']) - 1, final=0)
        review_page += len(t['bodies'])
        group = [x for x in manifest['old'] if x['topic'] == t['code']]
        MAP['topics'][t['code']]['question'] = len(DOC)
        bookmark(3, '完整旧题 / ' + str(len(group)) + ' 道', len(DOC) + 1)
        reset_flow(t['code'] + ' / 完整旧题', t['title'] + ' · 题目及全部选项')
        for item in group:
            put_item(item, 'question')
        print('questions', t['code'], len(DOC), flush=True)
    assert review_page == knowledge_end
    bookmark(1, '综合题 / 34 道', len(DOC) + 1)
    reset_flow('综合题 / 完整题干', '29 道历年真题与 5 道 B 树、外排序补充题')
    last_subject = None
    for item in manifest['big']:
        if item['subject'] != last_subject:
            bookmark(2, NAMES[item['subject']], len(DOC) + 1)
            last_subject = item['subject']
        put_item(item, 'question', level=3, force_page=True)
    bookmark(1, 'relax / 80 道完整选择题', len(DOC) + 1)
    for sub in NAMES:
        group = [x for x in manifest['relax'] if x['subject'] == sub]
        bookmark(2, NAMES[sub], len(DOC) + 1)
        reset_flow('relax / ' + NAMES[sub], '完整题目、选项与图形 · 解析统一置后')
        for item in group:
            put_item(item, 'question', level=3)
    DOC.insert_pdf(review, from_page=knowledge_end, to_page=knowledge_end)
    bookmark(1, '资料来源与题号规则')
    MAP['answer_start'] = len(DOC)
    new_page('集中解析', '原错选、解题过程与题源核验')
    bookmark(1, '集中解析 / 457 + 34 + 80 道')
    y = paragraph(CURRENT, '所有练习已在前部完整列出。从这里开始依次给出旧题、综合题和 relax 的解析。每道解析旁的小圆点跳回对应题目。', LEFT, 139, size=12, leading=22) + 25
    y = paragraph(CURRENT, '旧题的“任务特征”描述本题所需操作，不冒充实测难度。登记数量按同一回顾主题统计，不等于某个具体知识点的个人错误率。对明显定位到一步的错选给出局部判断；其余保留知识/流程候选，再由迁移题核验。', LEFT, y, size=11, leading=20) + 25
    y = paragraph(CURRENT, '题源核验包括 OS 3.1 第 11 题的静态/动态重定位与原解析分歧，以及 relax 网络第 6 章第 46 题的解析笔误。核验意见先于原解析显示，避免把印刷/模型问题当成你的能力问题。', LEFT, y, size=11, leading=20) + 25
    paragraph(CURRENT, '阅读时先看你写出的依据和中间步骤，再核对原解析。重做正确但机制讲不清，仍补机制；机制清楚且陌生变式稳定通过，转为间隔复习。', LEFT, y, size=11, leading=20)
    last_subject = None
    for t in TOPICS:
        if t['subject'] != last_subject:
            bookmark(2, NAMES[t['subject']] + ' / 旧题解析', len(DOC) + 1)
            last_subject = t['subject']
        group = [x for x in manifest['old'] if x['topic'] == t['code']]
        MAP['topics'][t['code']]['answer'] = len(DOC)
        bookmark(3, t['code'] + ' / ' + t['title'], len(DOC) + 1)
        reset_flow(t['code'] + ' / 旧题解析', t['title'] + ' · 原记录与完整解题过程')
        for item in group:
            put_item(item, 'answer')
        print('answers', t['code'], len(DOC), flush=True)
    bookmark(2, '综合题 / 完整解析', len(DOC) + 1)
    reset_flow('综合题 / 完整解析', '按 G- 编号与练习区对应')
    for item in manifest['big']:
        put_item(item, 'answer', level=3, force_page=True)
    bookmark(2, 'relax / 完整解析', len(DOC) + 1)
    for sub in NAMES:
        group = [x for x in manifest['relax'] if x['subject'] == sub]
        bookmark(3, NAMES[sub], len(DOC) + 1)
        reset_flow('relax / ' + NAMES[sub] + '解析', '原解析及必要核验意见')
        for item in group:
            put_item(item, 'answer')
    fill_contents(toc_pages, manifest)
    assert len(POSITIONS) == 571
    for item_id, destinations in POSITIONS.items():
        assert set(destinations) == {'question', 'answer'}, item_id
        assert destinations['question']['page'] < MAP['answer_start'] < destinations['answer']['page'], item_id
    for d in DOTS:
        target = POSITIONS[d['id']]['answer' if d['side'] == 'question' else 'question']
        DOC[d['page']].insert_link({'kind': fitz.LINK_GOTO, 'from': fitz.Rect(d['rect']), 'page': target['page'], 'to': fitz.Point(54, max(35, target['y'] - 6)), 'zoom': 0})
    for i, page in enumerate(DOC):
        write(page, '408 / 第二版', LEFT, 815, 8, 'muted')
        num = str(i + 1)
        write(page, num, RIGHT - FONT.text_length(num, fontsize=8.5), 815, 8.5, 'muted')
    DOC.set_toc(TOC, collapse=2)
    DOC.set_metadata({'title': '408 薄弱点精读与练习册｜第二版', 'author': '个人学习资料整理', 'subject': '41 个知识主题、457 道旧题、34 道综合题、80 道 relax，集中解析与双向微型圆点链接', 'keywords': '408,文件系统,中断,CPU可见性,OSI,TCP/IP,B树,外部排序,奈奎斯特,香农'})
    (BUILD / 'navigation.json').write_text(json.dumps({'positions': POSITIONS, 'dots': DOTS, 'map': MAP, 'toc': TOC, 'pages': len(DOC)}, ensure_ascii=False, indent=2))
    print('saving', len(DOC), 'pages', len(DOTS), 'dots', flush=True)
    DOC.save(OUT, garbage=4, deflate=True)
    print('saved', OUT, OUT.stat().st_size, flush=True)


if __name__ == '__main__':
    main()
