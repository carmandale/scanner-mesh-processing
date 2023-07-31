import subprocess
import argparse
import time
import os
from colorama import init, Fore, Style
init(autoreset=True)  # initializes colorama


print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬ batch_face_detector ▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')


def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1: ]
    
    # add parser rules
    parser.add_argument("-n", "--scan", help="scan name")
    parser.add_argument("-m", "--path", help="directory", default = "/System/Volumes/Data/mnt/scanDrive/takes/") 
    parser.add_argument("-sf", "--software", help="software", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/")
    parser.add_argument("-f", "--face_detector", help="face detector path", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023//pose_gen_package/face_detector_win.py")
    parser.add_argument("-sp", "--shape_predictor", help="shape predictor path", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/pose_gen_package/shape_predictor_68_face_landmarks.dat")
    parser.add_argument("-b", "--blender", help="Enter the path Blender Executable", dest="blender_path", default = "/Applications/Blender.app/Contents/MacOS/Blender")
    parser.add_argument("-r", "--rotmesh", help="Enter the path to Rotate Mesh Script", dest="rotmesh_path", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/rotate_mesh.py")
    parser.add_argument("-cs", "--clean_start", help="to start with a clean scene", default=1)
    parser.add_argument("-is", "--index_start", help="from index", dest="index_start")
    parser.add_argument("-ie", "--index_end", help="to index", dest="index_end")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


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


def find_directories(directory):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return [], []

    directories_paths = []
    directory_names = []
    for entry in os.scandir(directory):
        if entry.is_dir():
            directories_paths.append(entry.path)
            directory_names.append(entry.name)

    return directories_paths, directory_names


if __name__ == '__main__':
    # BACTH FACE DETECTION
    IT = time.perf_counter()

    args = get_args()
    print(args)
    path = str(args.path)
    software = str(args.software)
    blender_path = str(args.blender_path)
    rotmesh_path = str(args.rotmesh_path)
    face_detector = str(args.face_detector)
    shape_predictor = str(args.shape_predictor)
    index_start = int(args.index_start)
    index_end = int(args.index_end)

    print_enhanced(path, label="PATH", label_color="cyan")
    print_enhanced(index_start, label="INDEX_START", label_color="cyan")
    print_enhanced(index_end, label="INDEX_END", label_color="cyan")

    directories_data = find_directories(path)
    print_enhanced(directories_data[1], label="DIRECTORY_NAMES", label_color="cyan")

    if index_start < 0 or index_start >= len(directories_data[1]):
            index_start = 0

    if index_end <= 0 or index_end >= len(directories_data[1]):
        index_end = len(directories_data[1]) - 1

    for i, dir_name in enumerate(directories_data[1]):
        if any(word in dir_name for word in ("turntable", "log", "test")):
            continue

        if i < index_start:
                continue

        if i > index_end + 1:
            break
        
        MAIN_IT = time.perf_counter()

        subprocess.run(["python", face_detector, "--", "--scan", dir_name, "--path", path, "--software", software, "--shape_predictor", shape_predictor, "--blender", blender_path, "--rotmesh", rotmesh_path])

        MAIN_ET_S = time.perf_counter() - MAIN_IT
        print_enhanced(f"Elapsed Time: {MAIN_ET_S} sec", label=f"INDEX: {i} | NAME: {dir_name} | face detector windows FINISHED", label_color="green")

    ET_S = time.perf_counter() - IT
    ET_M = ET_S/60
    print_enhanced(f"Total Elapsed Time: {ET_M} min | {ET_S} sec", label="batch face detector windows FINISHED", label_color="green")