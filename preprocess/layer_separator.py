import argparse
import os
from datetime import datetime
from img_to_sketch import save_sketch_single
from segmentation_separation import sketch_to_segmented_single, subtract_color_single
from sketch_transparent import sketch_transparent_single, segment_sketch_blend


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", default = "./input/-11_4.png", type = str)
    default_output_dir = os.path.join("./output", datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    parser.add_argument("--output_dir", default = default_output_dir, type = str)
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    save_sketch_single(args.input, args.output_dir)
    sketch_transparent_single(os.path.join(args.output_dir, "sketch.png"), args.output_dir)
    sketch_to_segmented_single(args.input, os.path.join(args.output_dir, "sketch.png"), os.path.join(args.output_dir, "sketch_transparent.png"),args.output_dir)
    segment_sketch_blend(os.path.join(args.output_dir, "sketch_transparent.png"), os.path.join(args.output_dir, "segmented.png"), args.output_dir)
    subtract_color_single(args.input, os.path.join(args.output_dir, "segment_sketch_blend.png"),os.path.join(args.output_dir, "sketch_transparent.png"), args.output_dir)