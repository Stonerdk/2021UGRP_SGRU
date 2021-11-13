from PIL import Image
from glob import glob
import os

WIDTH = 512
HEIGHT = 512


def sketch_transparent(src_dir, dest_dir, size):
    for fname in glob(os.path.join(src_dir, "*.png")):
        try:
            sketch_img = Image.open(fname)
            sketch_img = sketch_img.convert("RGB")
        except:
            print("file not found")
            continue
        sketch_pix = sketch_img.load()

        sketch_transparent_img = Image.new(mode = "RGBA", size = (size, size), color = (0, 0, 0, 0))
        sketch_transparent_pix = sketch_transparent_img.load()
        for x in range(size):
            for y in range(HEIGHT):
                alpha = 1 - min(sketch_pix[x, y]) / 255
                r, g, b = 0, 0, 0
                if alpha != 0:
                    r = min(255, int((sketch_pix[x, y][0] - (1 - alpha) * 255) / alpha))
                    g = min(255, int((sketch_pix[x, y][1] - (1 - alpha) * 255) / alpha))
                    b = min(255, int((sketch_pix[x, y][2] - (1 - alpha) * 255) / alpha))
                sketch_transparent_pix[x, y] = (r, g, b, int(alpha * 255))
        sketch_transparent_img.save(os.path.join(dest_dir, fname[9:]))
        print("transparent saved " + fname)

