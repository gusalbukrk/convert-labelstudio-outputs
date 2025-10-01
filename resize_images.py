# for each image in INPUT_PATH, crop left and right square images, resize to RESIZE_TO size and save to OUTPUT_PATH

import os
import shutil
from PIL import Image

INPUT_PATH = '/home/gusalbukrk/Downloads/natan'
OUTPUT_PATH = '/home/gusalbukrk/Downloads/natan-resized'

RESIZE_TO = (512, 512)

if os.path.exists(OUTPUT_PATH):
    shutil.rmtree(OUTPUT_PATH)
os.makedirs(OUTPUT_PATH)
os.makedirs(os.path.join(OUTPUT_PATH, 'images'))
os.makedirs(os.path.join(OUTPUT_PATH, 'masks'))

for dir in ['images', 'masks']:
    input_dir_path = os.path.join(INPUT_PATH, dir)

    for filename in os.listdir(input_dir_path):
        print(filename)

        img = Image.open(os.path.join(input_dir_path, filename))
        resized = img.resize(RESIZE_TO)
        p = os.path.join(OUTPUT_PATH, dir, filename)
        resized.save(p)
        img.close()

print('Done')
