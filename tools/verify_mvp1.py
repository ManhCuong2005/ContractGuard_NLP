"""Re-run reproducible technical verification; does not train an official model."""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    reports = ROOT/'reports'
    reports.mkdir(exist_ok=True)
    checks = {}
    commands = {
        'tests':[sys.executable, '-m', 'pytest', '-q', '--junitxml=reports/test-results.xml'],
        'dependencies':[sys.executable, '-m', 'pip', 'check'],
        'cli':[sys.executable, '-m', 'contractguard', '--help'],
        'prediction_script':[sys.executable, 'tools/predict.py', '--help'],
        'audit':[sys.executable, '-m', 'contractguard', 'audit', '--data', 'data/clauses.csv'],
        'readiness':[sys.executable, '-m', 'contractguard', 'readiness', '--output', 'reports/readiness.json'],
        'annotation_inspector':[sys.executable, 'tools/inspect_annotation.py', '--label', 'abnormal', '--count', '1'],
        'compile':[sys.executable, '-m', 'compileall', '-q', '-x', r'(^|[\\/])node_modules([\\/]|$)', 'src', 'tools'],
    }
    for name, command in commands.items():
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        checks[name] = {'returncode':result.returncode}
        (reports/(name+'.log')).write_text(result.stdout+result.stderr, encoding='utf-8')
        print(f'{name}: {"PASS" if result.returncode==0 else "FAIL"}')
        if result.returncode:
            print(result.stdout+result.stderr)
    suite = ET.parse(reports/'test-results.xml').find('testsuite')
    summary = {'purpose':'technical_verification_only', 'verified_at':datetime.now(timezone.utc).isoformat(),
               'checks':checks, 'tests':dict(suite.attrib) if suite is not None else {},
               'official_training_performed':False,
               'official_metrics':None,
               'notes':'Model save/reload, new input prediction and experiment engine tested on explicitly marked toy fixtures only. See tests.log.'}
    (reports/'verification.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return int(any(check['returncode'] for check in checks.values()))


if __name__ == '__main__':
    raise SystemExit(main())
