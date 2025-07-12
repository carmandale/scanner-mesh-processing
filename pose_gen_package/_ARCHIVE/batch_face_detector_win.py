import subprocess
import argparse
import time
import os
from typing import NamedTuple
from colorama import init, Fore, Style
init(autoreset=True)  # initializes colorama


print('\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬ batch_face_detector ▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬ 31.07.2023 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n')


def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
    
    # add parser rules
    parser.add_argument("-m", "--path", help="directory", default = "/Users/administrator/groove-test/takes/") 
    parser.add_argument("-sf", "--software", help="software", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/")
    parser.add_argument("-f", "--face_detector", help="face detector path", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023//pose_gen_package/face_detector_win.py")
    parser.add_argument("-sp", "--shape_predictor", help="shape predictor path", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/pose_gen_package/shape_predictor_68_face_landmarks.dat")
    parser.add_argument("-b", "--blender", help="Enter the path Blender Executable", dest="blender_path", default = "/Applications/Blender.app/Contents/MacOS/Blender")
    parser.add_argument("-r", "--rotmesh", help="Enter the path to Rotate Mesh Script", dest="rotmesh_path", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/rotate_mesh.py")
    parser.add_argument("-cs", "--clean_start", help="to start with a clean scene", default=1)
    parser.add_argument('-ip', '--issues_txt_filepath', help="issues text filepath", default="") 
    parser.add_argument("-is", "--index_start", help="from index", dest="index_start", default=0)
    parser.add_argument("-ie", "--index_end", help="to index", dest="index_end", default=0)
    parser.add_argument("-io", "--index_only", help="when provided, it will only process this index", dest="index_only", default=-1)
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


def print_args(args):
    for arg in vars(args):
        print_enhanced(f"{getattr(args, arg)}", label=f"{arg}", label_color="cyan")


def profile_execution(func):
        import timeit
        import cProfile
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Measure execution time
            execution_time = timeit.timeit(lambda: func(*args, **kwargs), number=1)
            print("Execution Time:", execution_time)

            # Profile the function using cProfile
            cProfile.runctx('func(*args, **kwargs)', globals(), locals(), sort='time')

        return wrapper

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


def file_exists(filepath):
    return os.path.isfile(filepath)


class Dir(NamedTuple):
    path: str
    name: str


def find_directories(directory):
    if not os.path.exists(directory):
        print_enhanced(f"Directory '{directory}' does not exist.", text_color="red", label="ERROR", label_color="red")
        return []
    directories = [Dir(entry.path, entry.name) for entry in os.scandir(directory) if entry.is_dir()]
    return directories


def read_file_lines(filepath):
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
        return lines
    except IOError as e:
        print_enhanced(f"Unable to read file: {filepath} | {e}", text_color="red", label="ERROR", label_color="red")
        return []


def get_scan_ids_from_issues_text_file(filepath):
    lines = [line.split("\n")[0] for line in read_file_lines(filepath)]
    return lines


if __name__ == '__main__':
    # BACTH FACE DETECTION
    IT = time.perf_counter()

    args = get_args()
    path = str(args.path)
    software = str(args.software)
    blender_path = str(args.blender_path)
    rotmesh_path = str(args.rotmesh_path)
    face_detector = str(args.face_detector)
    shape_predictor = str(args.shape_predictor)
    issues_txt_filepath = str(args.issues_txt_filepath)
    index_start = int(args.index_start)
    index_end = int(args.index_end)
    index_only = int(args.index_only)

    print_args(args)

    directories_data = find_directories(path)
    print_enhanced(len(directories_data), label="DIRECTORY_NAMES", label_color="cyan")

    scan_issues = []
    if issues_txt_filepath != "":
        scan_issues = (get_scan_ids_from_issues_text_file(issues_txt_filepath))

    issues_list = []
    if scan_issues:
        issues_list = [dir.name for dir in directories_data if dir.name in scan_issues]

    print_enhanced(issues_list, label="ISSUES LIST", label_color="cyan")

    dir_names = [dir.name for dir in directories_data]

    if index_start < 0 or index_start >= len(dir_names):
            index_start = 0

    if index_end <= 0 or index_end >= len(dir_names):
        index_end = len(dir_names) - 1

    if index_only >= 0:
        index_start = 0
        index_end = 0

    for i, scan_ID in enumerate(dir_names):
        if any(word in scan_ID for word in ("turntable", "log", "test")):
            continue

        if i < index_start:
                continue

        if i > index_end + 1:
            break

        # To use the issues list and quickly get a duplicate for testing
        if issues_list:
            if scan_ID not in issues_list:
                continue

        if index_only >= 0 and index_only != i:
            continue
        
        MAIN_IT = time.perf_counter()

        subprocess.run(["python", face_detector, "--", "--scan", scan_ID, "--path", path, "--software", software, "--shape_predictor", shape_predictor, "--blender", blender_path, "--rotmesh", rotmesh_path])

        MAIN_ET_S = time.perf_counter() - MAIN_IT
        print_enhanced(f"Elapsed Time: {MAIN_ET_S} sec", label=f"INDEX: {i} | NAME: {scan_ID} | face detector windows FINISHED", label_color="green")

    ET_S = time.perf_counter() - IT
    ET_M = ET_S/60
    print_enhanced(f"Total Elapsed Time: {ET_M} min | {ET_S} sec", label="batch face detector windows FINISHED", label_color="green")