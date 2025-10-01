# for each image in INPUT_PATH, crop left and right square images, resize to RESIZE_TO size and save to OUTPUT_PATH

import os
import shutil
from PIL import Image

INPUT_PATH = '/home/gusalbukrk/Downloads/wildfire-cerrado'
OUTPUT_PATH = '/home/gusalbukrk/Downloads/wildfire-cerrado-resized'

RESIZE_TO = (512, 512)

if os.path.exists(OUTPUT_PATH):
    shutil.rmtree(OUTPUT_PATH)
os.makedirs(OUTPUT_PATH)
os.makedirs(os.path.join(OUTPUT_PATH, 'images'))
os.makedirs(os.path.join(OUTPUT_PATH, 'masks'))

# dimensions of the images in the dataset
# video_9: 1920x1080
# video_19: 1280x720
# video_31: 1920x1080
# video_37: 3840x2160

for dir in ['images', 'masks']:
    input_dir_path = os.path.join(INPUT_PATH, dir)

    for filename in os.listdir(input_dir_path):
        print(filename)

        img = Image.open(os.path.join(input_dir_path, filename))
        w, h = img.size

        # left, upper, right and lower
        left_crop = img.crop((0, 0, h, h)).resize(RESIZE_TO)
        right_crop = img.crop((w - h, 0, w, h)).resize(RESIZE_TO)

        # skip masks that have no fire (all black) and delete their corresponding images
        if dir == 'masks':
            left_crop_path = os.path.join(OUTPUT_PATH, dir, filename.replace('.jpg_mask.png', '_1.jpg_mask.png'))
            right_crop_path = os.path.join(OUTPUT_PATH, dir, filename.replace('.jpg_mask.png', '_2.jpg_mask.png'))

            if left_crop.getextrema()[1] == 0:
                print('\tskipping', left_crop_path.split('/')[-1])
                os.remove(left_crop_path.replace('masks', 'images').replace('_mask.png', ''))
            else:
                left_crop.save(left_crop_path)

            if right_crop.getextrema()[1] == 0:
                print('\tskipping', right_crop_path.split('/')[-1])
                os.remove(right_crop_path.replace('masks', 'images').replace('_mask.png', ''))
            else:
                right_crop.save(right_crop_path)
        else:
            left_crop_path = os.path.join(OUTPUT_PATH, dir, filename[:-4] + '_1' + filename[-4:])
            right_crop_path = os.path.join(OUTPUT_PATH, dir, filename[:-4] + '_2' + filename[-4:])

            left_crop.save(left_crop_path)
            right_crop.save(right_crop_path)

        img.close()

print('Done')
