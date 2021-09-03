from keras.models import load_model
import cv2
import numpy as np
from helper import *
import os
import sys

mod = load_model('mod.h5')

def get(name, path, output_dir):
    from_mat = cv2.imread(path)
    width = float(from_mat.shape[1])
    height = float(from_mat.shape[0])
    new_width = 0
    new_height = 0
    from_mat = cv2.resize(from_mat, (512, 512), interpolation=cv2.INTER_AREA)
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

#default directory name
if len(sys.argv) != 3:
    webtoon_dir_name = './toon'
    sketch_dir_name = './sketch'   
else: 
    webtoon_dir_name = sys.argv[1]
    sketch_dir_name = sys.argv[2]

file_list = os.listdir(webtoon_dir_name)
print(file_list)

for img in file_list:
    img_path = webtoon_dir_name + '/' + img
    print(img +' started')
    get(img, img_path, sketch_dir_name)
    print(img +' ended')