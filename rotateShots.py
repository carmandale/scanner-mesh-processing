import subprocess
import argparse
import os
from tqdm import tqdm
from PIL import Image

# USAGE - python3 rotateShots.py

def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    if "--" in all_arguments:
        double_dash_index = all_arguments.index("--")
        script_args = all_arguments[double_dash_index + 1:]
    else:
        script_args = []

    # add parser rules
    parser.add_argument('-n', '--scan', help="scan name")
    parser.add_argument('-m', '--path', help="directory", default = "/Users/administrator/groove-test/takes/") 
    parser.add_argument("-b", "--blender", help="Enter the path Blender Executable", dest="blender_path", default = "/Applications/Blender.app/Contents/MacOS/Blender")
    parser.add_argument("-r", "--rotmesh", help="Enter the path to Rotate Mesh Script", dest="rotmesh_path", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/rotate_mesh.py")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

args = get_args()
scan = str(args.scan)
path = str(args.path)
blender = str(args.blender_path)
rotmesh = str(args.rotmesh_path)
software = "/Users/administrator/groove-test/software/scannermeshprocessing-2023"


def process_scans(path, blender, rotmesh):
    scans = [entry.name for entry in os.scandir(path) if entry.is_dir()]
    for scan in tqdm(scans, desc="Processing scans"):
        blend_file = os.path.join(path, scan, "photogrammetry", f"{scan}.blend")
        subprocess.run([blender, "-b", blend_file, "-P", rotmesh,"--", "--scan", scan, "--facing 0.5", "--path", path])

process_scans(path, blender, rotmesh)

images_per_row = 8

# Collect image paths
image_paths = []
for scan in os.listdir(path):
    scan_dir = os.path.join(path, scan, "photogrammetry")
    if os.path.isdir(scan_dir):
        image_path = os.path.join(scan_dir, f"{scan}.png")
        if os.path.isfile(image_path):
            image_paths.append(image_path)

# Load images and create grid
images = []
for image_path in tqdm(image_paths, desc="Loading images"):
    images.append(Image.open(image_path))
num_images = len(images)
rows = (num_images + images_per_row - 1) // images_per_row
row_heights = [max([img.size[1] for img in images[i*images_per_row:(i+1)*images_per_row]]) for i in range(rows)]
grid_width = sum([img.size[0] for img in images[:images_per_row]])
grid_height = sum(row_heights)
grid_image = Image.new('RGB', (grid_width, grid_height), color=(255, 255, 255))
x_offset = 0
y_offset = 0
for i, img in enumerate(tqdm(images, desc="Creating grid")):
    grid_image.paste(img, (x_offset, y_offset))
    x_offset += img.size[0]
    if (i + 1) % images_per_row == 0:
        x_offset = 0
        y_offset += row_heights[i // images_per_row]

# Show grid image in window
grid_image.show()

# # Collect image paths
# image_paths = []
# for scan in os.listdir(path):
#     scan_dir = os.path.join(path, scan, "photogrammetry")
#     if os.path.isdir(scan_dir):
#         image_path = os.path.join(scan_dir, f"{scan}.png")
#         if os.path.isfile(image_path):
#             image_paths.append(image_path)

# # Load images and combine them
# images = [Image.open(p) for p in image_paths]
# widths, heights = zip(*(i.size for i in images))
# total_width = sum(widths)
# max_height = max(heights)
# combined_image = Image.new('RGB', (total_width, max_height), color=(255, 255, 255))
# x_offset = 0
# for img in images:
#     combined_image.paste(img, (x_offset, 0))
#     x_offset += img.size[0]

# # Show combined image in window
# combined_image.show()
