"""Run one case directly on CUDA using the pinned upstream helper and SDPA."""
import argparse, importlib.util, json, time
from pathlib import Path
from evaluate import ROOT, verify_case, validate_response
MODEL='akhilaaa3/Jev-Omni'
REVISION='5addda86ddee081a68fb067477ea100c221b8917'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',default='context-arrival')
    p.add_argument('--model-dir',type=Path,default=ROOT/'models/jev-omni')
    p.add_argument('--output',type=Path,default=ROOT/'runs/gpu-result.json')
    p.add_argument('--download',action='store_true',help='Download the pinned checkpoint and helper; large GPU model')
    args=p.parse_args()
    if args.output.exists():p.error('Output exists; choose a new filename')
    cases=json.loads((ROOT/'data/cases.json').read_text())
    case=next((c for c in cases if c['id']==args.case),None)
    if case is None:p.error('Unknown case: '+args.case)
    file=verify_case(case)
    import torch, transformers
    if not torch.cuda.is_available():raise RuntimeError('A CUDA-enabled PyTorch build and GPU are required')
    if args.download:
        from huggingface_hub import snapshot_download
        snapshot_download(MODEL,revision=REVISION,local_dir=args.model_dir,allow_patterns=['*.json','*.jinja','model*.safetensors*','head.pt','jev_omni.py','LICENSE*','NOTICE*'])
        (args.model_dir/'lab-revision.txt').write_text(REVISION)
    stamp=args.model_dir/'lab-revision.txt'
    if not stamp.exists() or stamp.read_text().strip()!=REVISION:
        raise RuntimeError('Use --download to prepare the pinned checkpoint')
    spec=importlib.util.spec_from_file_location('jev_upstream',args.model_dir/'jev_omni.py')
    upstream=importlib.util.module_from_spec(spec);spec.loader.exec_module(upstream)
    config=transformers.AutoConfig.from_pretrained(args.model_dir,local_files_only=True,trust_remote_code=False)
    if config.architectures!=['Gemma4UnifiedForConditionalGeneration']:raise RuntimeError('Unexpected architecture')
    torch.set_num_threads(8)
    model=transformers.Gemma4UnifiedForConditionalGeneration.from_pretrained(args.model_dir,dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa',local_files_only=True,trust_remote_code=False).eval()
    decision=json.loads((args.model_dir/'decision_config.json').read_text())
    head=upstream._Head256(decision['hidden_size']).to('cuda').eval()
    head.load_state_dict(torch.load(args.model_dir/'head.pt',map_location='cuda',weights_only=True))
    _,decoder=upstream._find_backbone(model)
    processor=transformers.AutoProcessor.from_pretrained(args.model_dir,local_files_only=True,trust_remote_code=False)
    engine=upstream.JevOmni(model,head,processor,decoder)
    request=dict(case['payload']);request.pop('video_frames',None) # Pinned helper samples 16 by default.
    torch.cuda.synchronize();start=time.perf_counter()
    output=engine.predict(**request,media=str(file))
    torch.cuda.synchronize();elapsed=(time.perf_counter()-start)*1000
    validate_response(output,case['payload']['options'])
    report={'model':MODEL,'revision':REVISION,'case':case,'output':output,'elapsed_ms':elapsed,'timing_scope':'preprocessing + GPU inference, excluding load and upload'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(output,indent=2))

if __name__=='__main__':main()
