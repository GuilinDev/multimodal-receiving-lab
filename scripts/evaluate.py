"""Inspect recorded cases or evaluate them against a compatible local service."""
import argparse, hashlib, json, math, mimetypes, time, urllib.request, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def validate_response(response, options):
    probabilities=response['probabilities']
    if set(probabilities)!=set(options): raise ValueError('Response options differ from the question')
    values=[probabilities[o] for o in options]
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in values):
        raise ValueError('Invalid probability')
    if not math.isclose(sum(values),1,abs_tol=1e-5): raise ValueError('Probabilities do not sum to one')
    best=max(range(len(values)),key=values.__getitem__)
    if response.get('prediction')!=options[best]: raise ValueError('Prediction disagrees with scores')
    if 'confidence' in response and not math.isclose(response['confidence'],values[best],abs_tol=1e-5):
        raise ValueError('Confidence disagrees with top score')
    return response

def verify_case(case, assets=ROOT/'assets'):
    file=assets/case['file']
    if hashlib.sha256(file.read_bytes()).hexdigest()!=case['sha256']:
        raise ValueError(f"Evidence hash changed: {case['id']}")
    return file

def predict(base_url, payload, file):
    boundary=uuid.uuid4().hex
    body=(f'--{boundary}\r\nContent-Disposition: form-data; name="payload"\r\n\r\n'.encode()
          +json.dumps(payload).encode()
          +f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file.name}"\r\nContent-Type: {mimetypes.guess_type(file.name)[0] or "application/octet-stream"}\r\n\r\n'.encode()
          +file.read_bytes()+f'\r\n--{boundary}--\r\n'.encode())
    req=urllib.request.Request(base_url.rstrip('/')+'/predict',body,{'Content-Type':f'multipart/form-data; boundary={boundary}'})
    with urllib.request.urlopen(req,timeout=180) as r:return validate_response(json.load(r),payload['options'])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--recorded',action='store_true');mode.add_argument('--base-url')
    p.add_argument('--output',type=Path,default=ROOT/'runs/new-results.json');a=p.parse_args()
    if a.recorded:
        report=json.loads((ROOT/'data/recorded-results.json').read_text())
        for c in report['cases']:
            verify_case(c);validate_response(c['output'],c['payload']['options'])
            print(f"{c['id']}: {c['output']['prediction']} ({c['output']['confidence']:.1%})")
        return
    cases=json.loads((ROOT/'data/cases.json').read_text())
    for c in cases:verify_case(c)
    if a.output.exists():p.error('Output already exists; choose another filename to retain previous runs')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    report={'mode':'fresh service requests','cases':[]}
    for case in cases:
        start=time.perf_counter();row=dict(case)
        try:row['output']=predict(a.base_url,case['payload'],verify_case(case))
        except Exception as e:row['error']=f'{type(e).__name__}: {e}'
        row['wall_seconds']=time.perf_counter()-start
        report['cases'].append(row)
        a.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(case['id'],row.get('error',row.get('output',{}).get('prediction')))
    if any('error' in c for c in report['cases']):raise SystemExit(1)

if __name__=='__main__':main()
