# select QUANTITY images from each subdirectory in SRC_DIR proportionally to the total number of images in each subdirectory
# copy selected images to DEST_DIR
# then divide images in DEST_DIR into 3 subdirectories: leonardo, luiz and natan

import os
import shutil

SRC_DIR = '/home/gusalbukrk/Downloads/frames'
DEST_DIR = '/home/gusalbukrk/Downloads/dataset'
QUANTITY = 360 # quantity of images to select in total

if os.path.exists(DEST_DIR):
    shutil.rmtree(DEST_DIR)
os.makedirs(DEST_DIR)

subdirs = sorted(os.listdir(SRC_DIR))
total_quantities = [ len(os.listdir(os.path.join(SRC_DIR, subdir))) for subdir in subdirs ]
proportions = [ q * 100 / sum(total_quantities) for q in total_quantities ]

z = list(zip(subdirs, total_quantities, proportions))

print('Subdirectory | Total Quantity | Proportion')
for subdir, total_quantity, proportion in z:
    print(f'{subdir} | {total_quantity} | {proportion:.2f}%')
print()

print(f"Copying a total of {QUANTITY} images.")
for subdir, total_quantity, proportion in z:
    subdir_path = os.path.join(SRC_DIR, subdir)
    files = sorted(os.listdir(subdir_path))

    quantity_to_select = round(QUANTITY * proportion / 100)
    step = total_quantity / quantity_to_select
    selected_imgs = [files[int(i * step)] for i in range(quantity_to_select)]

    for img in selected_imgs:
        src = os.path.join(subdir_path, img)
        dst = os.path.join(DEST_DIR, f"video{subdir}-{img}")
        shutil.copy(src, dst)
        # print(f'Copied {src} to {dst}')

print('Dividing images into subdirectories leonardo, luiz and natan.')
copied_images = sorted(os.listdir(DEST_DIR))
quantity_per_person = QUANTITY // 3
for index, p in enumerate(['leonardo', 'luiz', 'natan']):
    p_dir = os.path.join(DEST_DIR, p)
    if not os.path.exists(p_dir):
        os.makedirs(p_dir)

    start = quantity_per_person * index
    end = start + quantity_per_person

    for img in copied_images[start:end]:
        src = os.path.join(DEST_DIR, img)
        dst = os.path.join(p_dir, img)
        shutil.move(src, dst)
        # print(f'Moved {src} to {dst}')

print('DONE!')
