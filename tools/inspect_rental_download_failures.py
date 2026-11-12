"""Archive two parse-failure responses for inspection; do not bypass access blocks."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,sha256,write_json
from rental_expansion_v2 import get_public


def main():
    base=ROOT/'data/rental_expansion_v2'
    selected={'v2_attachment_78ad147c475a','v2_public_upload_845798279'}
    failed={x['document_id']:x for p in (base/'collection_runs').glob('*.json') for x in read_json(p)['failures'] if x['document_id'] in selected}
    records=[]
    for sid,spec in failed.items():
        folder=base/'unparsed_responses'/sid
        output=folder/'response.bin'
        metadata=folder/'response.json'
        if output.exists():
            record=read_json(metadata)
        else:
            try:raw,url,kind,robots=get_public(spec['url'])
            except Exception as exc:
                print(sid,type(exc).__name__,str(exc)[:100])
                continue
            folder.mkdir(parents=True,exist_ok=True)
            output.write_bytes(raw)
            record=dict(document_id=sid,source_url=spec['url'],resolved_url=url,content_type=kind,
                robots_check=robots,raw_path=output.relative_to(ROOT).as_posix(),sha256=sha256(output),
                bytes=len(raw),original_error=spec['error'],status='needs_agent_response_inspection_not_a_labeled_source')
            write_json(metadata,record)
        records.append(record)
        print(sid,record['content_type'],record['bytes'],repr(output.read_bytes()[:45]))
    write_json(base/'unparsed_responses/inspection_manifest.json',records)


if __name__=='__main__':main()
