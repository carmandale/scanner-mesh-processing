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

# USAGE blender -b -P fixTexturePaths.py

def copy_missing_texture(texture_path, directories):
    for directory in directories:
        blend_file_path = os.path.join(directory, f'{directory}','photogrammetry/')
        print(blend_file_path)
        if os.path.exists(blend_file_path):
            blend_dir = os.path.dirname(blend_file_path)
            texture_file_path = os.path.join(blend_dir, os.path.basename(texture_path))
            print(texture_file_path)
            if not os.path.exists(texture_file_path):
                print(f'Copying {texture_path} to {blend_dir}')
                shutil.copy(texture_path, blend_dir)

path_to_blender_files = '/Users/administrator/groove-test/takes/'
directories = [os.path.join(path_to_blender_files, d) for d in os.listdir(path_to_blender_files) if os.path.isdir(os.path.join(path_to_blender_files, d))]
# directories = ['/Users/administrator/groove-test/CFP_backwards/3a08a4d1-c3be-d38a-0649-e0fc6d4c6ca0']
missing_texture_path = '/Users/administrator/groove-test/software/scannermeshprocessing-2023/kloofendal_48d_partly_cloudy_4k.hdr'

# copy_missing_texture(missing_texture_path, directories)

def fix_texture_paths(directories):
    for directory in tqdm(directories, desc="Fixing files", unit="file"):
        if os.path.isdir(os.path.join(directory, 'photogrammetry')):
            file_path = os.path.join(directory, 'photogrammetry', f'{os.path.basename(directory)}.blend')

            # Open the blend file to modify the texture paths
            bpy.ops.wm.open_mainfile(filepath=file_path)

            for image in bpy.data.images:
                if image is not None and not image.packed_file:
                    if not os.path.exists(image.filepath):
                        image_file_name = os.path.basename(image.filepath)
                        image_dir = os.path.dirname(file_path)
                        image.filepath = os.path.join(image_dir, image_file_name)
                        image.reload()
                        print('Fixed missing image:', image.filepath)

            # Save the modified blend file
            bpy.ops.wm.save_mainfile(filepath=file_path)

            print('Fixed missing images in file:', file_path)



fix_texture_paths(directories)