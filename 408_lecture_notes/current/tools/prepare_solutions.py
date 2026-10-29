#!/usr/bin/env python3
"""Match current examples conservatively and regenerate original solution crops.

Run after chapter authors have finished examples.json::
    python current/tools/prepare_solutions.py
A partial check requires --output so it cannot replace the complete index::
    python current/tools/prepare_solutions.py --chapter DS01 --output /tmp/DS01.json

Only typographic normalization is automatic. Equivalent paraphrases require an
independent review ledger binding exact question SHA and original PDF identities,
pages and bounding boxes. Changed data, expanded requirements, source errors,
ambiguous candidates and unverified sources retain the author's native solution.
No historical image cache is read. Source crops are rendered
from the original PDF at 300 dpi; clipped PDFs preserve original PDF objects.
The index records source identification separately from pending visual review.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import difflib
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
ANALYSIS = Path('/workspace/study_analysis/v2')
DPI = 300
VERSION = 2
SUBJECT_DIRS = {'DS': '01_数据结构', 'CO': '02_计算机组成原理',
                'OS': '03_操作系统', 'CN': '04_计算机网络'}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(2 ** 20), b''):
            h.update(chunk)
    return h.hexdigest()


def clean_question(text):
    """Remove worksheet running material and leading numbering, not question data."""
    lines = []
    for line in str(text or '').splitlines():
        line = line.strip()
        if not line:
            continue
        if (re.match(r'^·\s*第\s*\d+\s*页', line)
                or re.match(r'^(公众号[:：]|27王道|一[、.]\s*单项选择题)', line)
                or re.match(r'^第[一二三四五六七八九十\d]+\s*章', line)
                or re.match(r'^\d+\.\d+\s*[\u4e00-\u9fff]', line)
                or ('答案见' in line and len(line) < 30)):
            continue
        lines.append(line)
    text = '\n'.join(lines)
    text = re.sub(r'^\s*\d{1,3}[.．、]\s*', '', text)
    text = re.sub(r'【\s*\d{4}\s*统考\s*真题\s*[】〗]', '', text)
    return text.strip()


def canonical(text):
    """Normalize typography while retaining math relations, numbers and negations."""
    text = unicodedata.normalize('NFKC', clean_question(text))
    for old, new in [ ('\\leq', '≤'), ('\\geq', '≥'), ('\\neq', '≠'),
                      ('\\times', '×'), ('\\cdot', '×'), ('\\to', '→'),
                      ('\\Theta', 'Θ'), ('\\log', 'log') ]:
        text = text.replace(old, new)
    text = re.sub(r'\\(?:text|mathrm|mathbf|operatorname)\s*\{([^{}]*)\}', r'\1', text)
    text = re.sub(r'\\(?:left|right|displaystyle|quad|qquad)\b', '', text)
    text = text.replace('\\(', '').replace('\\)', '').replace('\\[', '').replace('\\]', '')
    text = text.replace('`', '').replace('$', '').replace('**', '')
    text = re.sub(r'\s+', '', text)
    # Ignore prose punctuation and empty answer blanks, retain meaningful math signs.
    text = re.sub(r'[。?？!！:：;；“”"「」【】〖〗]', '', text)
    text = text.replace('，', ',')
    text = re.sub(r'(?<!\d)[.,]|[.,](?!\d)', '', text)
    text = text.replace('()', '').replace('（）', '')
    return text


def critical_tokens(text):
    # Altered data/operators must never be admitted by a high prose similarity score.
    text = canonical(text)
    return re.findall(r'\d+(?:\.\d+)?|[<>≤≥≠=+*/%−-]|不|非|最|仅|至多|至少', text)


def compare_question(current, original):
    a, b = canonical(current), canonical(original)
    score = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0
    evidence = {'similarity': round(score, 5), 'example_chars': len(a), 'source_chars': len(b),
                'critical_tokens_equal': critical_tokens(current) == critical_tokens(original)}
    if '\ufffd' in a + b or '\x00' in a + b:
        return False, evidence, '题干含无法识别字符，不能确认公式或数据完整性'
    if len(a) < 12 or len(b) < 12:
        return False, evidence, '题干有效文本过短，不能确认原题身份'
    if a == b:
        return True, evidence, '原题题干、数据和选项经排版规范化后完全一致'
    # A one-character prose OCR variation in a long question is allowed only when
    # critical data and relations agree. No topical/fuzzy threshold can accept rewrites.
    differences = [op for op in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
                   if op[0] != 'equal']
    only_cjk = all(op == 'replace' and i2-i1 == j2-j1 == 1
                   and re.fullmatch(r'[\u4e00-\u9fff]', a[i1:i2])
                   and re.fullmatch(r'[\u4e00-\u9fff]', b[j1:j2])
                   for op, i1, i2, j1, j2 in differences)
    if (len(a) >= 100 and score >= .992 and len(differences) == 1
            and only_cjk and evidence['critical_tokens_equal']):
        # Still do not promote uncertain OCR prose to a verified image match.
        return False, evidence, '疑似单字 OCR 差异；缺少逐字确证，保留原生解析'
    return False, evidence, '题干、数据或选项与原题不完全一致；不套用原解析截图'


class Sources:
    def __init__(self, analysis, project, verifications=None):
        self.analysis, self.project = analysis, project
        self.verifications = {}
        self.verifications_path = Path(verifications) if verifications else None
        if self.verifications_path and self.verifications_path.exists():
            ledger = read_json(self.verifications_path)
            entries = ledger.get('verifications', [])
            for entry in entries:
                if entry['example_id'] in self.verifications:
                    raise ValueError(f"独立核验台账例题 id 重复: {entry['example_id']}")
                self.verifications[entry['example_id']] = entry
        self.documents = {}
        self.hashes = {}
        self.candidates = []
        self.by_key = collections.defaultdict(list)
        self.inputs = ([self.verifications_path] if self.verifications_path
                       and self.verifications_path.exists() else [])
        answers_path = analysis / 'book_answers.json'
        items_path = analysis / 'all_items.json'
        big_path = analysis / 'big_manifest.json'
        answers = read_json(answers_path)
        groups = read_json(items_path)
        big = read_json(big_path)
        self.inputs.extend([answers_path, items_path, big_path])
        # Existing full manifests carry more precise question coordinates than text dumps.
        seen = set()
        for group, items in list(groups.items()) + [('big_manifest', big)]:
            for item in items:
                key = self.key(item)
                signature = (str(item.get('question_path')), str(item.get('question_crops')),
                             str(item.get('answer_path')), str(item.get('answer_crops')))
                if signature in seen:
                    continue
                seen.add(signature)
                candidate = {'id': item.get('id'), 'source_key': key,
                             'subject': item.get('subject'), 'group': group,
                             'question': item.get('text', ''),
                             'question_path': item.get('question_path') or item.get('book'),
                             'question_crops': item.get('question_crops') or item.get('crops', []),
                             'answer_path': item.get('answer_path'),
                             'answer_crops': item.get('answer_crops', []),
                             'answer': item.get('answer') if isinstance(item.get('answer'), str) else None}
                if group == 'old' and key in answers:
                    candidate['answer'] = answers[key].get('answer')
                self.add(candidate)
        # Full indexed comprehensive questions are distinct from same-numbered
        # multiple-choice workbook entries. Preserve their own candidate IDs/crops.
        full_big_path = analysis / 'big_candidates.json'
        if full_big_path.exists():
            self.inputs.append(full_big_path)
            for item in read_json(full_big_path):
                answer = item.get('answer')
                if not isinstance(answer, dict) or not answer.get('crops'):
                    continue
                self.add({'id': f"full-big-{self.key(item)}",
                          'source_key': self.key(item), 'subject': item.get('subject'),
                          'group': 'full_comprehensive_question', 'question': item.get('text', ''),
                          'question_path': item.get('book'), 'question_crops': item.get('crops', []),
                          'answer_path': answer.get('book'), 'answer_crops': answer.get('crops', []),
                          'answer': None})
        # Book answer keys cover questions beyond the previously selected 457 examples.
        # Native text from each full worksheet supplies independently checkable questions.
        for subject, dirname in SUBJECT_DIRS.items():
            paths = sorted((project / dirname).glob('*横版*选择题做题本.pdf'))
            if len(paths) != 1:
                continue
            path = paths[0]
            self.inputs.append(path)
            doc = self.document(path)
            bookmarks = [(re.match(r'^(\d+\.\d+)', title).group(1), page)
                         for level, title, page in doc.get_toc()
                         if level == 2 and re.match(r'^(\d+\.\d+)', title)]
            section = None
            sections_by_page = dict((page, sec) for sec, page in bookmarks)
            for pageno, page in enumerate(doc, 1):
                section = sections_by_page.get(pageno, section)
                if not section:
                    continue
                text = page.get_text('text', sort=True)
                marks = list(re.finditer(r'^\s*(\d{1,3})[.．、](?!\d)', text, re.M))
                if len(marks) != 1:
                    continue
                num = int(marks[0].group(1))
                key = f'{subject}:{section}:{num}'
                if key not in answers:
                    continue
                qtext = clean_question(text[marks[0].start():])
                answer = answers[key]
                self.add({'id': f'workbook-{key}', 'source_key': key, 'subject': subject,
                          'group': 'full_workbook', 'question': qtext,
                          'question_path': str(path),
                          'question_crops': [{'page': pageno, 'bbox': list(page.rect)}],
                          'answer_path': answer['book'], 'answer_crops': answer.get('crops', []),
                          'answer': answer.get('answer')})

    @staticmethod
    def key(item):
        subject, section = item.get('subject'), item.get('section')
        num = item.get('题号', item.get('num'))
        return f'{subject}:{section}:{num}' if subject and section and num is not None else None

    def add(self, candidate):
        if not candidate['question']:
            return
        candidate['canonical'] = canonical(candidate['question'])
        self.candidates.append(candidate)
        if candidate['source_key']:
            self.by_key[candidate['source_key']].append(candidate)
        if candidate['id']:
            self.by_key[candidate['id']].append(candidate)

    def document(self, path):
        path = str(Path(path).resolve())
        if path not in self.documents:
            self.documents[path] = fitz.open(path)
        return self.documents[path]

    def fingerprint(self, path):
        path = str(Path(path).resolve())
        if path not in self.hashes:
            self.hashes[path] = sha_file(path)
        return self.hashes[path]

    def crop_text(self, path, crops):
        return '\n'.join(self.document(path)[crop['page'] - 1].get_text(
            'text', clip=fitz.Rect(crop['bbox']), sort=True) for crop in crops)

    def independently_verified(self, example, subject):
        """An explicit review binds exact authored text to immutable original crops.

        No similarity score admits a semantic rewrite. A human/model reviewer must
        inspect question data, choices, requirements and any diagram independently.
        Stale ledger records fail closed when either authored text or PDFs change.
        """
        entry = self.verifications.get(example['id'])
        if not entry:
            return None
        evidence = {'verification_method': 'independent_review_ledger',
                    'verification_example_id': example['id'],
                    'ledger_path': str(self.verifications_path),
                    'ledger_sha256': self.fingerprint(self.verifications_path)}
        qsha = hashlib.sha256(example['question'].encode('utf-8')).hexdigest()
        if entry.get('question_sha256') != qsha:
            return None, evidence, '独立核验台账题干 SHA 已过期；保留原生解析'
        reason = str(entry.get('reason') or '').strip()
        if not reason or not entry.get('reviewed_utc'):
            return None, evidence, '独立核验台账缺少核验理由或时间；保留原生解析'
        evidence['independent_review_reason'] = reason
        if entry.get('verdict') == 'native':
            return None, evidence, '独立核验保留原生解析：' + reason
        if entry.get('verdict') != 'independent_verified':
            return None, evidence, '独立核验台账结论无效；保留原生解析'
        identity = entry.get('source', {})
        matches = [c for c in self.candidates if c['subject'] == subject
                   and c.get('id') == identity.get('id')
                   and c.get('source_key') == identity.get('source_key')
                   and str(Path(c['question_path']).resolve()) == identity.get('question_pdf')
                   and str(Path(c['answer_path']).resolve()) == identity.get('answer_pdf')
                   and c['question_crops'] == identity.get('question_crops')
                   and c['answer_crops'] == identity.get('answer_crops')]
        if not matches:
            return None, evidence, '独立核验来源身份或页码坐标与原材料索引不一致；保留原生解析'
        candidate = matches[0]
        for field, source_field in [('question_pdf_sha256', 'question_path'),
                                    ('answer_pdf_sha256', 'answer_path')]:
            if identity.get(field) != self.fingerprint(candidate[source_field]):
                return None, evidence, '独立核验来源 PDF 指纹已变更；保留原生解析'
        if not candidate['answer_crops']:
            return None, evidence, '独立核验来源缺少原解析坐标；保留原生解析'
        answer = str(example.get('answer', '')).strip().upper()
        original_answer = str(candidate.get('answer') or '').strip().upper()
        if (re.fullmatch(r'[ABCD]', answer) and re.fullmatch(r'[ABCD]', original_answer)
                and answer != original_answer):
            return None, evidence, f'答案与独立核验原解析冲突（当前 {answer}，来源 {original_answer}）；保留原生解析'
        corrected_crops = entry.get('export_answer_crops')
        if corrected_crops is not None:
            # Reviewer may narrow/split indexed rectangles to exclude neighboring
            # solutions. Every rectangle must remain within its original page crop.
            if not isinstance(corrected_crops, list) or not corrected_crops:
                return None, evidence, '独立核验的修正裁切列表无效；保留原生解析'
            for crop in corrected_crops:
                rect = fitz.Rect(crop['bbox'])
                if (not rect.is_valid or rect.is_empty or not any(
                        original['page'] == crop['page']
                        and fitz.Rect(original['bbox']).contains(rect)
                        for original in candidate['answer_crops'])):
                    return None, evidence, '独立核验修正裁切超出原索引范围；保留原生解析'
            candidate = {**candidate, 'indexed_answer_crops': candidate['answer_crops'],
                         'answer_crops': corrected_crops}
            evidence['crop_correction_reason'] = entry.get('crop_correction_reason')
        evidence['identity_verification'] = 'independent_verified'
        evidence['reviewed_utc'] = entry['reviewed_utc']
        return candidate, evidence, '独立逐题核验确认同题：' + reason

    def match(self, example, subject):
        verified = self.independently_verified(example, subject)
        if verified is not None:
            return verified
        key = example.get('source_key')
        choices = self.by_key.get(key, []) if key else self.candidates
        choices = [c for c in choices if c['subject'] == subject]
        # Exact normalized manifest candidates are cheap to retrieve. Only they
        # can pass; remaining candidates supply a nearest-candidate audit reason.
        if not key and choices:
            qnorm = canonical(example.get('question'))
            exact = [c for c in choices if c['canonical'] == qnorm]
            if exact:
                choices = exact
            else:
                choices = sorted(choices, key=lambda c: difflib.SequenceMatcher(
                    None, qnorm, c['canonical'], autojunk=False).quick_ratio(), reverse=True)[:8]
        if not choices:
            return None, None, 'source_key 无可核对题干或未收录；保留原生解析' if key else '没有可核对的同科原题记录；保留原生解析'
        accepted, near = [], []
        for candidate in choices:
            # Manifest text is sometimes OCR. Prefer original native PDF text when usable.
            original = candidate['question']
            try:
                native = self.crop_text(candidate['question_path'], candidate['question_crops'])
                if candidate['group'] == 'full_workbook':
                    marker = re.search(r'^\s*\d{1,3}[.．、](?!\d)', native, re.M)
                    if marker:
                        native = native[marker.start():]
                if len(re.findall(r'[\u4e00-\u9fff]', native)) >= 12:
                    original = native
            except (OSError, ValueError, RuntimeError, IndexError, TypeError):
                pass
            ok, evidence, reason = compare_question(example.get('question'), original)
            evidence['source_text_origin'] = 'original_pdf_native_text' if original != candidate['question'] else 'manifest_question_text'
            near.append((evidence['similarity'], evidence, reason, candidate))
            if ok:
                answer = str(example.get('answer', '')).strip().upper()
                original_answer = str(candidate.get('answer') or '').strip().upper()
                if re.fullmatch(r'[ABCD]', answer) and re.fullmatch(r'[ABCD]', original_answer) and answer != original_answer:
                    near[-1] = (1, evidence, f'答案与原解析冲突（当前 {answer}，来源 {original_answer}）；保留原生解析', candidate)
                    continue
                accepted.append((candidate, evidence, reason))
        if not accepted:
            _, evidence, reason, candidate = max(near, key=lambda entry: entry[0])
            evidence['nearest_candidate_id'] = candidate['id']
            evidence['nearest_source_key'] = candidate['source_key']
            return None, evidence, reason
        # Different manifest names can describe the same original answer crop.
        signatures = {(str(c['answer_path']), json.dumps(c['answer_crops'], sort_keys=True))
                      for c, _, _ in accepted}
        if len(signatures) != 1:
            return None, None, '相同题干对应多个不同解析来源，不能自动确认；保留原生解析'
        candidate, evidence, reason = accepted[0]
        if not candidate['answer_path'] or not candidate['answer_crops']:
            return None, evidence, '题干已匹配，但没有可核验原解析坐标；保留原生解析'
        return candidate, evidence, ('source_key 已定位；' if key else '依据完整题干独立定位；') + reason

    def close(self):
        for doc in self.documents.values():
            doc.close()


def split_long_crop(sources, source_path, crop, max_ratio=1.11):
    """Split only at source-image blank rows; never cut through a long diagram."""
    import math
    import numpy as np

    rect = fitz.Rect(crop['bbox'])
    if rect.height <= rect.width * max_ratio:
        return [crop]
    page = sources.document(source_path)[int(crop['page']) - 1]
    if not rect.is_valid or rect.is_empty or not page.rect.contains(rect):
        raise ValueError(f'原 PDF bbox 无效或越界: {list(rect)}')
    pix = page.get_pixmap(dpi=DPI, clip=rect, colorspace=fitz.csRGB, alpha=False)
    pixels = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    # Source ink is dark; the pale watermark must not suppress real blank lines.
    ink_rows = (pixels[:, :, :3].min(axis=2) < 135).sum(axis=1)
    blank = ink_rows <= max(2, int(pix.width * .001))
    padded = np.concatenate(([False], blank, [False])).astype(np.int8)
    starts = np.flatnonzero(np.diff(padded) == 1)
    ends = np.flatnonzero(np.diff(padded) == -1)
    gaps = [(start + end) / 2 for start, end in zip(starts, ends)
            if end - start >= DPI / 72 * 1.8]
    points_per_row = rect.height / pix.height
    gap_points = [rect.y0 + row * points_per_row for row in gaps]
    max_height = rect.width * max_ratio
    count = math.ceil(rect.height / max_height)
    boundaries = [rect.y0]
    for remaining in range(count, 1, -1):
        top = boundaries[-1]
        target = top + (rect.y1 - top) / remaining
        low = max(top + 45, rect.y1 - max_height * (remaining - 1))
        high = min(top + max_height, rect.y1 - 45 * (remaining - 1))
        eligible = [y for y in gap_points if low <= y <= high]
        if not eligible:
            return [{**crop, 'needs_split': True,
                     'split_reason': '原图过长且未找到可安全切分的空白行；需人工处理长图或表格'}]
        boundaries.append(min(eligible, key=lambda y: abs(y - target)))
    boundaries.append(rect.y1)
    return [{**crop, 'bbox': [rect.x0, top, rect.x1, bottom],
             'parent_bbox': list(rect), 'split_part': i, 'split_parts': count,
             'split_reason': '按原 PDF 新渲染 300dpi 的空白行连续切分'}
            for i, (top, bottom) in enumerate(zip(boundaries, boundaries[1:]), 1)]


def export_crop(sources, source_path, crop, assets, current, dry_run=False):
    page_number = int(crop['page'])
    doc = sources.document(source_path)
    if not 1 <= page_number <= len(doc):
        raise ValueError(f'原 PDF 页码越界: {page_number}')
    page = doc[page_number - 1]
    rect = fitz.Rect(crop['bbox'])
    if not rect.is_valid or rect.is_empty or not page.rect.contains(rect):
        raise ValueError(f'原 PDF bbox 无效或越界: {list(rect)}')
    fingerprint = sources.fingerprint(source_path)
    identity = {'path': str(Path(source_path).resolve()), 'sha256': fingerprint,
                'page': page_number, 'bbox': list(rect), 'dpi': DPI, 'version': VERSION}
    token = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:24]
    png, pdf, metadata = [assets / f'{token}.{extension}' for extension in ('png', 'pdf', 'json')]
    if not dry_run:
        assets.mkdir(parents=True, exist_ok=True)
        reusable = False
        if metadata.exists() and png.exists() and pdf.exists():
            old = read_json(metadata)
            reusable = (old.get('identity') == identity and old.get('png_sha256') == sha_file(png)
                        and old.get('pdf_sha256') == sha_file(pdf))
        if not reusable:
            pix = page.get_pixmap(dpi=DPI, clip=rect, colorspace=fitz.csRGB, alpha=False)
            pix.save(png)
            with fitz.open() as clipped:
                target = clipped.new_page(width=rect.width, height=rect.height)
                target.show_pdf_page(target.rect, doc, page_number - 1, clip=rect)
                clipped.save(pdf, garbage=4, deflate=True)
            write_json(metadata, {'identity': identity, 'png_sha256': sha_file(png),
                                  'pdf_sha256': sha_file(pdf),
                                  'pixel_dimensions': [pix.width, pix.height]})
        saved = read_json(metadata)
    else:
        saved = {}
    return {**identity, 'png': str(png.relative_to(current)), 'pdf': str(pdf.relative_to(current)),
            'png_sha256': saved.get('png_sha256'), 'pdf_sha256': saved.get('pdf_sha256'),
            'pixel_dimensions': saved.get('pixel_dimensions'),
            'pdf_mode': 'original_pdf_objects_preserved', 'crop_visual_review': 'pending',
            **{key: crop[key] for key in ('parent_bbox', 'split_part', 'split_parts',
                                         'split_reason', 'needs_split') if key in crop}}


def load_examples(root, chapters):
    examples, inputs = [], []
    for path in sorted((root / 'chapters').glob('*/examples.json')):
        chapter = path.parent.name
        if chapters and chapter not in chapters:
            continue
        content = read_json(path)
        items = content if isinstance(content, list) else content.get('examples', [])
        if not isinstance(items, list):
            raise ValueError(f'examples 必须为列表: {path}')
        inputs.append(path)
        for item in items:
            if not isinstance(item, dict) or not item.get('id') or not item.get('question'):
                raise ValueError(f'例题缺少 id/question: {path}')
            examples.append((chapter, item))
    if not examples:
        raise ValueError('没有找到当前 examples.json 中的例题；未覆盖原索引')
    ids = [e['id'] for _, e in examples]
    if len(set(ids)) != len(ids):
        raise ValueError('例题 id 重复，不能建立一一对应索引')
    return examples, inputs


def prepare(args):
    root, analysis, project = args.current.resolve(), args.analysis.resolve(), args.project.resolve()
    if args.chapter and not args.output:
        raise ValueError('部分章节运行必须传 --output，避免覆盖完整 example_index.json')
    examples, example_inputs = load_examples(root, set(args.chapter))
    sources = Sources(analysis, project, args.verifications or root / 'sources/solution_source_verifications.json')
    records = []
    try:
        for chapter, example in examples:
            record = dict(example)
            record.setdefault('chapter', chapter)
            record.setdefault('subject', chapter[:2])
            record.update({'source': None, 'crops': [], 'solution_mode': 'native'})
            candidate, evidence, reason = sources.match(example, chapter[:2])
            record['match_reason'] = reason
            record['match_evidence'] = evidence
            if candidate:
                try:
                    segments = [segment for crop in candidate['answer_crops']
                                for segment in split_long_crop(sources, candidate['answer_path'], crop)]
                    crops = [export_crop(sources, candidate['answer_path'], segment,
                                         root / 'solutions/assets', root, args.dry_run)
                             for segment in segments]
                    source = {'id': candidate['id'], 'source_key': candidate['source_key'],
                              'manifest_group': candidate['group'],
                              'pdf': str(Path(candidate['answer_path']).resolve()),
                              'sha256': sources.fingerprint(candidate['answer_path']),
                              'question_pdf': str(Path(candidate['question_path']).resolve()),
                              'question_pdf_sha256': sources.fingerprint(candidate['question_path']),
                              'question_crops': candidate['question_crops'],
                              'answer_crops': candidate['answer_crops'],
                              **({'indexed_answer_crops': candidate['indexed_answer_crops']}
                                 if 'indexed_answer_crops' in candidate else {}),
                              'identity_verification': (evidence or {}).get(
                                  'identity_verification', 'normalized_full_question_equal'),
                              'source_visual_review': 'pending'}
                    record.update({'source': source, 'crops': crops,
                                   'solution_mode': 'original_screenshot'})
                except (OSError, ValueError, RuntimeError, IndexError, TypeError) as error:
                    record['match_reason'] += f'；原 PDF 导出未成功：{error}；保留原生解析'
            records.append(record)
            print(f"{example['id']}: {record['solution_mode']} — {record['match_reason']}", flush=True)
        counts = collections.Counter(record['solution_mode'] for record in records)
        result = {'schema_version': VERSION,
                  'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                  'scope': sorted(args.chapter) if args.chapter else 'all_current_examples',
                  'policy': '完整题干与原题一致后使用原 PDF 裁切；不以相似主题、旧底稿锚点或答案代替原题身份核验；未确认者保留作者原生解析。',
                  'source_crop_dpi': DPI, 'dry_run': args.dry_run,
                  'visual_review_status': 'pending_after_github_push',
                  'summary': {'examples': len(records), **dict(counts),
                              'crops_needing_manual_split': sum(c.get('needs_split', False)
                                  for record in records for c in record['crops'])},
                  'inputs': [{'path': str(path), 'sha256': sources.fingerprint(path)}
                             for path in dict.fromkeys(example_inputs + sources.inputs)],
                  'examples': records}
        output = args.output or root / 'sources/example_index.json'
        write_json(output, result)
        print(json.dumps({'output': str(output), **result['summary']}, ensure_ascii=False))
    finally:
        sources.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', type=Path, default=ROOT)
    parser.add_argument('--analysis', type=Path, default=ANALYSIS)
    parser.add_argument('--project', type=Path, default=PROJECT)
    parser.add_argument('--chapter', action='append', default=[])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verifications', type=Path, help='独立逐题核验台账；默认 current/sources/solution_source_verifications.json')
    parser.add_argument('--dry-run', action='store_true', help='仅匹配并写索引，不生成资产')
    prepare(parser.parse_args())


if __name__ == '__main__':
    main()
