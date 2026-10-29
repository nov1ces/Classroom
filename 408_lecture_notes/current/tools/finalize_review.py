#!/usr/bin/env python3
"""Validate current page-review coverage, PDF identities, and release checks."""
import argparse
from pathlib import Path
import fitz
from build_notes import ROOT, read, jwrite, sha

NOTES='books/408四科_强化笔记.pdf'
SOLUTIONS='books/408强化例题解析.pdf'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--finalize',action='store_true')
    parser.add_argument('--review-dir',type=Path,default=ROOT/'sources/reviews/current')
    args=parser.parse_args()
    errors=[];books=[];reports=[]
    for path in sorted(args.review_dir.glob('*.json')):
        report=read(path)
        if report.get('status')=='passed' and report.get('pdf_sha256'):reports.append((path,report))
    for file in [NOTES,SOLUTIONS]:
        fingerprint=sha(ROOT/file)
        with fitz.open(ROOT/file) as doc:pages=len(doc)
        evidence={}
        for path,report in reports:
            if report['pdf_sha256']!=fingerprint:continue
            for page in report.get('viewed_pages',[]):
                if not isinstance(page,int) or not 1<=page<=pages:errors.append(f'{path.name}: invalid reviewed page {page}')
                else:evidence[page]=str(path.relative_to(ROOT))
        missing=sorted(set(range(1,pages+1))-set(evidence))
        books.append({'file':file,'pdf_sha256':fingerprint,'pages':pages,'covered_pages':len(evidence),'missing_pages':missing,
                      'page_evidence':[{'page':p,'review':evidence[p],'method':'full_page_visual_review'} for p in sorted(evidence)]})
    machine=read(ROOT/'sources/final_layout_checks.json');checks=read(ROOT/'sources/book_checks.json');navigation=read(ROOT/'sources/navigation_exact_checks.json')
    errors.extend(machine['compile_warnings']);errors.extend(checks['errors']);errors.extend(navigation['errors'])
    if navigation['navigation_sha256']!=sha(ROOT/'sources/navigation.json'):errors.append('Stale navigation index check')
    for records,key in [(machine['books'],'pdf_sha256'),(checks['books'],'sha256'),(navigation['pdfs'],'sha256')]:
        for book in records:
            if sha(ROOT/book['file'])!=book[key]:errors.append('Stale PDF check: '+book['file'])
    for book in machine['books']:errors.extend(book['issues'])
    integrity=read(ROOT/'sources/text_integrity_checks.json');errors.extend(integrity['errors'])
    for book in integrity['inputs']:
        if sha(ROOT/book['file'])!=book['sha256']:errors.append('Stale text integrity check: '+book['file'])
    pending=[{'file':b['file'],'page':p} for b in books for p in b['missing_pages']]
    result={'status':'passed' if not pending and not errors else 'incomplete','github_pre_layout':read(ROOT/'sources/github_pre_layout.json'),
            'books':books,'subject_books':checks['page_equivalence'],'pending_pages':pending,'errors':errors,
            'scope':'Final delivered page layouts and displayed answer crops; source identity checks are recorded separately.'}
    jwrite(ROOT/'sources/reviews/final_page_coverage.json',result)
    print({'status':result['status'],'pending_pages':pending,'errors':errors})
    if args.finalize:
        if pending or errors:raise SystemExit('Page review is incomplete.')
        index=read(ROOT/'sources/example_index.json');index['visual_review_status']='passed_for_exported_answer_crops_in_final_book'
        index['visual_review_reference']='sources/visual_review.json';index['visual_review_pdf_sha256']=sha(ROOT/SOLUTIONS)
        for example in index['examples']:
            if example.get('source'):example['source']['source_visual_review']='answer_crops_reviewed_in_final_book; whole_original_page_review_not_claimed'
            for crop in example['crops']:crop['crop_visual_review']='passed_in_final_solution_book'
        jwrite(ROOT/'sources/example_index.json',index)
        result['source_index_sha256']=sha(ROOT/'sources/example_index.json');result['displayed_source_crops']=sum(len(e['crops']) for e in index['examples'])
        jwrite(ROOT/'sources/visual_review.json',result)
        machine['visual_review']='passed';machine['visual_review_reference']='sources/visual_review.json';jwrite(ROOT/'sources/final_layout_checks.json',machine)

if __name__=='__main__':main()
