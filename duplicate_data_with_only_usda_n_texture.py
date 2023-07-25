import argparse
import shutil
import os


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
    parser.add_argument('-m', '--path', help="scans directory", default="")
    parser.add_argument('-o', '--output_dir', help="output directory", default="") 
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


def copy_file(source_file, destination_folder):
    try:
        # Check if the source file exists
        if not os.path.isfile(source_file):
            print(f"Source file '{source_file}' does not exist.")
            return False
        
        # Create the destination folder if it doesn't exist
        if not os.path.isdir(destination_folder):
            os.makedirs(destination_folder)
            print(f"Destination folder '{destination_folder}' created.")

        # Get the filename from the source file path
        file_name = os.path.basename(source_file)

        # Construct the destination file path
        destination_file = os.path.join(destination_folder, file_name)

        # Copy the file to the destination folder
        shutil.copy2(source_file, destination_file)

        print(f"File '{file_name}' copied to '{destination_folder}' successfully.")
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ SCANS WITH ISSUES ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

scan_issues_list =[
    ["3a08a0a8-263f-b4e6-afd7-03e28c760339" ,"rotated"],
    ["3a08a05f-9c00-ce7e-887f-07d6f6a8d22c" ,"rotated"],
    ["3a08a58d-45ff-7c7e-3f52-a4687b86f4f9" ,"slight rotation"],
    ["3a08a59e-70ad-4405-7692-0b1fc014c554" ,"rotated"],
    ["3a08a63b-e153-2092-8734-079812e2bc27" ,"rotated"],
    ["3a08a607-6e01-c89e-8e44-e8d7e2790edb" ,"rotated"],
    ["3a089b80-a900-650b-b459-557a0dcce1b6" ,"slight rotation"],
    ["3a089b81-35ac-6e03-5b9c-6b0c3cc94bb9" ,"slight rotation"],
    ["3a089ff9-3b21-458b-c054-77c1c9ad51c1" ,"slight rotation"],
]


# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ MAIN ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

def main():
    # MAIN VARIABLES
    print_decorated("Main variables")

    args = get_args()
    path = str(args.path)
    output_dir = str(args.output_dir)

    print_enhanced(path, label="PATH", label_color="cyan")
    print_enhanced(output_dir, label="OUTPUT_DIR", label_color="cyan")

    directories_data = find_directories(path)
    print_enhanced(directories_data[1], label="DIRECTORY_NAMES", label_color="cyan")

    issues_list = [scan_ID for scan_ID, issue in scan_issues_list]

    for scan_ID in directories_data[1]:
        if "turntable" in scan_ID:
            continue

        # To use the issues list and quickly get a duplicate for testing
        if scan_ID not in issues_list:
            continue

        usda_filepath = os.path.join(path, scan_ID, "photogrammetry", "baked_mesh.usda")
        destination_folder = os.path.join(output_dir, scan_ID, "photogrammetry")
        copy_file(usda_filepath, destination_folder)

        usda_filepath = os.path.join(path, scan_ID, "photogrammetry", "baked_mesh_tex0.png")
        destination_folder = os.path.join(output_dir, scan_ID, "photogrammetry")
        copy_file(usda_filepath, destination_folder)


if __name__ == '__main__': 
    main()