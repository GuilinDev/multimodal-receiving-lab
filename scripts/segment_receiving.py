"""Run real SAM 3.1 video segmentation and preserve masks and source indices."""
import argparse, functools, hashlib, inspect, json, subprocess, sys, time
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sam-repo',type=Path,required=True);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--prompt',default='cardboard box');p.add_argument('--fps',type=int,default=8)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(a.sam_repo))
    import cv2,numpy as np,torch
    from sam3.model_builder import build_sam3_multiplex_video_predictor
    torch.set_num_threads(8)
    frame_dir=a.output/'frames';frame_dir.mkdir(exist_ok=True)
    cap=cv2.VideoCapture(str(a.input));source_fps=cap.get(cv2.CAP_PROP_FPS);n=0;kept=[]
    while True:
        ok,frame=cap.read()
        if not ok:break
        if n>=len(kept)*source_fps/a.fps:
            cv2.imwrite(str(frame_dir/f'{len(kept):05d}.jpg'),frame)
            kept.append({'source_frame':n,'source_second':n/source_fps})
        n+=1
    cap.release()
    if not kept:raise RuntimeError('No decoded frames')
    model=build_sam3_multiplex_video_predictor(checkpoint_path=str(a.checkpoint),bpe_path=str(a.sam_repo/'sam3/assets/bpe_simple_vocab_16e6.txt.gz'),use_fa3=False,compile=False,warm_up=False,async_loading_frames=False)
    original=model.model.init_state;names=set(inspect.signature(original).parameters)
    @functools.wraps(original)
    def compatible_init_state(*args,**kwargs):return original(*args,**{k:v for k,v in kwargs.items() if k in names})
    model.model.init_state=compatible_init_state
    torch.cuda.synchronize();start=time.perf_counter()
    sid=model.handle_request(dict(type='start_session',resource_path=str(frame_dir)))['session_id']
    model.handle_request(dict(type='add_prompt',session_id=sid,frame_index=0,text=a.prompt))
    records=[];masks_by_frame={};objects_by_frame={}
    for item in model.handle_stream_request(dict(type='propagate_in_video',session_id=sid,propagation_direction='forward',start_frame_index=0)):
        idx=int(item['frame_index']);o=item['outputs'];masks=np.asarray(o['out_binary_masks']);ids=np.asarray(o['out_obj_ids'])
        frame=cv2.imread(str(frame_dir/f'{idx:05d}.jpg'));h,w=frame.shape[:2]
        union=masks.any(axis=0).astype('uint8').squeeze() if len(masks) else np.zeros((h,w),np.uint8)
        masks_by_frame[idx]=union;objects_by_frame[idx]=masks
        ys,xs=np.where(union)
        box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
        records.append({'frame':idx,'time':idx/a.fps,**kept[idx],'object_ids':ids.tolist(),'mask_pixels':int(union.sum()),'bbox':box})
        if idx%16==0:print('FRAME',idx,'objects',len(ids),'mask_pixels',int(union.sum()),flush=True)
    torch.cuda.synchronize();elapsed=time.perf_counter()-start
    model.handle_request(dict(type='close_session',session_id=sid))
    if sorted(masks_by_frame)!=list(range(len(kept))):raise RuntimeError('Incomplete mask sequence')
    masks=np.stack([masks_by_frame[i] for i in range(len(kept))]);np.savez_compressed(a.output/'masks.npz',masks=masks)
    np.savez_compressed(a.output/'instance-masks.npz',**{f'frame_{i:05d}':v for i,v in objects_by_frame.items()})
    record={'model':'facebook/sam3.1','checkpoint_revision':a.checkpoint.parent.name,'sam_code_revision':subprocess.check_output(['git','-C',str(a.sam_repo),'rev-parse','HEAD'],text=True).strip(),'prompt':a.prompt,'source_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'source_fps':source_fps,'source_decoded_frames':n,'fps':a.fps,'width':w,'height':h,'processing_seconds':elapsed,'timing_scope':'session initialization, prompt and propagation; excludes model load, rendering and Jev inference','torch':torch.__version__,'frames':sorted(records,key=lambda r:r['frame'])}
    (a.output/'result.json').write_text(json.dumps(record,indent=2))
    print('DONE',len(kept),'frames',round(elapsed,2),'seconds',flush=True)

if __name__=='__main__':main()
