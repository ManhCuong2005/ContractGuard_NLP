"""Versioned public-source collection for the requested rental expansion. No label inference."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import threading
import time
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import zipfile
from xml.etree import ElementTree as ET

import requests

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,sha256,write_json
from rental_corpus import semantic_html,html_pages

BASE=ROOT/'data/rental_expansion_v2'
AGENT='ContractGuard-AcademicDataset/0.2'
LOCK=threading.Lock()
HOSTS={}


def discover():
    old={s['source_url'] for s in read_json(ROOT/'data/rental_mvp1a_v1/collection_manifest.json')}
    found={}
    rejected=[]
    for path in sorted((BASE/'discovery').glob('search_*.json')):
        if not re.fullmatch(r'search_\d+\.json',path.name):continue
        result=read_json(path)['result']
        for match in re.finditer(r'^([^\n]*)\((https://[^\n]+)\)\s*$',result,re.M):
            title,url=match.groups()
            host=urlsplit(url).netloc.lower()
            if any(x in host for x in ['scribd.','studocu.','reddit.','timvanban.']):
                rejected.append(dict(url=url,reason='Third-party upload / discussion / download aggregator; not selected as a primary source.'))
                continue
            if url in old or url in found:continue
            if not re.search(r'thuê|THUÊ|THUE|hop.dong|HỢP ĐỒNG|noi.tru|NỘI TRÚ|noi.quy|nội quy|ky.tuc',title+' '+url,re.I):
                rejected.append(dict(url=url,reason='Search result not a rental contract/rules candidate.'))
                continue
            fmt='pdf' if re.search(r'\.pdf(?:[?#]|$)',url,re.I) else ('docx' if re.search(r'\.docx(?:[?#]|$)',url,re.I) else 'html')
            sid='v2_'+re.sub('[^a-z0-9]+','_',host.removeprefix('www.')).strip('_')[:38]+'_'+hashlib.sha256(url.encode()).hexdigest()[:8]
            found[url]=dict(document_id=sid,url=url,title=title.strip(),format=fmt,discovered_in=path.relative_to(ROOT).as_posix())
    write_json(BASE/'discovery/source_queue.json',list(found.values()))
    write_json(BASE/'discovery/search_rejections.json',rejected)
    print('New URL candidates',len(found),'deferred search results',len(rejected))


def host_state(url):
    host=urlsplit(url).netloc
    with LOCK:
        if host not in HOSTS:HOSTS[host]={'lock':threading.Lock(),'robots':None,'last':0}
        return HOSTS[host]


def get_public(url):
    if urlsplit(url).scheme!='https':raise ValueError('Only public HTTPS URLs')
    state=host_state(url)
    with state['lock']:
        if state['robots'] is None:
            robots_url='https://'+urlsplit(url).netloc+'/robots.txt'
            try:
                response=requests.get(robots_url,timeout=(8,15),headers={'User-Agent':AGENT})
                robot=RobotFileParser()
                if response.status_code==200:
                    robot.parse(response.text.splitlines())
                    state['robots']=(robot,'parsed_200')
                else:state['robots']=(None,'http_'+str(response.status_code))
            except requests.RequestException as exc:
                state['robots']=(None,type(exc).__name__)
        robot,status=state['robots']
        if robot and not robot.can_fetch(AGENT,url):raise ValueError('Disallowed by robots.txt')
        time.sleep(max(0,.6-(time.monotonic()-state['last'])))
        response=requests.get(url,timeout=(12,40),headers={'User-Agent':AGENT},stream=True)
        response.raise_for_status()
        chunks=[]
        size=0
        for chunk in response.iter_content(65536):
            size+=len(chunk)
            if size>40_000_000:
                response.close()
                raise ValueError('More than 40 MB; inspect before collection')
            chunks.append(chunk)
        state['last']=time.monotonic()
        return b''.join(chunks),response.url,response.headers.get('Content-Type',''),status


def fetch_one(spec):
    folder=BASE/'raw'/spec['document_id']
    manifest=folder/'source.json'
    if manifest.exists():
        source=read_json(manifest)
        assert source['source_url']==spec['url'] and sha256(ROOT/source['raw_path'])==source['source_sha256']
        return source
    raw,resolved,content_type,robots_status=get_public(spec['url'])
    fmt=spec['format']
    if raw.startswith(b'%PDF'):fmt='pdf'
    elif raw.startswith(b'PK') and ('docx' in spec['url'] or 'wordprocessingml' in content_type):fmt='docx'
    links=[]
    if fmt=='pdf':
        import pdfplumber
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            pages=[p.extract_text(x_tolerance=2,y_tolerance=3) or '' for p in pdf.pages]
        method='pdfplumber_geometry_2_3'
        selector=None
    elif fmt=='docx':
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            xml=ET.fromstring(archive.read('word/document.xml'))
            ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            pages=['\n'.join(''.join(t.text or '' for t in p.iter(ns+'t')) for p in xml.iter(ns+'p'))]
        method='ooxml_ordered_paragraphs'
        selector=None
    else:
        _,links,_=html_pages(raw)
        pages,selector=semantic_html(raw)
        method='semantic_dom_paragraphs_v2'
    folder.mkdir(parents=True,exist_ok=True)
    original=folder/('original.'+fmt)
    if original.exists():raise ValueError('Partial source exists; inspect, do not overwrite')
    original.write_bytes(raw)
    write_json(folder/'pages.json',pages)
    write_json(folder/'links.json',[{**link,'url':urljoin(resolved,link['href'])} for link in links])
    source=dict(document_id=spec['document_id'],title=spec['title'],source_url=spec['url'],resolved_url=resolved,
        format=fmt,data_kind='public_rental_source_candidate',source_use_status='pending_dataset_and_source_review',
        raw_path=original.relative_to(ROOT).as_posix(),source_sha256=sha256(original),
        pages_path=(folder/'pages.json').relative_to(ROOT).as_posix(),pages_sha256=sha256(folder/'pages.json'),
        page_count=len(pages),extractor=method,html_selector=selector,content_type=content_type,
        retrieved_at=datetime.now(timezone.utc).isoformat(),robots_check=robots_status,
        requires_visual_transcription=not any(p.strip() for p in pages),
        notes='Discovery candidate only. Need agent scope, text, role, family, context, license and label review. No approval inferred.')
    write_json(manifest,source)
    return source


def fetch(queue):
    specs=read_json(queue)
    successes=[]
    failures=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        work={pool.submit(fetch_one,s):s for s in specs}
        for future in as_completed(work):
            spec=work[future]
            try:
                result=future.result()
                successes.append(result)
                print(result['document_id'],result['page_count'],'pages',flush=True)
            except Exception as exc:
                failures.append(dict(**spec,error=type(exc).__name__+': '+str(exc)))
                print(spec['document_id'],'unavailable',type(exc).__name__,flush=True)
    known={s['document_id']:s for s in read_json(BASE/'collection_manifest.json')} if (BASE/'collection_manifest.json').exists() else {}
    known.update({s['document_id']:s for s in successes})
    write_json(BASE/'collection_manifest.json',list(known.values()))
    receipt=dict(queue=str(queue),successes=[s['document_id'] for s in successes],failures=failures,recorded_at=datetime.now(timezone.utc).isoformat())
    write_json(BASE/'collection_runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'),receipt)
    print('Batch',len(successes),'archived;',len(failures),'unavailable; total',len(known),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['discover','fetch'])
    p.add_argument('--queue',type=Path,default=BASE/'discovery/source_queue.json')
    args=p.parse_args()
    if args.command=='discover':discover()
    else:fetch(args.queue)


if __name__=='__main__':main()
