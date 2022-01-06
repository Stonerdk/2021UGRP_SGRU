from toon_cut import cut_raw_images
from webtoon_crawler import webcrawling
import argparse
import os
from glob import glob
from img_to_sketch import save_sketch
from segmentation_separation import sketch_to_segmented, extract_region
import shutil
import cv2

class subdir_gen:
    def __init__(self, root):
        self.root = root
    def new_dir(self, name):
        d = os.path.join(self.root, name)
        if not os.path.exists(d):
            os.mkdir(d)
        return d

def dir_resize(src_dir, dest_dir, size):
    for fname in glob(os.path.join(src_dir, "*.png")):
        img = cv2.imread(fname, cv2.IMREAD_COLOR)
        dst = cv2.resize(img, dsize=(size, size), interpolation=cv2.INTER_AREA)
        cv2.imwrite(os.path.join(dest_dir, os.path.split(fname)[1]), dst)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #저장할 폴더, 시작 URL, 총 진행할 화 수
    parser.add_argument('--output_dir', default='./LR', type = str, help='image directory name.')
    parser.add_argument('--start_url', default='https://comic.naver.com/webtoon/detail?titleId=570503&no=366&weekday=thu', type = str,
                        help='start website url. (lower)')
    parser.add_argument('--episode_cnt', default=5, type = int, help='count of episodes.')
    parser.add_argument('--size', default = 512, type = int, help = 'width, height of output')
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    
    sdgen = subdir_gen(args.output_dir)
    crawling_dir = sdgen.new_dir("crawling")
    roughcut_dir = sdgen.new_dir("roughcut")
    original_dir = sdgen.new_dir("original")
    sketch_dir = sdgen.new_dir("sketch")
    segmented_dir = sdgen.new_dir("segmented")
    segmented_col_dir = sdgen.new_dir("segmented_color")
    segmented_sub_dir = sdgen.new_dir("segmented_sub")

    # webcrawling(args.start_url, args.episode_cnt, crawling_dir)
    
    if args.size == 512:
        cut_raw_images(crawling_dir, roughcut_dir, original_dir)
        save_sketch(original_dir, sketch_dir)
    else:
        original_dir_512 = sdgen.new_dir("original_512")
        sketch_dir_512 = sdgen.new_dir("sketch_512")
        cut_raw_images(crawling_dir, roughcut_dir, original_dir_512)
        save_sketch(original_dir_512, sketch_dir_512)
        dir_resize(original_dir_512, original_dir, args.size)
        dir_resize(sketch_dir_512, sketch_dir, args.size)
        shutil.rmtree(original_dir_512)
        shutil.rmtree(sketch_dir_512)
    shutil.rmtree(crawling_dir)
    shutil.rmtree(roughcut_dir)

    sketch_to_segmented(sketch_dir, segmented_dir)
    extract_region(original_dir, segmented_dir, segmented_col_dir, segmented_sub_dir, args.size)