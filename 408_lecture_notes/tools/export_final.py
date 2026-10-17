#!/usr/bin/env python3
"""Export the current, checked four-book edition and a linked combined PDF."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/final'
NAMES = dict(DS='数据结构', CO='计算机组成原理', OS='操作系统', CN='计算机网络')


def load(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source_checks = load('editorial/final/choice_source_checks.json')
    choice_checks = load('editorial/final/choice_pdf_checks.json')
    labels = load('editorial/final/chinese_format_scan.json')
    table_checks = load('editorial/final/table_pdf_checks.json')
    assert source_checks['status'] == choice_checks['status'] == labels['status'] == table_checks['status'] == 'PASS'
    for path, fingerprint in source_checks['source_sha256'].items():
        assert sha(ROOT / path) == fingerprint, path
    visual_path = ROOT / 'editorial/final/visual_review.json'
    visual = json.loads(visual_path.read_text()) if visual_path.exists() else {'books': []}
    visual_books = {b['subject']: b for b in visual['books']}
    source_books = {b['subject']: b for b in source_checks['books']}
    books = []
    combined = fitz.open()
    toc, page_labels, print_sections = [], [], []
    offset = 0
    expected_links = 0
    for sub, title in NAMES.items():
        mf = load(f'build/{sub}/build_manifest.json')
        audit = load(f'editorial/final/pdf/{sub}/audit.json')
        choices = next(b for b in choice_checks['books'] if b['subject'] == sub)
        source_label = next(b for b in labels['books'] if b['subject'] == sub)
        tables = next(b for b in table_checks['books'] if b['subject'] == sub)
        path = ROOT / mf['pdf']
        fingerprint = sha(path)
        assert not mf['partial'] and mf['edition'] == 'release'
        assert audit['structural_status'] == 'PASS'
        assert fingerprint == mf['sha256'] == audit['sha256'] == choices['sha256'] == source_label['sha256'] == tables['sha256']
        assert audit['print_layout']['even_page_count'] and audit['print_layout']['cover_back_blank']
        assert audit['print_layout']['blank_pages_render_pure_white']
        assert offset % 2 == 0
        for source in mf['sources']:
            assert sha(ROOT / source['path']) == source['sha256']
        target = OUT / (title + '_最终稿.pdf')
        shutil.copyfile(path, target)
        with fitz.open(path) as doc:
            assert '正文内容审阅稿' not in doc[0].get_text()
            combined.insert_pdf(doc, links=False)
            # XeLaTeX uses named destinations. insert_pdf omits those links,
            # so resolve them to explicit page targets in the combined file.
            for page_index, page in enumerate(doc):
                for link in page.get_links():
                    if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                        point = fitz.Point(link['to'])
                        if link['kind'] == fitz.LINK_NAMED:
                            point.y = doc[link['page']].rect.height - point.y
                        combined[offset + page_index].insert_link(dict(kind=fitz.LINK_GOTO,
                            page=offset + link['page'], to=point,
                            zoom=link.get('zoom', 0.0), **{'from': link['from']}))
                    elif link['kind'] == fitz.LINK_URI:
                        combined[offset + page_index].insert_link(dict(kind=fitz.LINK_URI,
                            uri=link['uri'], **{'from': link['from']}))
            toc.append([1, title, offset + 1])
            toc.extend([[level + 1, text, page + offset] for level, text, page in doc.get_toc()])
            page_labels.extend([dict(rule, startpage=rule['startpage'] + offset) for rule in doc.get_page_labels()])
            pages = len(doc)
            assert pages % 2 == 0 and not doc[1].get_text().strip() and not doc[1].get_drawings()
        print_sections.append(dict(subject=sub, start_physical_page=offset + 1, physical_pages=pages,
            cover_back_blank_physical_page=offset + 2))
        detail = visual_books.get(sub, {})
        books.append(dict(subject=sub, title=title, pdf=str(target.relative_to(ROOT)),
            sha256=fingerprint, bytes=target.stat().st_size, physical_pages=pages,
            chapters=len(mf['sources']), sources=mf['sources'],
            numbered_examples=sum(q['title'].startswith('例 ') for q in mf['questions']),
            choices=source_books[sub]['choices'], statements=source_books[sub]['statements'],
            tables=tables['table_count'], print_layout=audit['print_layout'],
            structural_check='PASS', option_alignment_check='PASS',
            visual_check=detail.get('status') if detail.get('sha256') == fingerprint else 'NOT_CURRENT'))
        offset += pages
        expected_links += audit['internal_link_count']
    combined.set_toc(toc)
    combined.set_page_labels(page_labels)
    combined.set_metadata(dict(title='408 四科自学讲义·最终稿', author='408 讲义编辑项目',
        subject='数据结构、计算机组成原理、操作系统、计算机网络', creator='PyMuPDF'))
    combined_path = OUT / '408四科讲义_最终稿_合订本.pdf'
    combined.save(combined_path, garbage=4, deflate=True)
    combined.close()
    with fitz.open(combined_path) as doc:
        assert len(doc) == offset
        links = [link for page in doc for link in page.get_links() if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED)]
        assert len(links) == expected_links
        assert all(0 <= link.get('page', -1) < len(doc) for link in links)
        assert all(1 <= entry[2] <= len(doc) for entry in doc.get_toc())
        index = 0
        roundtrip_links = 0
        for book in books:
            with fitz.open(ROOT / book['pdf']) as source:
                book_offset = index
                for page in source:
                    target = doc[index]
                    assert target.get_text() == page.get_text(), (book['subject'], index)
                    matrix = fitz.Matrix(.3, .3)
                    assert target.get_pixmap(matrix=matrix, alpha=False).samples == page.get_pixmap(matrix=matrix, alpha=False).samples
                    original_links = [link for link in page.get_links() if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED)]
                    target_links = [link for link in target.get_links() if link['kind'] == fitz.LINK_GOTO]
                    assert len(original_links) == len(target_links)
                    for original, actual in zip(original_links, target_links):
                        point = fitz.Point(original['to'])
                        if original['kind'] == fitz.LINK_NAMED:
                            point.y = source[original['page']].rect.height - point.y
                        assert actual['page'] == book_offset + original['page']
                        assert abs(actual['to'].x - point.x) < .01 and abs(actual['to'].y - point.y) < .01
                        assert all(abs(a - b) < .01 for a, b in zip(actual['from'], original['from']))
                        roundtrip_links += 1
                    index += 1
        assert roundtrip_links == expected_links
    tools = ['tools/build_books.py', 'tools/book_choices.py', 'tools/book_images.lua',
        'tools/book_preamble.tex', 'tools/verify_choice_layout.py', 'tools/audit_books.py',
        'tools/verify_reader_layout.py', 'tools/verify_conversion.py', 'tools/resolve_fonts.py',
        'tools/book_tables.py', 'tools/verify_table_layout.py', 'tools/export_final.py', 'build_final.sh']
    manifest = dict(edition='final_duplex', exported_at=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        source_note='保留DeepSeek润色及后续内容修订；补IEEE浮点数表、逐表优化列宽，并为双面打印留白。正文与构建工具指纹见本清单。',
        counts=dict(books=4, chapters=sum(b['chapters'] for b in books), physical_pages=offset,
            numbered_examples=sum(b['numbered_examples'] for b in books),
            choices=source_checks['choices'], statements=source_checks['statements'],
            tables=table_checks['table_count'],
            aligned_monospaced_code_choice_sets=sum(c['already_aligned_monospaced_code_choices']
                for b in source_checks['books'] for c in b['chapters'])), books=books,
        combined=dict(pdf=str(combined_path.relative_to(ROOT)), sha256=sha(combined_path),
            bytes=combined_path.stat().st_size, physical_pages=offset, internal_links=expected_links,
            bookmarks=len(toc), source_page_text_and_pixels_identical=True),
        print_layout=dict(even_page_count=offset % 2 == 0, all_subject_covers_start_on_odd_pages=True,
            sections=print_sections),
        checks=['editorial/final/choice_source_checks.json', 'editorial/final/choice_pdf_checks.json',
            'editorial/final/visual_review.json', 'editorial/final/chinese_format_scan.json',
            'editorial/final/conversion_results.json', 'editorial/final/table_pdf_checks.json',
            'editorial/final/delivery_checks.json'],
        tool_sha256={p:sha(ROOT / p) for p in tools},
        review_scope='29章文本与结构保全；全部选项和题组逐组坐标核对；全页渲染与版面总览、重点页细看；不重新认证历史独立内容审校或官方题源。')
    manifest_path = OUT / '最终稿交付清单.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    pages_description = '、'.join(str(b['physical_pages']) for b in books)
    (OUT / '最终稿说明.md').write_text(f'''# 408 四科讲义最终稿

四科共29章、193道编号例题、{offset}页。保留DeepSeek润色，以及数据结构第5章自测第1题、计组例3-13的后续优化。

本版补充IEEE 754单、双精度参数及特殊编码表，并按实际字体宽度优化四科{table_checks['table_count']}张表格：保持正文满宽，让可容纳的短字段不换行，长说明允许必要换行。计组例3-12的六列表头及数据均可单行显示。

每本科目封面后均有一张纯空白页，总页数均为偶数，末尾按需补空白。合订时各科封面从奇数物理页开始。打印时选择双面、长边翻转，并保留PDF中的空白页。

本轮统一164组A—D选项与15组罗马数字题组：按实际字宽采用四列、两列或逐项布局；选项标签使用统一宽度，长项续行悬挂缩进。另1组程序代码选项保留等宽格式。计组例2-4和例2-9已重点复查。

分科PDF与合订本均有书签和有效内部链接；合订本保留四科目录层级，全部页面的文字及渲染像素与分科文件一致。四科分卷依次为{pages_description}页。交付清单提供源码和文件SHA256，核验记录存于项目editorial/final。

版面检查为全页渲染、全页总览和重点页细看，另有逐组选项坐标检查；历史题源及内容审校的边界仍以原记录为准。

重新生成：在完整项目根目录运行bash build_final.sh。构建不会自动补记新的人工阅图记录。
''')
    delivery = dict(status='PASS', combined_pdf_sha256=sha(combined_path),
        roundtrip_link_targets_checked=roundtrip_links,
        source_to_combined_page_text_and_pixels=f'All {offset} pages verified by export_final.py',
        source_chapters_verified=sum(len(b['sources']) for b in books),
        text_and_code_preservation='editorial/final/choice_source_checks.json',
        conversion_checks='editorial/final/conversion_results.json')
    delivery['print_layout'] = manifest['print_layout']
    delivery['table_layout_checks'] = 'editorial/final/table_pdf_checks.json'
    (ROOT / 'editorial/final/delivery_checks.json').write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(**manifest['counts'], combined=str(combined_path.relative_to(ROOT)),
        subject_pdfs=[b['pdf'] for b in books]), ensure_ascii=False))


if __name__ == '__main__':
    main()
