import sys
import numpy as np
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1], sys.argv[2]
names = ['sand', 'water', 'jelly', 'ice', 'moss', 'iron', 'dough', 'rubber', 'feather', 'glass',
         'magnet', 'mercury', 'ember', 'frost', 'lava', 'steam', 'mud', 'brick', 'rust', 'ash',
         'bread', 'obsidian']
img = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
size = img.shape[0] / 5

for i, name in enumerate(names):
    r, c = divmod(i, 5)
    cell = img[int(r * size) + 4:int((r + 1) * size) - 4, int(c * size) + 4:int((c + 1) * size) - 4]
    h, w, _ = cell.shape
    edge = np.concatenate([cell[0], cell[-1], cell[:, 0], cell[:, -1]])
    bg = np.median(edge, axis=0)
    dist = np.linalg.norm(cell - bg, axis=2)
    magenta = (cell[..., 0] - cell[..., 1] > 70) & (cell[..., 2] - cell[..., 1] > 70)
    near_bg = (dist < 70) | (magenta & (dist < 120))
    labels, _ = ndimage.label(near_bg)
    border = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    bgmask = np.isin(labels, list(border))
    fg = ~bgmask
    fg = ndimage.binary_fill_holes(fg) & ~(bgmask & ~ndimage.binary_fill_holes(fg))
    band = ndimage.binary_dilation(fg, iterations=1) & ~ndimage.binary_erosion(fg, iterations=1)
    alpha = fg.astype(np.float32)
    alpha[band] = np.clip((dist[band] - 40) / 80, 0, 1) * fg[band] + np.clip((dist[band] - 40) / 80, 0, 1) * ~fg[band] * 0.0
    rgb = cell.copy()
    spill = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]
    tinted = band & (spill > 30)
    m = np.minimum(rgb[..., 0], rgb[..., 2])
    rgb[..., 0][tinted] = np.minimum(rgb[..., 0], rgb[..., 1] + 30)[tinted]
    rgb[..., 2][tinted] = np.minimum(rgb[..., 2], rgb[..., 1] + 30)[tinted]
    rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    ys, xs = np.nonzero(alpha > 0.05)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = Image.fromarray(rgba[y0:y1, x0:x1], 'RGBA')
    side = max(crop.size) + 8
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(crop, ((side - crop.size[0]) // 2, (side - crop.size[1]) // 2))
    canvas.resize((128, 128), Image.LANCZOS).save(f'{out}/{name}.png')
print('ok', len(names))
