import numpy as np
import cv2
from linefiller.trappedball_fill import trapped_ball_fill_multi, flood_fill_multi, mark_fill, build_fill_map, merge_fill, \
    show_fill_map
from linefiller.thinning import thinning
from glob import glob
import traceback
import sys, os
from PIL import Image
from collections import deque

WIDTH = 256
HEIGHT = 256


def trap_ball(sketch_image):
    ret, binary = cv2.threshold(sketch_image, 220, 255, cv2.THRESH_BINARY)

    fills = []
    result = binary

    fill = trapped_ball_fill_multi(result, 3, method='max')
    fills += fill
    result = mark_fill(result, fill)
    fill = trapped_ball_fill_multi(result, 2, method=None)
    fills += fill
    result = mark_fill(result, fill)
    fill = trapped_ball_fill_multi(result, 1, method=None)
    fills += fill
    result = mark_fill(result, fill)
    fill = flood_fill_multi(result)
    fills += fill
    fillmap = build_fill_map(result, fills)
    fillmap = merge_fill(fillmap)

    return show_fill_map(thinning(fillmap))

def sketch_to_segmented(sketch_dir, segmented_dir):
    failed = []
    success = []

    for fname in glob(sketch_dir + "/*.png"):
        try:
            im = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
            result = trap_ball(im)
            cv2.imwrite(os.path.join(segmented_dir, os.path.split(fname)[1]), result)
            success.append(os.path.split(fname)[1])
        except Exception as e:
            traceback.print_exc()
            failed.append(os.path.split(fname)[1])
        print("segmented done : " + fname)
        
    print(failed)


def sketch_to_segmented_single(original_file, sketch_file, sketch_transparent_file, output_dir):
    im = cv2.imread(sketch_file, cv2.IMREAD_GRAYSCALE)
    segmented_result = trap_ball(im)
    cv2.imwrite(os.path.join(output_dir, "segmented.png"), segmented_result)

    sketch_transparent_pix = Image.open(sketch_transparent_file).load()
    toon_pix = Image.open(original_file).load()
    segmented_pix = Image.open(os.path.join(output_dir, "segmented.png")).load()

    checked = [[False] * HEIGHT for _ in range(WIDTH)]
    clusters = []
    deq = deque()
    
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if checked[x][y]:
                continue
            col = segmented_pix[x, y]
            deq = deque()
            deq.append((x, y))
            cluster = []
            while deq:
                xx, yy = deq.popleft()
                if xx < 0 or yy < 0 or xx >= WIDTH or yy >= HEIGHT:
                    continue
                if segmented_pix[xx, yy] == col and not checked[xx][yy]:
                    cluster.append((xx, yy))
                    checked[xx][yy] = True
                    deq.append((xx, yy + 1))
                    deq.append((xx - 1, yy))
                    deq.append((xx + 1, yy))
                    deq.append((xx, yy - 1))
            clusters.append(cluster)
    
    segmented_color_im = Image.new(mode = "RGB", size = (WIDTH, HEIGHT), color = (0, 128, 255))
    segmented_color_pix = segmented_color_im.load()

    # get capital color from each segments
    for cluster in clusters:
        red, green, blue = 0, 0, 0
        d = 0
        for x, y in cluster:
            w = 1 - sketch_transparent_pix[x, y][3] / 255
            r, g, b = toon_pix[x, y]
            red, green, blue = red + r * w, green + g * w, blue + b * w
            d += w
        col = (int(red / d), int(green / d), int(blue / d))
        for x, y in cluster:
            if sum(col) / 3 >= 235:
                col = (255, 255, 255)
            if sum(col) / 3 < 20:
                col = (0,0,0)
            segmented_color_pix[x, y] = col
    
    segmented_color_im.save(os.path.join(output_dir, "segmented.png"))
    

def subtract_color_single(original_file, segmented_file, sketch_transparent_file, output_dir, size = 256):
    original_pix = Image.open(original_file).load()
    segmented_pix = Image.open(segmented_file).load()
    sketch_transparent_pix = Image.open(sketch_transparent_file).load()

    subtract_im = Image.new(mode = 'RGBA', size = (256,256))
    subtract_pix = subtract_im.load()
    for x in range(256):
        for y in range(256):
            r0, g0, b0 = segmented_pix[x, y][:3]
            r1, g1, b1 = original_pix[x, y]
            base_a = sketch_transparent_pix[x, y][3]
            r, g, b = 0, 0, 0
            min_list = [1]
            if r0 != 0:
                min_list.append(r1 / r0)
            if b0 != 0:
                min_list.append(b1 / b0)
            if g0 != 0:
                min_list.append(g1 / g0)
            if r0 != 255:
                min_list.append((255 - r1) / (255 - r0))
            if b0 != 255:
                min_list.append((255 - b1) / (255 - b0))
            if g0 != 255:
                min_list.append((255 - g1) / (255 - g0))
            alpha = 1 - min(min_list)
            if alpha != 0:
                r = int(min(255, (r1 - (1 - alpha) * r0) / alpha))
                g = int(min(255, (g1 - (1 - alpha) * g0) / alpha))
                b = int(min(255, (b1 - (1 - alpha) * b0) / alpha))
            alpha = min(alpha * 255, 64)
            alpha = int(alpha * (1 - base_a / 255))
            subtract_pix[x, y] = (r, g, b, alpha)
    
    subtract_im.save(os.path.join(output_dir, "subtract.png"))


