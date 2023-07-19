import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys

import argparse

parser = argparse.ArgumentParser(description="Run Shots GUI")
parser.add_argument("--scan_id", type=str, help="Scan ID")
parser.add_argument("--base_path", type=str, help="Base path for scans", default="/System/Volumes/Data/mnt/scanDrive/takes")
args = parser.parse_args()

if args.scan_id:
    scan_id = args.scan_id
if args.base_path:
    base_path = args.base_path


# Set the paths and arguments based on the original shell script
software = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023"
blender = "/Applications/Blender.app/Contents/MacOS/Blender"
posegen = "/Users/groovejones/Software/pose_gen_package/pose_generator.py"
faceDetect = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/pose_gen_package/face_detector.py"




def run_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()

def select_directory():
    global base_path
    base_path = filedialog.askdirectory()
    base_path_entry.delete(0, tk.END)
    base_path_entry.insert(0, base_path)

def run_cleanup():
    cleanup_cmd = f'"{blender}" -b -P "{software}/CleanUp.py" -- --scan {scan_id.get()} --facing 0.5 --path "{base_path}"'
    run_command(cleanup_cmd)
    messagebox.showinfo("Info", "Cleanup completed.")

def run_pose_detection():
    pose_detection_cmd = f'python3 "{faceDetect}" -- --scan {scan_id.get()} --path "{base_path}"'
    run_command(pose_detection_cmd)
    messagebox.showinfo("Info", "Pose detection completed.")

def run_rigging():
    rigging_cmd = f'"{blender}" -b -P "{software}/AddRig.py" -- --scan {scan_id.get()} --path "{base_path}"'
    run_command(rigging_cmd)
    messagebox.showinfo("Info", "Rigging completed.")

def show_picture():
    final_image_path = os.path.join(base_path, scan_id.get(), "photogrammetry", f"{scan_id.get()}.png")
    if os.path.exists(final_image_path):
        img = tk.PhotoImage(file=final_image_path)
        img_lbl.config(image=img)
        img_lbl.image = img
    else:
        messagebox.showerror("Error", "Image not found.")

def show_model():
    final_model_path = os.path.join(base_path, scan_id.get(), "photogrammetry", "baked_mesh.usda")
    if os.path.exists(final_model_path):
        subprocess.run(["qlmanage", "-p", final_model_path])
    else:
        messagebox.showerror("Error", "Model not found.")

def generate_mesh():
    if not scan_id.get():
        messagebox.showerror("Error", "Please provide a scan ID.")
        return

    detail_option = detail_level.get()
    feature_sensitivity_option = feature_sensitivity.get()
    
    preview_option = ""
    if generate_preview.get():
        preview_option = "preview"
    
    generate_mesh_cmd = f'"{software}/generateMesh.bak.sh" {scan_id.get()} "{base_path}" "{feature_sensitivity_option}" "{detail_option}" "{preview_option}"' 
    run_command(generate_mesh_cmd)
    print("==================")
    print("generate_mesh_cmd")
    print("==================")
    print(generate_mesh_cmd)
    print("==================")
    messagebox.showinfo("Info", "Mesh generated.")



root = tk.Tk()
root.title("Python GUI for 3D Scanner")

scan_id = tk.StringVar(value=args.scan_id)
base_path = args.base_path

scan_id_label = tk.Label(root, text="Scan ID:")
scan_id_label.grid(row=0, column=0, padx=5, pady=5)
scan_id_entry = tk.Entry(root, textvariable=scan_id)
scan_id_entry.grid(row=0, column=1, padx=5, pady=5)

base_path_label = tk.Label(root, text="Base Path:")
base_path_label.grid(row=1, column=0, padx=5, pady=5)
base_path_entry = tk.Entry(root, text=base_path)
base_path_entry.grid(row=1, column=1, padx=5, pady=5)
base_path_button = tk.Button(root, text="Select Directory", command=select_directory)
base_path_button.grid(row=1, column=2, padx=5, pady=5)

cleanup_button = tk.Button(root, text="Run Cleanup", command=run_cleanup)
cleanup_button.grid(row=2, column=0, padx=5, pady=5)

pose_detection_button = tk.Button(root, text="Run Pose Detection", command=run_pose_detection)
pose_detection_button.grid(row=2, column=1, padx=5, pady=5)

rigging_button = tk.Button(root, text="Run Rigging", command=run_rigging)
rigging_button.grid(row=2, column=2, padx=5, pady=5)

show_picture_button = tk.Button(root, text="Show Picture", command=show_picture)
show_picture_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

show_model_button = tk.Button(root, text="Show Model", command=show_model)
show_model_button.grid(row=3, column=2, columnspan=3, padx=5, pady=5)

generate_mesh_button = tk.Button(root, text="Generate Mesh", command=generate_mesh)
generate_mesh_button.grid(row=7, column=2, columnspan=3, padx=5, pady=5)

detail_level = tk.StringVar(value="full")
feature_sensitivity = tk.StringVar(value="normal")

detail_options = ["full", "raw"]
feature_sensitivity_options = ["normal", "high"]

detail_label = tk.Label(root, text="Detail Level:")
detail_label.grid(row=5, column=0, padx=5, pady=5)
detail_menu = tk.OptionMenu(root, detail_level, *detail_options)
detail_menu.grid(row=5, column=1, padx=5, pady=5)

feature_sensitivity_label = tk.Label(root, text="Feature Sensitivity:")
feature_sensitivity_label.grid(row=6, column=0, padx=5, pady=5)
feature_sensitivity_menu = tk.OptionMenu(root, feature_sensitivity, *feature_sensitivity_options)
feature_sensitivity_menu.grid(row=6, column=1, padx=5, pady=5)

generate_preview = tk.BooleanVar()
generate_preview_checkbox = tk.Checkbutton(root, text="Generate Preview", variable=generate_preview)
generate_preview_checkbox.grid(row=7, column=0, padx=5, pady=5)

img_lbl = tk.Label(root)
img_lbl.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
