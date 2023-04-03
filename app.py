import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import time

entry = None
image_label = None
machine_name_label = None
start_time_label = None
face_detection_label = None
button_load_image = None
button_reverse_image = None
button_additional_commands = None
button_resubmit_scan = None
progressbar = None
status_label = None


def load_image(scan_id):
    image_path = f"/System/Volumes/Data/mnt/scanDrive/takes/{scan_id}/photogrammetry/{scan_id}.png"
    if os.path.exists(image_path):
        image = Image.open(image_path)
        image = image.resize((int(image.width * 0.25), int(image.height * 0.25)), Image.ANTIALIAS)
        return image
    return None

def run_commands(root, commands, after_finish, run_all=False):
    def run_command():
        nonlocal commands
        nonlocal start_time
        nonlocal elapsed_time

        if commands:
            command = commands.pop(0)
            status_label.config(text="Running", fg="black")
            progressbar.start(50)

            if run_all:
                root.after(100, lambda: run_all_commands(command))
            else:
                root.after(100, lambda: run_single_command(command))
        else:
            progressbar.stop()
            total_time = time.time() - start_time
            status_label.config(text=f"Finished in {total_time:.2f}s", fg="green")
            after_finish()
            return

        elapsed_time = time.time() - start_time
        status_label.config(text=f"Running ({elapsed_time:.2f}s)", fg="black")
        root.after(100, run_command)

    def run_single_command(command):
        subprocess.run(command, shell=True, check=True)
        run_command()

    def run_all_commands(command):
        subprocess.run(command, shell=True)
        run_command()

    disable_buttons()
    start_time = time.time()
    elapsed_time = 0.0
    run_command()

def disable_buttons():
    button_load_image.config(state="disabled")
    button_reverse_image.config(state="disabled")
    button_additional_commands.config(state="disabled")
    button_resubmit_scan.config(state="disabled")

def enable_buttons():
    button_load_image.config(state="normal")
    button_reverse_image.config(state="normal")
    button_additional_commands.config(state="normal")
    button_resubmit_scan.config(state="normal")

def on_enter(event=None, show_no_image_alert=True):
    global entry
    global image_label
    global machine_name_label
    global start_time_label
    global face_detection_label
    scan_id = entry.get().strip()

    if not scan_id:
        messagebox.showerror("Error", "Please enter a valid scan ID.")
        return

    image = load_image(scan_id)

    # Read commands.sh and update machine_name_label and start_time_label
    commands_sh_path = f"/System/Volumes/Data/mnt/scanDrive/takes/{scan_id}/commands.sh"
    if os.path.exists(commands_sh_path):
        with open(commands_sh_path, "r") as file:
            lines = file.readlines()

        machine_name = lines[2].strip().split(': ')[1]
        start_time = lines[3].strip().split(': ')[1]

        machine_name_label.config(text=f"Machine Name: {machine_name}")
        start_time_label.config(text=f"Start Time: {start_time}")

        # Read face_detection_log.txt and update face_detection_label
        face_detection_log_path = f"/System/Volumes/Data/mnt/scanDrive/takes/{scan_id}/face_detection_log.txt"
        if os.path.exists(face_detection_log_path):
            with open(face_detection_log_path, "r") as file:
                lines = file.readlines()

            face_detection_result = lines[-1].strip()
            if "FAILED" in face_detection_result:
                face_detection_label.config(text="Face detection FAILED")
            else:
                face_detection_label.config(text="")

        if image is None and show_no_image_alert:
            messagebox.showerror("Error", "No image available.")
        else:
            # Update the image label
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            image_label.image = photo
    else:
        messagebox.showerror("Error", f"commands.sh not found for scan ID: {scan_id}")
    
    status_label.config(text="Running...")

