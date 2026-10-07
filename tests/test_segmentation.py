import ast,hashlib,json,struct,unittest,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];REPORT=json.loads((R/'data/sam31-recorded.json').read_text())

class SegmentationTests(unittest.TestCase):
    def test_same_original_source_as_jev_video(self):
        self.assertEqual(hashlib.sha256((R/'assets/opening.mp4').read_bytes()).hexdigest(),REPORT['source_sha256'])
    def test_frame_sequence_and_source_order(self):
        rows=REPORT['frames'];self.assertEqual([r['frame'] for r in rows],list(range(56)))
        self.assertEqual(REPORT['fps'],8)
        self.assertEqual([r['source_frame'] for r in rows],sorted(r['source_frame'] for r in rows))
        for r in rows:
            self.assertAlmostEqual(r['source_second'],r['source_frame']/REPORT['source_fps'])
            self.assertGreater(r['mask_pixels'],0)
    def test_binary_masks_match_every_reported_pixel_count(self):
        with zipfile.ZipFile(R/'data/sam31-masks.npz') as z:
            with z.open('masks.npy') as f:
                self.assertEqual(f.read(6),b'\x93NUMPY');major,minor=f.read(2)
                fmt='<H' if major==1 else '<I';length=struct.unpack(fmt,f.read(struct.calcsize(fmt)))[0]
                header=ast.literal_eval(f.read(length).decode('latin1'));raw=f.read()
        self.assertEqual(header['shape'],(56,720,1280));self.assertEqual(header['descr'],'|u1');self.assertFalse(header['fortran_order'])
        size=720*1280;self.assertEqual(len(raw),56*size)
        self.assertEqual(raw.count(0)+raw.count(1),len(raw))
        for i,row in enumerate(REPORT['frames']):self.assertEqual(raw[i*size:(i+1)*size].count(1),row['mask_pixels'])
    def test_published_playback_hashes(self):
        for source,published in [('sampled.mp4','sam-source.mp4'),('overlay.mp4','sam-overlay.mp4'),('binary-mask.mp4','sam-binary.mp4')]:
            self.assertEqual(hashlib.sha256((R/'assets'/published).read_bytes()).hexdigest(),REPORT['visualization']['files'][source])

if __name__=='__main__':unittest.main()
