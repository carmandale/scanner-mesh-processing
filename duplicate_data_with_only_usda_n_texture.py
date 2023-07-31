import argparse
import shutil
import os
from typing import NamedTuple
from colorama import init, Fore, Style
init(autoreset=True)  # initializes colorama


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
    parser.add_argument('-p', '--path', help="scans directory", default="")
    parser.add_argument('-d', '--dest_dir', help="destination directory", default="")
    parser.add_argument('-i', '--issues_txt_filepath', help="issues text filepath", default="") 
    parsed_script_args, _ = parser.parse_known_args(script_args)
    return parsed_script_args

# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ UTILS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

# DEBUG
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


# OS
class Dir(NamedTuple):
    path: str
    name: str


def find_directories(directory):
    if not os.path.exists(directory):
        print_enhanced(f"Directory '{directory}' does not exist.", text_color="red", label="ERROR", label_color="red")
        return []
    directories = [Dir(entry.path, entry.name) for entry in os.scandir(directory) if entry.is_dir()]
    return directories


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


# TEXT FILES
def read_file_lines(filepath):
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
        return lines
    except IOError as e:
        print_enhanced(f"Unable to read file: {filepath} | {e}", text_color="red", label="ERROR", label_color="red")
        return []


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ ISSUES TEXT FILE ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

# Scans with issues are currently being written manually on a text file, each line should have the last 4 digits of the scans
def get_last_digits_from_issues_text_file(filepath):
    lines = read_file_lines(filepath)
    issues_four_last_digits = [line.split(" ")[0] for line in lines]
    return issues_four_last_digits


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def main():
    # MAIN VARIABLES
    print_decorated("Main variables")

    args = get_args()
    path = str(args.path)
    dest_dir = str(args.dest_dir)
    issues_txt_filepath = str(args.issues_txt_filepath)

    print_enhanced(path, label="PATH", label_color="cyan")
    print_enhanced(dest_dir, label="DEST_DIR", label_color="cyan")
    print_enhanced(issues_txt_filepath, label="ISSUES TXT FILEPATH", label_color="cyan")

    directories_data = find_directories(path)
    print_enhanced(len(directories_data), label="DIRECTORY_NAMES", label_color="cyan")

    issues_last_digits_list = []
    if issues_txt_filepath != "":
        issues_last_digits_list = (get_last_digits_from_issues_text_file(issues_txt_filepath))

    issues_list = []
    if issues_last_digits_list:
        digits_count = len(issues_last_digits_list[0])
        for dir in directories_data:
            if dir.name[-digits_count:] in issues_last_digits_list:
                issues_list.append(dir.name)

    print_enhanced(issues_list, label="ISSUES LIST", label_color="cyan")

    dir_names = [dir.name for dir in directories_data]

    for scan_ID in dir_names:
        if any(word in scan_ID for word in ("turntable", "log", "test")):
            continue

        # To use the issues list and quickly get a duplicate for testing
        if issues_list:
            if scan_ID not in issues_list:
                continue

        usda_filepath = os.path.join(path, scan_ID, "photogrammetry", "baked_mesh.usda")
        destination_folder = os.path.join(dest_dir, scan_ID, "photogrammetry")
        copy_file(usda_filepath, destination_folder)

        texture_filepath = os.path.join(path, scan_ID, "photogrammetry", "baked_mesh_tex0.png")
        destination_folder = os.path.join(dest_dir, scan_ID, "photogrammetry")
        copy_file(texture_filepath, destination_folder)


if __name__ == '__main__': 
    main()