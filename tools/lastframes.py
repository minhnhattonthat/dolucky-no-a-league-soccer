"""For a dir of fNNNNNN.png shots, find frames right before a text box region is cleared (ink count drops by >60%)
and paste them into one sheet:  python -X utf8 tools/lastframes.py DIR OUT.png [--box x,y,w,h]"""
import glob, os, sys
from PIL import Image

d, out = sys.argv[1], sys.argv[2]
box = (0, 136, 256, 56)
if '--box' in sys.argv:
    box = tuple(int(v) for v in sys.argv[sys.argv.index('--box') + 1].split(','))
files = sorted(glob.glob(os.path.join(d, 'f*.png')))


def ink(p):
    im = Image.open(p).convert('L').crop((box[0], box[1], box[0] + box[2], box[1] + box[3]))
    return sum(1 for v in im.getdata() if v > 100)


vals = [ink(f) for f in files]
pick = [files[i - 1] for i in range(1, len(vals)) if vals[i - 1] > 200 and vals[i] < vals[i - 1] * 0.4]
pick.append(files[-1])
ims = [Image.open(p).convert('RGB').crop((box[0], box[1], box[0] + box[2], box[1] + box[3])) for p in pick]
W = Image.new('RGB', (box[2], box[3] * len(ims)))
for i, im in enumerate(ims):
    W.paste(im, (0, i * box[3]))
W.save(out)
print(' '.join(os.path.basename(p) for p in pick))
