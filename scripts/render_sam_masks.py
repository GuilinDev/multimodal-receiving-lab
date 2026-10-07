"""Render measured binary masks, their contours and an unpainted ROI clip."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import cv2,numpy as np

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);a=p.parse_args();d=a.folder
    report=json.loads((d/'result.json').read_text());masks=np.load(d/'masks.npz')['masks'];fps=report['fps'];h,w=masks.shape[1:]
    union=masks.any(axis=0);ys,xs=np.where(union)
    if not len(xs):raise RuntimeError('No object masks to visualize')
    margin=32;x0=max(0,int(xs.min())-margin);y0=max(0,int(ys.min())-margin);x1=min(w,int(xs.max())+1+margin);y1=min(h,int(ys.max())+1+margin)
    # One fixed rectangle across the sequence preserves motion and some surrounding context.
    processes={}
    for name in ['sampled','overlay','binary-mask','roi']:
        processes[name]=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','fast','-movflags','+faststart',str(d/f'{name}.mp4')],stdin=subprocess.PIPE)
    crop_dir=d/'roi-frames';crop_dir.mkdir(exist_ok=True)
    for i,mask in enumerate(masks):
        img=cv2.imread(str(d/'frames'/f'{i:05d}.jpg'));m=mask.astype(bool);painted=img.copy()
        painted[m]=(img[m]*.52+np.array([240,145,25])*.48).astype('uint8')
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(painted,contours,-1,(255,183,55),2)
        binary=np.repeat((mask*255)[:,:,None],3,axis=2)
        crop=img[y0:y1,x0:x1];rh,rw=crop.shape[:2];scale=min(w/rw,h/rh)
        resized=cv2.resize(crop,(round(rw*scale),round(rh*scale)));roi=np.full_like(img,(36,27,20));dy=(h-resized.shape[0])//2;dx=(w-resized.shape[1])//2;roi[dy:dy+resized.shape[0],dx:dx+resized.shape[1]]=resized
        for name,frame in [('sampled',img),('overlay',painted),('binary-mask',binary),('roi',roi)]:processes[name].stdin.write(frame.tobytes())
        if i in [0,16,32,48,55]:
            cv2.imwrite(str(d/f'overlay-{i:03d}.jpg'),painted);cv2.imwrite(str(d/f'roi-{i:03d}.jpg'),roi)
    for proc in processes.values():
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('ffmpeg encoding failed')
    report['visualization']={'mask_alpha':.48,'bgr':[240,145,25],'contours':'binary mask external boundaries','roi_xyxy':[x0,y0,x1,y1],'roi_method':'fixed union bounding rectangle over all masks, 32px padding, original RGB content, aspect-preserving letterbox to source size','mask_used_for_jev':'only rectangle coordinates; no colored overlay sent to Jev','files':{name+'.mp4':hashlib.sha256((d/f'{name}.mp4').read_bytes()).hexdigest() for name in processes}}
    (d/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps({'frames':len(masks),'roi':report['visualization']['roi_xyxy'],'seconds':report['processing_seconds']}),flush=True)

if __name__=='__main__':main()
