"""Prepare an explicit assembler fork and geometry repair; preserve v1 and initial v2 outputs."""
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,sha256,write_json


def main():
    base=ROOT/'data/rental_expansion_v2'
    history=base/'extraction_history/initial_pool'
    history.mkdir(parents=True,exist_ok=True)
    for name in ['candidates.json','candidate_sources.json','candidate_coverage.json','candidate_snapshot.json']:
        path=base/name
        saved=history/name
        if path.exists() and not saved.exists():shutil.copyfile(path,saved)
    source=ROOT/'tools/build_rental_candidates.py'
    code=source.read_text('utf-8')
    replacements={
        "if not value or re.fullmatch(r'\\d+', value)": "if not normalize(value) or re.fullmatch(r'\\d+', value)",
        "if pdf_lines and ((pending_text.endswith(':') and len(pending_text)<220) or role_intro):":
        "if ((pending_text.endswith(':') and len(pending_text)<220) or role_intro):",
    }
    for before,after in replacements.items():
        assert code.count(before)==1,before
        code=code.replace(before,after)
    target=ROOT/'tools/rental_clause_assembly_v2.py'
    content='# Explicit v2 fork: preserve role introductions in every format and skip invisible-only lines.\n'+code
    if not target.exists():target.write_text(content,encoding='utf-8')
    else:assert target.read_text('utf-8')==content
    import pdfplumber
    old=next(s for s in read_json(ROOT/'data/rental_mvp1a_v1/collection_manifest.json') if s['document_id']=='bdsdaily_house_pdf')
    output=base/'source_repairs/bdsdaily_house_pdf/pages_geometry_v2.json'
    if not output.exists():
        with pdfplumber.open(ROOT/old['raw_path']) as pdf:
            pages=[p.extract_text(x_tolerance=2,y_tolerance=3) or '' for p in pdf.pages]
        write_json(output,pages)
    write_json(base/'source_repairs/repair_manifest.json',{
        'source_raw_sha256':old['source_sha256'],'original_pages_path':old['pages_path'],
        'repaired_pages_path':output.relative_to(ROOT).as_posix(),'repaired_pages_sha256':sha256(output),
        'repair':'PDF geometry extraction to restore wrapped word layout; no content paraphrase.',
        'assembler_fork_sha256':sha256(target),'original_assembler_sha256':sha256(source),
        'initial_pool_archived':True,'labels_assigned_by_this_operation':0})
    print('Assembler fork prepared and PDF geometry repaired; initial pool preserved.')


if __name__=='__main__':main()
