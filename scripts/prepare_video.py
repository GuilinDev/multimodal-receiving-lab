"""Fetch source footage, verify its hashes, and prepare the editable film assets."""
import hashlib,json,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'downloads';A=R/'video/assets/inventory';B=R/'video/assets/audio'
def ff(*args):subprocess.run(['ffmpeg','-y','-v','error',*map(str,args)],check=True)
def main():
    if not shutil.which('ffmpeg') or not shutil.which('curl'):raise SystemExit('Install FFmpeg and curl first.')
    gsap=R/'video/node_modules/gsap/dist/gsap.min.js'
    if not gsap.exists():raise SystemExit('First run npm install from the video directory')
    for p in [D,A,B]:p.mkdir(parents=True,exist_ok=True)
    sources=json.loads((R/'data/sources.json').read_text())['sources']
    for s in sources:
        id=s['id'];f=D/f'{id}.mp4'
        if not f.exists():
            quality='hd_1920_1080' if id=='4440949' else 'uhd_3840_2160'
            url=f'https://videos.pexels.com/video-files/{id}/{id}-{quality}_25fps.mp4'
            temp=f.with_suffix('.partial')
            subprocess.run(['curl','-L','--fail','--retry','2','--output',str(temp),url],check=True)
            if hashlib.sha256(temp.read_bytes()).hexdigest()!=s['sha256']:
                raise RuntimeError(f'Source changed: {id}. Partial download retained for inspection.')
            temp.replace(f)
        if hashlib.sha256(f.read_bytes()).hexdigest()!=s['sha256']:raise RuntimeError('Hash mismatch: '+id)
    for id,name,start,dur,vf in [
        ('7287316','label-scan',0,8,'scale=1280:720'),
        ('7835166','delivery',0,8,'scale=1280:720'),
        ('7855154','label-macro',8,3,'crop=2000:1124:1000:560,scale=1280:720')]:
        ff('-ss',start,'-i',D/f'{id}.mp4','-t',dur,'-an','-vf',vf,'-r',25,'-c:v','libx264','-crf',18,'-preset','fast','-movflags','+faststart',A/f'{name}.mp4')
    for name in ['open.jpg','closed.jpg','restricted.jpg','opening.mp4']:shutil.copy2(R/'assets'/name,A/name)
    ff('-ss',1.5,'-i',A/'label-macro.mp4','-frames:v',1,'-pix_fmt','yuvj420p',A/'label-macro.jpg')
    for j,t in enumerate([0,1.84,3.68,5.56,6.8]):
        ff('-ss',t,'-i',A/'opening.mp4','-frames:v',1,'-pix_fmt','yuvj420p',A/f'frame-{j}.jpg')
    ff('-i',R/'assets/narration-en.mp3','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000',B/'inventory-v3.wav')
    shutil.copy2(gsap,R/'video/assets/gsap.min.js')
    print('Video assets prepared. Run npm run check from the video directory.')
if __name__=='__main__':main()
