import subprocess
import argparse
import time
import os


print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬ batch_CleanUp_v4 ▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 7.28.23 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ COMMAND LINE ARGUMENTS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def get_args():
    parser = argparse.ArgumentParser()
    # get all script args
    _, all_arguments = parser.parse_known_args()
    double_dash_index = all_arguments.index('--')
    script_args = all_arguments[double_dash_index + 1:]
    
    # add parser rules
    parser.add_argument('-n', '--scan', help="scan name")
    parser.add_argument('-m', '--path', help="directory", default="/System/Volumes/Data/mnt/scanDrive/takes/") 
    parser.add_argument('-p', '--padding', help="padding", default=0.0) 
    parser.add_argument('-f', '--floor_height', help="floor_height", default=0.016)
    parser.add_argument('-cp', '--cleanup_script', help="set path of the CleanUp script")
    parser.add_argument('-cs', '--clean_start', help="to start with a clean scene", default=1)
    parser.add_argument('-is', '--index_start', help="render from index", default="0")
    parser.add_argument('-ie', '--index_end', help="render to index", default="0")
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ USEFUL FUNCTIONS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
use_debug = True

def repeat_string(string, amount):
        concatenated_string = string * amount
        return concatenated_string


def debug_function_execution_with_args(func):
    def wrapper(*args, **kwargs):
        func_name = f"{func.__name__}()".upper()

        if not use_debug:
             return func(*args, **kwargs)
        
        start_label = f"\n▬▬▬ {func_name}: START ▬▬▬"        
        print(start_label)
        print (repeat_string("▬", len(start_label) - 1))

        print(f"▬▬▬ ARGS")

        if not args:
            print ("▬▬▬▬▬▬", None)
            
        for arg in args:
            print ("▬▬▬▬▬▬", arg)

        print(f"▬▬▬ KEYWORD ARGS")
        for key, value in kwargs.items():
            print("▬▬▬▬▬▬", key, ":", value)
    
        print(f"▬▬▬ RETURN ◄")
        result = func(*args, **kwargs)

        print("▬▬▬▬▬▬", result)

        end_label = f"▬▬▬ {func_name}: END ▬▬▬"
        print (repeat_string("▬", len(end_label) - 1))
        print(end_label)
        
        return result
    return wrapper


def print_decorated(message, symbol="▬", padding=0):
    border = symbol * (len(message) + padding)
    decorated_message = f"\n{message}\n{border}"
    print(decorated_message)


def print_enhanced(text, text_color="white", label="", label_color="white", prefix="", suffix=""):
    color_code = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }

    if label == "":
        return print(f"{prefix}{color_code[text_color]}{text}{color_code['reset']}{suffix}")
    
    print(f"{prefix}[{color_code[label_color]}{label}{color_code['reset']}] {color_code[text_color]}{text}{color_code['reset']}{suffix}")


# OS
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


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

if __name__ == '__main__':
    # BACTH CLEAN UP
    IT = time.perf_counter()

    args = get_args()
    path = str(args.path)
    cleanup_script = str(args.cleanup_script)
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

        subprocess.run(["blender", "-b", "-P", cleanup_script, "--", "--scan", dir_name, "--path", path])

        MAIN_ET_S = time.perf_counter() - MAIN_IT
        print_enhanced(f"Elapsed Time: {MAIN_ET_S} sec", label=f"INDEX: {i} | NAME: {dir_name} | CleanUp_v4 FINISHED", label_color="green")

    ET_S = time.perf_counter() - IT
    ET_M = ET_S/60
    print_enhanced(f"Total Elapsed Time: {ET_M} min | {ET_S} sec", label="Batch CleanUp_v4 FINISHED", label_color="green")