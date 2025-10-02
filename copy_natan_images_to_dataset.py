# copy Natan's images with correct names to dataset folder

import os
import shutil

INPUT_PATH = '/home/gusalbukrk/Downloads/natan'
OUTPUT_PATH = '/home/gusalbukrk/Downloads/wildfire-cerrado'

for dir in ['images', 'masks']:
    input_dir_path = os.path.join(INPUT_PATH, dir)

    for filename in os.listdir(input_dir_path):
        print(filename)

        shutil.copy(
            os.path.join(input_dir_path, filename),
            os.path.join(OUTPUT_PATH, dir, filename if dir == 'images' else filename.replace('.png', '.jpg_mask.png'))
        )

print('Done')