def subtract_color(src_rgb, dest_rgb):
    r0, g0, b0 = src_rgb
    r1, g1, b1 = dest_rgb
    r, g, b = 0, 0, 0
    min_list = [1]
    if r0 != 0:
        min_list.append(r1 / r0)
    if b0 != 0:
        min_list.append(b1 / b0)
    if g0 != 0:
        min_list.append(g1 / g0)
    if r0 != 255:
        min_list.append((255 - r1) / (255 - r0))
    if b0 != 255:
        min_list.append((255 - b1) / (255 - b0))
    if g0 != 255:
        min_list.append((255 - g1) / (255 - g0))
    alpha = 1 - min(min_list)
    if alpha != 0:
        r = int(min(255, (r1 - (1 - alpha) * r0) / alpha))
        g = int(min(255, (g1 - (1 - alpha) * g0) / alpha))
        b = int(min(255, (b1 - (1 - alpha) * b0) / alpha))
    return (r, g, b, int(255 * alpha))


def extract_region(original_dir, segmented_dir, segmented_color_dir, segmented_subtract_dir, size):
    WIDTH = size
    HEIGHT = size
    for fname in glob(os.path.join(original_dir, "*.png")):
        segmented_fname = os.path.join(segmented_dir, os.path.split(fname)[1])
        try:
            toon_image = Image.open(fname)
            segmented_image = Image.open(segmented_fname)
        except FileNotFoundError as e:
            print("file not found")
            continue
        toon_pix = toon_image.load()
        segmented_pix = segmented_image.load()

        checked = [[False] * HEIGHT for _ in range(WIDTH)]
        clusters = []
        deq = deque()
        
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if checked[x][y]:
                    continue
                col = segmented_pix[x, y]
                deq = deque()
                deq.append((x, y))
                cluster = []
                while deq:
                    xx, yy = deq.popleft()
                    if xx < 0 or yy < 0 or xx >= WIDTH or yy >= HEIGHT:
                        continue
                    if segmented_pix[xx, yy] == col and not checked[xx][yy]:
                        cluster.append((xx, yy))
                        checked[xx][yy] = True
                        deq.append((xx, yy + 1))
                        deq.append((xx - 1, yy))
                        deq.append((xx + 1, yy))
                        deq.append((xx, yy - 1))
                clusters.append(cluster)
        
        segmented_color_im = Image.new(mode = "RGB", size = (WIDTH, HEIGHT), color = (0, 128, 255))
        segmented_color_pix = segmented_color_im.load()

        segmented_subtract_im = Image.new(mode = "RGBA", size = (WIDTH, HEIGHT), color = (0, 0, 0, 0))
        segmented_subtract_pix = segmented_subtract_im.load()
        
        # get capital color from each segments
        for cluster in clusters:
            red, green, blue = 0, 0, 0
            for x, y in cluster:
                r, g, b = toon_pix[x, y]
                red, green, blue = red + r, green + g, blue + b
            cluster_size = len(cluster)
            col = (red // cluster_size, green // cluster_size, blue // cluster_size)
            for x, y in cluster:
                if col[0] >= 245:
                    col = (255, 255, 255)
                segmented_color_pix[x, y] = col
                segmented_subtract_pix[x, y] = subtract_color(col, toon_pix[x, y])
        
        segmented_color_im.save(os.path.join(segmented_color_dir, os.path.split(fname)[1]))
        segmented_subtract_im.save(os.path.join(segmented_subtract_dir, os.path.split(fname)[1]))
        print(f"{fname} clustering done")

if __name__ == "__main__":
    original_dir_name = os.path.join(sys.argv[1], "original")
    sketch_dir_name = os.path.join(sys.argv[1], "sketch")
    segmented_dir_name = os.path.join(sys.argv[1], "segmented_raw")
    segmented_color_name = os.path.join(sys.argv[1], "segmented_color")
    segmented_sub_name = os.path.join(sys.argv[1], "segmented_subtract")
    
    if not os.path.exists(segmented_dir_name):
        os.mkdir(segmented_dir_name)
    if not os.path.exists(segmented_color_name):
        os.mkdir(segmented_color_name)
    if not os.path.exists(segmented_sub_name):
        os.mkdir(segmented_sub_name)

    sketch_to_segmented(sketch_dir_name, segmented_dir_name)
    extract_region(original_dir_name, segmented_dir_name, segmented_color_name, segmented_sub_name, 512)