from keras.models import load_model
import cv2
import numpy as np
from img_to_sketch_helper import *
import os
import sys
from glob import glob

mod = load_model('mod.h5')

def get(name, path, output_dir):
    from_mat = cv2.imread(path)

    from_mat = cv2.copyMakeBorder(from_mat, 128, 128, 128, 128, cv2.BORDER_REPLICATE)
    cv2.imwrite(output_dir + "/extend.png",from_mat)
    new_width = 512
    new_height = 512
    from_mat = from_mat.transpose((2, 0, 1))
    light_map = np.zeros(from_mat.shape, dtype=np.float)
    for channel in range(3):
        light_map[channel] = get_light_map_single(from_mat[channel])
    light_map = normalize_pic(light_map)
    light_map = resize_img_512_3d(light_map)

    line_mat = mod.predict(light_map, batch_size=1)
    line_mat = line_mat.transpose((3, 1, 2, 0))[0]
    line_mat = line_mat[0:int(new_height), 0:int(new_width), :]
    filter('sketchKeras_colored', line_mat)
    line_mat = np.amax(line_mat, 2)
    denoise_filter_3('sketchKeras_enhanced', line_mat)
    denoise_filter_2('sketchKeras_pured', line_mat)
    denoise_filter('sketchKeras', line_mat, output_dir + '/'+ name)
    return


def save_sketch(original_dir, sketch_dir):
    for fname in glob(os.path.join(original_dir, "*.png")):
        img_name = os.path.split(fname)[1]
        get(img_name, fname, sketch_dir)
        print(img_name + " ended")


def save_sketch_single(original_file, output_dir):
    get("sketch.png", original_file, output_dir)


if __name__ == "__main__":

    webtoon_dir_name = os.path.join(sys.argv[1], "original")
    sketch_dir_name = os.path.join(sys.argv[1], "sketch")

    if not os.path.exists(sketch_dir_name):
        os.mkdir(sketch_dir_name)

    save_sketch(webtoon_dir_name, sketch_dir_name)