import bpy
import os
import shutil
import sys
# Add this block of code to append the installed tqdm package location to sys.path
import site
user_site_packages = site.getusersitepackages()
if user_site_packages not in sys.path:
    sys.path.append(user_site_packages)

from tqdm import tqdm

def copy_missing_texture(texture_path, directories):
    for directory in directories:
        blend_file_path = os.path.join(directory, 'photogrammetry', f'{directory}.blend')
        if os.path.exists(blend_file_path):
            blend_dir = os.path.dirname(blend_file_path)
            texture_file_path = os.path.join(blend_dir, os.path.basename(texture_path))
            if not os.path.exists(texture_file_path):
                print(f'Copying {texture_path} to {blend_dir}')
                shutil.copy(texture_path, blend_dir)

path_to_blender_files = '/Users/dalecarman/Dropbox (Groove Jones)/Projects/scanner_dev/CFP_backwards/'
directories = [os.path.join(path_to_blender_files, d) for d in os.listdir(path_to_blender_files) if os.path.isdir(os.path.join(path_to_blender_files, d))]
missing_texture_path = '/Users/dalecarman/Dropbox (Groove Jones)/Projects/scanner_dev/Software/scannermeshprocessing/kloofendal_48d_partly_cloudy_4k.hdr'

copy_missing_texture(missing_texture_path, directories)

for directory in tqdm(directories, desc="Fixing files", unit="file"):
    if os.path.isdir(os.path.join(directory, 'photogrammetry')):
        file_path = os.path.join(directory, 'photogrammetry', f'{os.path.basename(directory)}.blend')
        with bpy.data.libraries.load(file_path) as (data_from, data_to):
            data_to.images = data_from.images

        for image in data_to.images:
            if image is not None and not image.packed_file:
                if not os.path.exists(image.filepath):
                    image_file_name = os.path.basename(image.filepath)
                    image_dir = os.path.dirname(file_path)
                    image.filepath = os.path.join(image_dir, image_file_name)
                    image.reload()
                    print('Fixed missing image:', image.filepath)

        # Save to a temporary file
        temp_file_path = file_path + ".temp"
        bpy.ops.wm.save_as_mainfile
        print('Fixed missing images in file:', file_path)