def reverse_image():
    scan_id = entry.get().strip()
    commands_sh_path = f"/System/Volumes/Data/mnt/scanDrive/takes/{scan_id}/commands.sh"
    if os.path.exists(commands_sh_path):
        with open(commands_sh_path, "r") as file:
            lines = file.readlines()

        command = lines[6].strip()
        start_time = time.time()  # Capture the current time before running the command
        run_commands(root, [command], after_finish=lambda: on_reverse_image_finish(scan_id, start_time))
    else:
        messagebox.showerror("Error", f"commands.sh not found for scan ID: {scan_id}")

def on_reverse_image_finish(scan_id, start_time):
    on_enter(show_no_image_alert=False)
    status_label.config(text=f"Reverse image finished in {time.time() - start_time:.2f}s", fg="green")
    image = load_image(scan_id)
    if image is not None:
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo
    enable_buttons()

def additional_commands():
    scan_id = entry.get().strip()
    commands_sh_path = f"/System/Volumes/Data/mnt/scanDrive/takes/{scan_id}/commands.sh"
    if os.path.exists(commands_sh_path):
        with open(commands_sh_path, "r") as file:
            lines = file.readlines()

        commands = [lines[7].strip(), lines[8].strip(), lines[11].strip()]
        start_time = time.time()  # Capture the current time before running the commands
        run_commands(root, commands, after_finish=lambda: on_additional_commands_finish(start_time))
    else:
        messagebox.showerror("Error", f"commands.sh not found for scan ID: {scan_id}")

def on_additional_commands_finish(start_time):
    status_label.config(text=f"Finished in {time.time() - start_time:.2f}s", fg="green")
    enable_buttons()

def resubmit_entire_scan():
    scan_id = entry.get().strip()
    commands_sh_path = f"/System/Volumes/Data/mnt/scanDrive/takes/{scan_id}/commands.sh"
    if os.path.exists(commands_sh_path):
        with open(commands_sh_path, "r") as file:
            lines = file.readlines()

        # Read all the commands and remove the comments
        commands = [line.strip() for line in lines if not line.strip().startswith("###")]

        run_commands(root, commands, after_finish=lambda: on_enter(show_no_image_alert=False), run_all=True)
    else:
        messagebox.showerror("Error", f"commands.sh not found for scan ID: {scan_id}")

def main():
    global root
    global entry
    global image_label
    global machine_name_label
    global start_time_label
    global face_detection_label
    global button_load_image
    global button_reverse_image
    global button_additional_commands
    global button_resubmit_scan
    global progressbar
    global status_label

    root = tk.Tk()
    root.title("Scan ID Image Viewer")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack()

    entry = tk.Entry(frame, width=30)
    entry.bind("<Return>", on_enter)
    entry.grid(row=0, column=0)

    button_load_image = tk.Button(frame, text="Load Image", command=lambda: on_enter(show_no_image_alert=True))
    button_load_image.grid(row=0, column=1)

    image_label = tk.Label(frame)
    image_label.grid(row=1, column=0, columnspan=2)

    machine_name_label = tk.Label(frame, text="")
    machine_name_label.grid(row=2, column=0, columnspan=2)

    start_time_label = tk.Label(frame, text="")
    start_time_label.grid(row=3, column=0, columnspan=2)

    face_detection_label = tk.Label(frame, text="", fg="red")
    face_detection_label.grid(row=4, column=0, columnspan=2)

    button_reverse_image = tk.Button(frame, text="Reverse Image", command=reverse_image)
    button_reverse_image.grid(row=5, column=0)

    button_additional_commands = tk.Button(frame, text="Run Additional Commands", command=additional_commands)
    button_additional_commands.grid(row=5, column=1)

    button_resubmit_scan = tk.Button(frame, text="Resubmit Entire Scan", command=resubmit_entire_scan)
    button_resubmit_scan.grid(row=6, column=0, columnspan=2)

    progressbar = ttk.Progressbar(frame, mode="indeterminate")
    progressbar.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)

    status_label = tk.Label(frame, text="")
    status_label.grid(row=8, column=0, columnspan=2)

    root.mainloop()

if __name__ == "__main__":
    main()
