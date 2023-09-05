import dlib
import cv2
import argparse
import os
import subprocess
import shutil
import time
import socket
from colorama import init, Fore, Style
init(autoreset=True)  # initializes colorama


print('_______________________________________')
print('_______________________________________')
print('______________FACE DETECT______________')
print('________________4.02.23________________')
print('_______________________________________')

# USAGE python pose_gen_package/face_detector.py -- --scan 3a08a611-ca46-2b5f-9658-9528fa4301f9

def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
    
    # add parser rules
    parser.add_argument('-n', '--scan', help="scan name")
    parser.add_argument('-m', '--path', help="directory", default = "/Users/administrator/groove-test/takes/") 
    parser.add_argument('-sp', '--shape_predictor', help="shape predictor path", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/pose_gen_package/shape_predictor_68_face_landmarks.dat")
    parser.add_argument('-sf', '--software', help="software", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/")
    parser.add_argument("-b", "--blender", help="Enter the path Blender Executable", dest="blender_path", default = "/Applications/Blender.app/Contents/MacOS/Blender")
    parser.add_argument("-r", "--rotmesh", help="Enter the path to Rotate Mesh Script", dest="rotmesh_path", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/rotate_mesh.py")
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


def detect_face(image_path, shape_predictor_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_detector = dlib.get_frontal_face_detector()
    landmark_predictor = dlib.shape_predictor(shape_predictor_path)

    faces = face_detector(gray)
    faceFound = False

    for rect in faces:
        landmarks = landmark_predictor(gray, rect)
        faceFound = True

        for i in range(0, landmarks.num_parts):
            x = landmarks.part(i).x
            y = landmarks.part(i).y
            cv2.circle(image, (x, y), 2, (0, 255, 0), -1)

    return faceFound

def pose_generator(image_path, software):
    pose_gen_script = os.path.join(software, "pose_gen_package", "pose_generator.test.py")
    subprocess.run(["python", pose_gen_script, "-i", image_path])

def rotate_mesh(scan, path, blender, rotmesh, new_blend_file):
    print("\n", blender, "-b", new_blend_file, "-P", rotmesh, "--", "--scan", scan, "--facing 0.5", "--path", path, "\n")
    subprocess.run([f"{blender}/blender", "-b", new_blend_file, "-P", rotmesh, "--", "--scan", scan, "--facing 0.5", "--path", path])

def copy_and_rename_files(src, dst):
    if os.path.exists(src):
        shutil.copy(src, dst)

def move_and_rename_files(src, dst):
    if os.path.exists(src):
        shutil.move(src, dst)

def main():
    # Parse command line arguments
    args = get_args()
    scan = str(args.scan)
    server_path = str(args.path)
    blender = str(args.blender_path)
    rotmesh = str(args.rotmesh_path)
    software = str(args.software)
    shape_predictor_path = str(args.shape_predictor)

    #blender = "C:/Program Files/Blender Foundation/Blender 3.5/blender"
    #rotmesh = "C:/PROYECTOS/GrooveJones_Repository/scannermeshprocessing-2023/rotate_mesh.py"
    #software = "C:/PROYECTOS/GrooveJones_Repository/scannermeshprocessing-2023" # Luis's local test

    # Create a temporary local directory
    # local_temp_directory = "/tmp/face_detection"
    # local_scan_directory = copy_assets_to_local(server_path, local_temp_directory, scan)

    # Update the path variable to the local directory
    # path = local_temp_directory
    path = server_path
    blend_file = os.path.join(path, scan, "photogrammetry", f"{scan}.blend")
    png_file = os.path.join(path, scan, "photogrammetry", f"{scan}.png")

    # Load the image
    image_path = os.path.join(path, scan, "photogrammetry", f"{scan}.png")

    faceFound = detect_face(image_path, shape_predictor_path)

    if faceFound:
        print_enhanced("SUCCESS", text_color="green", label="DETECT FACE", label_color="green")
        log_message = "Face detection: SUCCESS"
        write_log(scan, path, log_message)
        # cv2.imshow("Facial Landmarks", image)
        # Call pose_generator.py script
        print('calling pose_generator.py')
        pose_generator(image_path, software)
        # sys.exit(0)
    else:
        print_enhanced("FAILED", text_color="red", label="DETECT FACE", label_color="red")
        log_message = "Face detection: FAILED"
        write_unified_log(scan, path, log_message)
        # cv2.imshow("Facial Landmarks", image)

        # Copy and rename the blend file
        old_blend_file = blend_file
        new_blend_file = os.path.join(path, scan, "photogrammetry", f"{scan}-bak.blend")
        old_png_file = png_file
        new_png_file = os.path.join(path, scan, "photogrammetry", f"{scan}-bak.png")
        move_and_rename_files(old_blend_file, new_blend_file)
        move_and_rename_files(old_png_file, new_png_file)
        
        # Launch blender and rotate the mesh
        print('calling rotate_mesh.py')
        rotate_mesh(scan, path, blender, rotmesh, new_blend_file)

        print('running face detection again')
        faceFound = detect_face(image_path, shape_predictor_path)

        if faceFound:
            print_enhanced("SUCCESS after rotation", text_color="green", label="DETECT FACE", label_color="green")
            log_message = "Face detection after rotation: SUCCESS"
            write_log(scan, path, log_message)
            # Call pose_generator.py script
            print('calling pose_generator.py')
            pose_generator(image_path)
        else:
            print_enhanced("FAILED after rotation", text_color="red", label="DETECT FACE", label_color="red")
            log_message = "Face detection after rotation: FAILED"
            write_log(scan, path, log_message)
            write_unified_log(scan, path, log_message)

        # cv2.imshow("Rotated Image", rotated_image)
        # sys.exit(1)
        
    # cv2.imshow("Facial Landmarks", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Copy the results back to the server directory
    # copy_results_to_server(server_path, local_temp_directory, scan)

if __name__ == '__main__':
    main()