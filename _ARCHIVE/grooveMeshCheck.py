import os
import subprocess
import bpy
import argparse
import sys
import shutil
import shlex

def main(usdz_path, prep_usdz_script_path, groove_mesher_path, source_images_path, output_path, feature_sensitivity, detail):
    # 1. Rename a file from preview.usdz to preview.zip
    usdz_folder = os.path.dirname(usdz_path)
    usdz_filename = os.path.basename(usdz_path)
    zip_path = os.path.join(usdz_folder, 'preview.zip')

    print("Copying and renaming the USDZ file to a ZIP file...")
    shutil.copy(usdz_path, zip_path)  # Use shutil.copy() instead of os.rename()

    # 2. Unzip the file
    print("Unzipping the file...")
    subprocess.run(['unzip', zip_path, '-d', usdz_folder])

    # 3. Find the baked_mesh.usdc file
    # for root, dirs, files in os.walk(usdz_folder):
    #     for file in files:
    #         if file == 'baked_mesh.usdc':
    #             usdc_path = os.path.join(root, file)
    #             break

    # file = 'baked_mesh.usda'
    file = 'preview.usdz'
    usdc_path = os.path.join(usdz_folder, file)

    # 4. Import the baked_mesh.usdc file
    bpy.ops.wm.usd_import(filepath=usdc_path)
    print(usdc_path)
    # bpy.ops.wm.usd_import(filepath="/Volumes/gjc/productions/Wasserman_CFP2210/rawFootage/backup/takes/3a08a0a6-ae67-d2e4-e1fc-de5e3f3a13f1/photogrammetry/baked_mesh.usdc")

    # 5. Run the Blender Python script called prepUSDZ.py
    print("Running the prepUSDZ.py script...")
    sys.path.append(os.path.dirname(prep_usdz_script_path))
    import prepUSDZ
    result = prepUSDZ.main()

    if result:
        min_x, max_x, min_y, max_y, min_z, max_z = result
        print("Bounding box values received from prepUSDZ.py script.")
        print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}, min_z: {min_z}, max_z: {max_z}")

        # 6. Run the groove-mesher app with the bounding box values
        print("Running groove-mesher...")
        newMinY = abs(min_y)
        newMaxY = -(abs(max_y))
        command_list = [
            f'"{groove_mesher_path}"',
            f'"{source_images_path}"',
            f'"{output_path}"',
            "--create-final-model",
            # "--enable-object-masking",
            "--feature-sensitivity="+feature_sensitivity,
            "-d="+detail,
            f"--minX={min_x:.2f}",
            f"--maxX={max_x:.2f}",
            # f"--minY={min_z:.2f}",
            # f"--maxY={max_z:.2f}",
            f"--minZ={newMaxY:.2f}",
            f"--maxZ={newMinY:.2f}"
        ]

        command_str = ' '.join(command_list)
        subprocess.run(command_str, shell=True)
        print(command_str)

    else:
        print("Bounding box values not received from prepUSDZ.py script. Skipping groove-mesher execution.")

def get_args():
    # Remove Blender specific arguments
    argv = sys.argv[sys.argv.index("--") + 1:]

    parser = argparse.ArgumentParser(description='Process USDZ file and run a Blender script.')
    parser.add_argument('usdz_path', type=str, help='Path to the preview.usdz file.')
    parser.add_argument('prep_usdz_script_path', type=str, help='Path to the prepUSDZ.py script.')
    parser.add_argument('groove_mesher_path', type=str, help='Path to the groove-mesher app.')
    parser.add_argument('source_images_path', type=str, help='Path to the scanner source images.')
    parser.add_argument('output_path', type=str, help='Path to the photogrammetry output.')
    parser.add_argument('feature_sensitivity', type=str, choices=['normal', 'high'], default='normal', help='Feature sensitivity for groove-mesher (default: normal).')
    parser.add_argument('detail', type=str, choices=['full', 'raw'], default='full', help='The detail to generate (default: full).')

    return parser.parse_args(argv)

if __name__ == "__main__":
    args = get_args()
    main(args.usdz_path, args.prep_usdz_script_path, args.groove_mesher_path, args.source_images_path, args.output_path, args.feature_sensitivity, args.detail)

