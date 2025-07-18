import os
import cv2
import time
import shutil
import socket
import argparse
import subprocess
from mtcnn import MTCNN
from colorama import init, Fore, Style
init(autoreset=True)  # initializes colorama


print('\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ FACE DETECT ▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 7.18.25 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n')

# USAGE python pose_gen_package/face_detector.py -- --scan SCAN_ID --path path/takes/ --software path/scannermeshprocessing-2023/ --rotmesh scannermeshprocessing-2023/rotate_mesh.py

def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
    
    # add parser rules
    parser.add_argument('-n', '--scan', help="scan name")
    parser.add_argument('-m', '--path', help="directory", default = "/System/Volumes/Data/mnt/scanDrive/takes/") 
    parser.add_argument('-sf', '--software', help="software", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/")
    parser.add_argument("-b", "--blender", help="Enter the path Blender Executable", dest="blender_path", default = "/Applications/Blender.app/Contents/MacOS/Blender")
    parser.add_argument("-r", "--rotmesh", help="Enter the path to Rotate Mesh Script", dest="rotmesh_path", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/rotate_mesh.py")
    parser.add_argument("-bp", "--bypass", help="0 to do face detection | 1 to go straight to the pose generation process", dest="bypass", default = 0)
    parser.add_argument("-s", "--save", help="Use Save Landmarks Image in Pose Generator", default="1")

    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


def print_enhanced(text, text_color="white", label="", label_color="white", prefix="", suffix=""):
    color_code = {
        'black': Fore.BLACK,
        'red': Fore.RED,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE,
        'reset': Style.RESET_ALL
    }

    if label == "":
        return print(f"{prefix}{color_code[text_color]}{text}{suffix}")

    print(f"{prefix}[{color_code[label_color]}{label}{Style.RESET_ALL}] {color_code[text_color]}{text}{suffix}")


def write_unified_log(scan, path, message):
    log_file_path = os.path.join(path, "_log", "face_detection_log.txt")
    machine_name = socket.gethostname()
    current_time = time.strftime("%I:%M:%S %p", time.localtime())

    with open(log_file_path, "a") as log_file:  # Changed mode from "w" to "a"
        log_file.write("\n\n")  # Add two newline characters to separate log entries
        log_file.write(f"Machine name: {machine_name}\n")
        log_file.write(f"Scan ID: {scan}\n")
        log_file.write(f"Time: {current_time}\n")
        log_file.write(message)


def write_log(scan, path, message):
    log_file_path = os.path.join(path, scan, "face_detection_log.txt")
    machine_name = socket.gethostname()
    current_time = time.strftime("%I:%M:%S %p", time.localtime())

    with open(log_file_path, "a") as log_file:  # Changed mode from "w" to "a"
        log_file.write("\n\n")  # Add two newline characters to separate log entries
        log_file.write(f"Machine name: {machine_name}\n")
        log_file.write(f"Scan ID: {scan}\n")
        log_file.write(f"Time: {current_time}\n")
        log_file.write(message)


def copy_assets_to_local(server_directory, local_directory, scan):
    server_scan_directory = os.path.join(server_directory, scan)
    local_scan_directory = os.path.join(local_directory, scan)
    print('_______________________________________________________________________')
    print(f"Copying assets from {server_scan_directory} to {local_scan_directory}")
    print('_______________________________________________________________________')

    if not os.path.exists(local_scan_directory):
        os.makedirs(local_scan_directory)

    for item in os.listdir(server_scan_directory):
        if item == "source":
            continue

        server_item_path = os.path.join(server_scan_directory, item)
        local_item_path = os.path.join(local_scan_directory, item)

        if os.path.isfile(server_item_path):
            shutil.copy(server_item_path, local_item_path)
        else:
            shutil.copytree(server_item_path, local_item_path)

    return local_scan_directory

def copy_results_to_server(server_directory, local_directory, scan):
    server_scan_directory = os.path.join(server_directory, scan)
    local_scan_directory = os.path.join(local_directory, scan)

    print('_______________________________________________________________________')
    print(f"Copying results from {local_scan_directory} to {server_scan_directory}")
    print('_______________________________________________________________________')

    start_time = time.time()

    for root, dirs, files in os.walk(local_scan_directory):
        if "source" in dirs:
            dirs.remove("source")

        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_scan_directory)
            server_path = os.path.join(server_scan_directory, relative_path)

            # Create the necessary directories in the server path
            server_file_directory = os.path.dirname(server_path)
            if not os.path.exists(server_file_directory):
                os.makedirs(server_file_directory)

            # print(f"Copying {local_path} to {server_path}")
            shutil.copy(local_path, server_path)

    elapsed_time = time.time() - start_time
    print(f"Copying process took {elapsed_time:.2f} seconds")

    shutil.rmtree(local_scan_directory)


def detect_faces(image_path):
    # Create the detector, using default weights
    detector = MTCNN()

    # Read the image
    img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

    # Detect faces
    faces = detector.detect_faces(img)

    # Return a list of faces or faces=[]
    return faces

def pose_generator(image_path, software, blender, blend_file, use_save_landmarks_image="0"):
    get_camera_corners_script = os.path.join(software, "pose_gen_package", "get_camera_corners.py")
    if os.path.exists(get_camera_corners_script):
        # print_enhanced(f"\n{blender} -b {blend_file} -P {get_camera_corners_script}\n", label="RUN COMMAND", label_color="yellow")
        subprocess.run([blender, "-b", blend_file, "-P", get_camera_corners_script])

    pose_gen_script = os.path.join(software, "pose_gen_package", "pose_generator.py")
    subprocess.run(["python", pose_gen_script, "-i", image_path, "-s", use_save_landmarks_image])

def rotate_mesh(scan, path, blender, rotmesh, new_blend_file):
    # print_enhanced(f"{blender} -b {new_blend_file} -P {rotmesh} -- --scan {scan} --path {path}", label="RUN COMMAND", label_color="yellow")
    subprocess.run([blender, "-b", new_blend_file, "-P", rotmesh, "--", "--scan", scan, "--path", path])

def copy_and_rename_files(src, dst):
    if os.path.exists(src):
        shutil.copy(src, dst)

def move_and_rename_files(src, dst):
    if os.path.exists(src):
        shutil.move(src, dst)

def main():
    # Parse command line arguments
    ARGS = get_args()
    SCAN = str(ARGS.scan)
    SCAN_DIR = str(ARGS.path)
    BLENDER_EXE = str(ARGS.blender_path)
    ROTATE_MESH_SCRIPT = str(ARGS.rotmesh_path)
    SOFTWARE = str(ARGS.software)
    BYPASS_FACE_DETECTION = int(ARGS.bypass)
    USE_SAVE_LANDMARKS_IMAGE = str(ARGS.save)

    BLEND_FILEPATH = os.path.join(SCAN_DIR, SCAN, "photogrammetry", f"{SCAN}.blend")
    PNG_FILEPATH = os.path.join(SCAN_DIR, SCAN, "photogrammetry", f"{SCAN}.png")

    # LOAD THE IMAGE
    IMAGE_PATH = os.path.join(SCAN_DIR, SCAN, "photogrammetry", f"{SCAN}.png")

    if BYPASS_FACE_DETECTION == 1:
        print_enhanced("BYPASSING FACE DETECTION", text_color="yellow", label="INFO", label_color="yellow")

        log_message = "Face detection: BYPASSED"
        write_log(SCAN, SCAN_DIR, log_message)

        # CALL POSE GENERATOR
        print_enhanced("Calling pose_generator.py", label="INFO", label_color="yellow")
        pose_generator(IMAGE_PATH, SOFTWARE, BLENDER_EXE, BLEND_FILEPATH, USE_SAVE_LANDMARKS_IMAGE)

        return

    faceFound = detect_faces(IMAGE_PATH)

    if faceFound:
        print_enhanced("SUCCESS", text_color="green", label="DETECT FACE", label_color="green")

        log_message = "Face detection: SUCCESS"
        write_log(SCAN, SCAN_DIR, log_message)

        # CALL POSE GENERATOR
        print_enhanced("Calling pose_generator.py", label="INFO", label_color="yellow")
        pose_generator(IMAGE_PATH, SOFTWARE, BLENDER_EXE, BLEND_FILEPATH, USE_SAVE_LANDMARKS_IMAGE)

        return

    print_enhanced("FAILED", text_color="red", label="DETECT FACE", label_color="red")
    log_message = "Face detection: FAILED"
    #write_unified_log(scan, path, log_message)

    # COPY AND RENAME BLEND AND PNG FILES
    old_blend_file = BLEND_FILEPATH
    new_blend_file = os.path.join(SCAN_DIR, SCAN, "photogrammetry", f"{SCAN}-bak.blend")
    old_png_file = PNG_FILEPATH
    new_png_file = os.path.join(SCAN_DIR, SCAN, "photogrammetry", f"{SCAN}-bak.png")
    move_and_rename_files(old_blend_file, new_blend_file)
    move_and_rename_files(old_png_file, new_png_file)

    # LAUNCH BLENDER TO ROTATE MESH
    print_enhanced("Calling rotate_mesh.py", label="INFO", label_color="yellow")
    rotate_mesh(SCAN, SCAN_DIR, BLENDER_EXE, ROTATE_MESH_SCRIPT, new_blend_file)

    print_enhanced("Running Face Detection again", label="INFO", label_color="yellow")
    faceFound = detect_faces(IMAGE_PATH)

    if faceFound:
        print_enhanced("SUCCESS after rotation", text_color="green", label="DETECT FACE", label_color="green")
        log_message = "Face detection after rotation: SUCCESS"
        write_log(SCAN, SCAN_DIR, log_message)
        
        # CALL POSE GENERATOR
        print_enhanced("Calling pose_generator.py", label="INFO", label_color="yellow")
        pose_generator(IMAGE_PATH, SOFTWARE, BLENDER_EXE, BLEND_FILEPATH, USE_SAVE_LANDMARKS_IMAGE)

        return

    print_enhanced("FAILED after rotation", text_color="red", label="DETECT FACE", label_color="red")
    log_message = "Face detection after rotation: FAILED"
    write_log(SCAN, SCAN_DIR, log_message)
    #write_unified_log(scan, path, log_message)

if __name__ == '__main__':
    main()