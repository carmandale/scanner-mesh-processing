import argparse
import os
import shutil
import platform
from typing import NamedTuple
from dataclasses import dataclass, field, asdict
from colorama import init, Fore, Style
init(autoreset=True)  # initializes colorama

print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬ scan_folder_reporter.py ▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ 31.07.2023 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ COMMAND LINE ARGUMENTS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

# usage python scannermeshprocessing-2023/scan_folder_reporter.py -- -id SCAN_ID -p SCAN_DIRECTORY -o 1

def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
    
    # add parser rules
    parser.add_argument('-p', '--path', help="directory", default = "/System/Volumes/Data/mnt/scanDrive/takes/") 
    parser.add_argument('-cp', '--copy_issues_path', help="path to copy issues to", default = "") 
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


def print_args(args):
    for arg in vars(args):
        print_enhanced(f"{getattr(args, arg)}", label=f"{arg}", label_color="cyan")


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ DEBUG UTILS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
use_debug = True


def print_decorated(message, symbol="▬", padding=0):
    border = symbol * (len(message) + padding)
    decorated_message = f"\n{message}\n{border}"
    print(decorated_message)


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

def clear_log(path):
    log_file_path = os.path.join(path, "_log", "scan_folder_reporter_issues_log.txt")
    with open(log_file_path, "w") as log_file:
        log_file.write(f"")

def write_log(scan_id, path):
    log_file_path = os.path.join(path, "_log", "scan_folder_reporter_issues_log.txt")
    
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 0:
        with open(log_file_path, "a") as log_file:
            log_file.write(f"\n{scan_id}")
    else:
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{scan_id}")

def file_read_lines(filepath):
    if os.path.exists(filepath):
        with open(filepath) as file:
            return file.readlines()


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ UTILS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

# OS
def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        os.system(f'open "{path}"')
    else:
        # Assuming it's a Linux or Linux-like environment
        os.system(f'xdg-open "{path}"')


class Dir(NamedTuple):
    path: str
    name: str


def find_directories(directory):
    if not os.path.exists(directory):
        print_enhanced(f"Directory '{directory}' does not exist.", text_color="red", label="ERROR", label_color="red")
        return []
    directories = [Dir(entry.path, entry.name) for entry in os.scandir(directory) if entry.is_dir()]
    return directories


def find_files(directory):
    if not os.path.exists(directory):
        print_enhanced(f"Directory '{directory}' does not exist.", text_color="red", label="ERROR", label_color="red")
        return []
    files = [entry.name for entry in os.scandir(directory)]
    return files


def copy_file(source_file, destination_folder):
    try:
        # Check if the source file exists
        if not os.path.isfile(source_file):
            print_enhanced(f"Source file '{source_file}' does not exist.", text_color="red", label="ERROR", label_color="red")
            return False
        
        # Create the destination folder if it doesn't exist
        if not os.path.isdir(destination_folder):
            os.makedirs(destination_folder)
            print_enhanced(f"Destination folder '{destination_folder}' created.", label="COPY FILE DIR", label_color="green")

        # Get the filename from the source file path
        file_name = os.path.basename(source_file)

        # Construct the destination file path
        destination_file = os.path.join(destination_folder, file_name)

        # Copy the file to the destination folder
        shutil.copy2(source_file, destination_file)

        print_enhanced(f"File '{file_name}' copied to '{destination_folder}'", label="COPY FILE SUCCESS", label_color="green")
        return True

    except Exception as e:
        print_enhanced(f"copy_file failed: {e}", text_color="red", label="ERROR", label_color="red")
        return False


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ SCAN DATA ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

@dataclass
class ScanData:
    path: str = field(default='')
    index: str = field(default='')
    scan_id : str = field(default='')
    usda_file: str = field(default='')
    usda_texture_file: str = field(default='')
    cleanup_blend: str = field(default='')
    cleanup_png: str = field(default='')
    pose_gen_result: str = field(default='')
    pose_test_blend: str = field(default='')
    pose_test_png: str = field(default='')
    rig_blend: str = field(default='')


def get_scan_data(scan_id, scan_dir, scan_index):
    files = find_files(scan_dir)

    if files:
        scan_files = ScanData()
        scan_files.index = scan_index
        scan_files.path = scan_dir
        scan_files.scan_id = scan_id
        for file in files:
            if "baked_mesh.usda" == file:
                scan_files.usda_file = file

            if "baked_mesh_tex0.png" == file:
                scan_files.usda_texture_file = file

            if f"{scan_id}.blend" == file:
                scan_files.cleanup_blend = file

            if f"{scan_id}.png" == file:
                scan_files.cleanup_png = file

            if f"{scan_id}_results.txt" == file:
                scan_files.pose_gen_result = file

            if f"{scan_id}-pose_test.blend" == file:
                scan_files.pose_test_blend = file

            if f"{scan_id}-pose_test.png" == file:
                scan_files.pose_test_png = file

            if f"{scan_id}-rig.blend" == file:
                scan_files.rig_blend = file

    return scan_files


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def main():
    # MAIN VARIABLES
    print_decorated("Main variables")

    args = get_args()
    path = str(args.path)
    copy_issues_path = str(args.copy_issues_path)

    print_args(args)

    directories_data = find_directories(path)
    print_enhanced(len(directories_data), label="DIRECTORY_NAMES", label_color="cyan")

    scans_with_issues = []
    
    print_decorated("SCANS DATA")
    for i, (dir_path, dir_name) in enumerate(directories_data):
        if any(word in dir_name for word in ("turntable", "log", "test")):
            continue
        
        scan_data_path = os.path.join(path, dir_name, "photogrammetry")
        scan_data = get_scan_data(dir_name, scan_data_path, i)

        if scan_data.pose_gen_result == "":
            scans_with_issues.append(scan_data)


        """for key, value in asdict(scan_data).items():
            if value == "":
                print_enhanced (f"{value}", label=f"{key}", label_color="red", prefix="\n" if "path" in key else "")
                continue
            print_enhanced (f"{value}", label=f"{key}", label_color="cyan", prefix="\n" if "path" in key else "")"""

    print_decorated("SCANS WITH ISSUES DATA")
    print_enhanced(f"{len(scans_with_issues)}", label="AMOUNT", label_color="yellow")

    clear_log(path)
    for scan_with_issues_data in scans_with_issues:
        write_log(scan_with_issues_data.scan_id, path)

        for key, value in asdict(scan_with_issues_data).items():
            if copy_issues_path != "":
                pass
                # dest_path = os.path.join(copy_issues_path, scan_with_issues_data.scan_id, "photogrammetry")
                #copy_file()

            if value == "":
                print_enhanced (f"{value}", label=f"{key}", label_color="red", prefix="\n" if "path" in key else "")
                continue
            print_enhanced (f"{value}", label=f"{key}", label_color="cyan", prefix="\n" if "path" in key else "")
        
        face_detection_log_lines = file_read_lines(os.path.join(path, scan_with_issues_data.scan_id, "face_detection_log.txt"))
        split_lines = [line.split("\n")[0] for line in face_detection_log_lines]
        print (split_lines)

if __name__ == '__main__': 
    main()