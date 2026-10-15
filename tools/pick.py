"""Paste chosen frames into one sheet: python -X utf8 tools/pick.py OUT.png DIR/fNNNNNN.png ... [--cols 3]"""
import sys
from PIL import Image

args = [a for a in sys.argv[2:] if not a.startswith('--')]
cols = 3
if '--cols' in sys.argv:
    cols = int(sys.argv[sys.argv.index('--cols') + 1]); args = [a for a in args if a != str(cols)]
ims = [Image.open(p) for p in args]
rows = (len(ims) + cols - 1) // cols
W = Image.new('RGB', (cols * 256, rows * 224))
for i, im in enumerate(ims):
    W.paste(im.convert('RGB'), ((i % cols) * 256, (i // cols) * 224))
W.save(sys.argv[1])
