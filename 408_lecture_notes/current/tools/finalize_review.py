#!/usr/bin/env python3
"""Bind final books to actual page reviews and proven unchanged page renderings."""
import argparse, hashlib
import fitz
from build_notes import ROOT, read, jwrite, sha

REV = ROOT/'sources/reviews'
NOTES = 'books/408四科_强化笔记.pdf'
SOLUTIONS = 'books/408强化例题解析.pdf'

def raster_rows(path):
    with fitz.open(path) as doc:
        rows=[]
        for i,p in enumerate(doc,1):
            w,h=p.rect.width,p.rect.height
            signature=[hashlib.sha256(p.get_pixmap(matrix=fitz.Matrix(1.45,1.45),clip=fitz.Rect(rect),alpha=False).samples).hexdigest()
                       for rect in [(0,0,w,27),(0,27,502,57),(538,27,w,57),(0,57,w,h)]]
            rows.append({'page':i,'sha256':hashlib.sha256(p.get_pixmap(matrix=fitz.Matrix(1.45,1.45),alpha=False).samples).hexdigest(),'content_signature':signature})
        return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--finalize',action='store_true');args=ap.parse_args()
    frozen=read(REV/'round2_full_page_signatures.json')
    comparison=read(REV/'round2_page_comparison.json')
    repaired=read(REV/'layout_notes_round2.json')
    old_notes=read(REV/'round1_page_signatures.json')['notes']
    assert comparison['previous_pdf_sha256']==old_notes['pdf_sha256']
    assert comparison['current_pdf_sha256']==repaired['pdf_sha256']==frozen['408四科_强化笔记.pdf']['pdf_sha256']
    assert repaired['status']=='passed'
    clean_old=set()
    for name in ['DS','CO','OS','CN']:
        record=read(REV/f'layout_{name}.json')
        assert record['pdf_sha256']==old_notes['pdf_sha256']
        clean_old.update(record['viewed_pages'])
    clean_old.difference_update(comparison['excluded_previous_issue_pages'])
    note_proof={}
    for row in comparison['pages']:
        if row['page'] in repaired['viewed_pages']:
            note_proof[row['page']]={'method':'full_page_visual_review','review':'sources/reviews/layout_notes_round2.json'}
        else:
            matches=[p for p in row['equivalent_reviewed_round1_pages'] if p in clean_old]
            if matches:note_proof[row['page']]={'method':'unchanged_rendering_from_reviewed_page','previous_pages':matches,'review':'sources/reviews/round2_page_comparison.json','folio_check':'sources/book_checks.json'}
    front=read(REV/'layout_solutions_round2_front.json')
    assert front['pdf_sha256']==frozen['408强化例题解析.pdf']['pdf_sha256']
    # The five quick-reference pages had reported issues and receive a fresh review.
    clean_front=set(front['viewed_pages'])-set(range(1,6))
    round3=read(REV/'round3_solutions_signatures.json')
    round2_pixels={r['page']:r['sha256'] for r in frozen['408强化例题解析.pdf']['pages']}
    reviewed_round3={}
    for row in round3['pages']:
        if row['page'] in clean_front and row['sha256']==round2_pixels.get(row['page']):
            reviewed_round3[row['page']]={'review':'sources/reviews/layout_solutions_round2_front.json','method':'exact_full_page_rendering_matches_reviewed_page','previous_pdf_sha256':front['pdf_sha256'],'previous_page':row['page']}
    for name in ['layout_solutions_final_front.json','layout_solutions_final_tail.json']:
        record=read(REV/name)
        assert record['pdf_sha256']==round3['pdf_sha256']
        issues={f['page'] for f in record.get('findings',[]) if 'page' in f}
        for page in set(record['viewed_pages'])-issues:
            reviewed_round3[page]={'review':'sources/reviews/'+name,'method':'full_page_visual_review','previous_pdf_sha256':record['pdf_sha256'],'previous_page':page}
    # The short-code split on these pages was recorded separately.
    for page in [27,28,32]:reviewed_round3.pop(page,None)
    books=[];pending=[]
    for file in [NOTES,SOLUTIONS]:
        path=ROOT/file;fingerprint=sha(path);rows=raster_rows(path)
        previous={r['page']:r['sha256'] for r in frozen[path.name]['pages']}
        direct={}
        if file==SOLUTIONS:
            for name in ['layout_solutions_last_changes.json']:
                report_path=REV/name
                if not report_path.exists():continue
                report=read(report_path)
                if report.get('status')=='passed' and report['pdf_sha256']==fingerprint:
                    direct.update({p:'sources/reviews/'+name for p in report['viewed_pages']})
        proofs=[]
        for row in rows:
            page=row['page'];proof=None
            if file==NOTES and row['sha256']==previous.get(page):proof=note_proof.get(page)
            elif file==SOLUTIONS:
                if page in direct:proof={'method':'full_page_visual_review','review':direct[page]}
                else:
                    matches=[r for r in round3['pages'] if r['page'] in reviewed_round3 and r['content_signature']==row['content_signature']]
                    if matches:
                        old=matches[0];proof={'method':'exact_rendering_matches_reviewed_page_except_verified_folio','previous_page':old['page'],'previous_pdf_sha256':round3['pdf_sha256'],'review_chain':reviewed_round3[old['page']],'folio_check':'sources/book_checks.json'}
            if proof:proofs.append({**row,**proof})
            else:pending.append({'file':file,'page':page})
        books.append({'file':file,'pdf_sha256':fingerprint,'pages':len(rows),'covered_pages':len(proofs),'page_evidence':proofs})
    checks=read(ROOT/'sources/book_checks.json');machine=read(ROOT/'sources/final_layout_checks.json')
    navigation=read(ROOT/'sources/navigation_exact_checks.json')
    errors=list(checks['errors'])+machine['compile_warnings']+navigation['errors']
    if navigation['navigation_sha256']!=sha(ROOT/'sources/navigation.json'):errors.append('Stale navigation index check')
    for book in navigation['pdfs']:
        if sha(ROOT/book['file'])!=book['sha256']:errors.append('Stale exact-navigation check: '+book['file'])
    for book in machine['books']:
        if sha(ROOT/book['file'])!=book['pdf_sha256']:errors.append('Stale machine check: '+book['file'])
        errors.extend(book['issues'])
    for book in checks['books']:
        if sha(ROOT/book['file'])!=book['sha256']:errors.append('Stale book check: '+book['file'])
    result={'status':'passed' if not pending and not errors else 'incomplete','github_pre_layout':read(ROOT/'sources/github_pre_layout.json'),
            'method':'Actual full-page reviews plus explicit exact-raster equivalence for unchanged pages; folios and four subject copies checked independently.',
            'books':books,'subject_books':checks['page_equivalence'],'pending_pages':pending,'errors':errors,
            'scope':'Final delivered page layouts and displayed source crops. Source identities are verified separately; whole original source pages are not all visually reviewed.'}
    jwrite(ROOT/'sources/reviews/final_page_coverage.json',result)
    print({'status':result['status'],'pending_pages':pending,'errors':errors})
    if args.finalize:
        if pending or errors:raise SystemExit('Final visual coverage is incomplete.')
        index=read(ROOT/'sources/example_index.json')
        index['visual_review_status']='passed_for_exported_answer_crops_in_final_book'
        index['visual_review_reference']='sources/visual_review.json'
        index['visual_review_pdf_sha256']=sha(ROOT/SOLUTIONS)
        for example in index['examples']:
            if example.get('source'):
                example['source']['source_visual_review']='answer_crops_reviewed_in_final_book; whole_original_page_review_not_claimed'
            for crop in example['crops']:crop['crop_visual_review']='passed_in_final_solution_book'
        jwrite(ROOT/'sources/example_index.json',index)
        result['source_index_sha256']=sha(ROOT/'sources/example_index.json')
        result['displayed_source_crops']=sum(len(e['crops']) for e in index['examples'])
        jwrite(ROOT/'sources/visual_review.json',result)
        machine['visual_review']='passed';machine['visual_review_reference']='sources/visual_review.json'
        jwrite(ROOT/'sources/final_layout_checks.json',machine)

if __name__=='__main__':main()
