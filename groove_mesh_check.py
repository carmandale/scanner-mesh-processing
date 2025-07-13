import os
import re
import subprocess
import bpy
import argparse
import sys
import shutil
import shlex
import select
import pty

def print_flush(*args, **kwargs):
    """
    Print function wrapper that automatically includes flush=True.
    
    Args:
        *args: Arguments to pass to print()
        **kwargs: Keyword arguments to pass to print()
    """
    kwargs['flush'] = True
    print(*args, **kwargs)

print_flush('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print_flush('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print_flush('▬▬▬▬▬▬▬▬▬ groove_mesh_check ▬▬▬▬▬▬▬▬▬▬▬')
print_flush('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 9.22.23 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print_flush('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print_flush('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')

def run_command_with_realtime_output(command: str, shell: bool = True) -> int:
    """
    Run a subprocess command with real-time output display on macOS.
    Uses multiple approaches to handle stubborn applications like groove-mesher.
    
    Args:
        command (str): The command to execute
        shell (bool): Whether to run the command through shell
    
    Returns:
        int: Return code from the subprocess
    """
    print_flush(f"Executing command: {command}")
    return _run_with_pty(command)

def _run_with_pty(command: str) -> int:
    """Run command with pseudo-terminal for real-time output on macOS."""
    try:
        # Create pseudo-terminal
        master, slave = pty.openpty()
        
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=slave,
            stderr=slave,
            stdin=slave,
            close_fds=True
        )
        
        # Close slave end in parent process
        os.close(slave)
        
        # Read output in real-time
        output_buffer = ""
        while True:
            try:
                # Check if data is available to read
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    data = os.read(master, 1024)
                    if data:
                        # Decode and handle partial lines, unify carriage returns
                        text = data.decode('utf-8', errors='ignore').replace('\r', '\n')
                        output_buffer += text
                        
                        # Process complete lines
                        while '\n' in output_buffer:
                            line, output_buffer = output_buffer.split('\n', 1)
                            if line.strip():
                                print_flush(line.strip())
                    else:
                        break
                
                # Check if process is still running
                if process.poll() is not None:
                    # Process finished, read any remaining output
                    try:
                        remaining = os.read(master, 1024)
                        if remaining:
                            text = remaining.decode('utf-8', errors='ignore').replace('\r', '\n')
                            output_buffer += text
                            # Print any remaining lines
                            for line in output_buffer.split('\n'):
                                if line.strip():
                                    print_flush(line.strip())
                    except:
                        pass
                    break
                    
            except OSError:
                break
        
        os.close(master)
        return process.wait()
        
    except Exception as e:
        print_flush(f"PTY setup failed: {e}")
        raise

def _run_with_popen(command: str, shell: bool = True) -> int:
    """Standard Popen approach with environment tweaks."""
    # Set environment variables that might help with buffering
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    env['TERM'] = 'dumb'  # Some apps behave differently with different TERM values
    
    process = subprocess.Popen(
        command,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=0,  # Try unbuffered
        env=env
    )
    
    # Read and print output line by line
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print_flush(output.strip())
    
    return process.wait()

def _run_with_script_command(command: str) -> int:
    """
    Use macOS script command to force TTY behavior.
    The script command tricks applications into thinking they're running in a real terminal.
    """
    import select, os
    # Start the process under script
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,  # Unbuffered at Python level
        universal_newlines=True
    )
    fd = process.stdout.fileno()
    buffer = ""
    # Read raw chunks and normalize both CR and LF into true lines
    while True:
        ready, _, _ = select.select([fd], [], [], 0.1)
        if ready:
            chunk = os.read(fd, 1024)
            if not chunk:
                break
            text = chunk.decode('utf-8', errors='ignore').replace('\r', '\n')
            buffer += text
            # Emit each complete line
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if line.strip():
                    print_flush(line.strip())
        elif process.poll() is not None:
            # Final flush of remaining data
            remaining = os.read(fd, 1024).decode('utf-8', errors='ignore').replace('\r', '\n')
            buffer += remaining
            for line in buffer.split('\n'):
                if line.strip():
                    print_flush(line.strip())
            break
    return process.wait()

def rename_files_to_correct_format(usdz_folder):
    pattern = r'_[a-f0-9]+(?=\.|_)'

    [os.rename(os.path.join(usdz_folder, f), os.path.join(usdz_folder, re.sub(pattern, '', f))) for f in os.listdir(usdz_folder) if re.search(pattern, f)]
    print_flush("All files renamed successfully!")

def main(scan_ID, usdz_path, prep_usdz_script_path, groove_mesher_path, source_images_path, output_path, feature_sensitivity):
    
    print_flush(f"\nscan id: {scan_ID}")
    print_flush(f"usdz_path: {usdz_path}")
    print_flush(f"prep_usdz_script_path: {prep_usdz_script_path}")
    print_flush(f"groove_mesher_path: {groove_mesher_path}")
    print_flush(f"source_images_path: {source_images_path}")
    print_flush(f"output_path: {output_path}")
    print_flush(f"feature_sensitivity: {feature_sensitivity}\n")


    # 1. Rename a file from preview.usdz to preview.zip
    usdz_folder = os.path.dirname(usdz_path)
    usdz_filename = os.path.basename(usdz_path)
    zip_path = os.path.join(usdz_folder, 'preview.zip')

    print_flush("Copying and renaming the USDZ file to a ZIP file...")
    shutil.copy(usdz_path, zip_path)  # Use shutil.copy() instead of os.rename()

    # 2. Unzip the file
    print_flush("Unzipping the file...")
    run_command_with_realtime_output(f'unzip "{zip_path}" -d "{usdz_folder}"')
 
    # M4 Specific
    # the file is saved as baked_mesh_XXXXXX.usdc, we need to rename it to baked_mesh.usdc, XXXXXX is a random number
    for root, dirs, files in os.walk(usdz_folder):
        for file in files:
            if file.startswith('baked_mesh_') and file.endswith('.usdc'):
                usdc_path = os.path.join(root, file)
                new_usdc_path = os.path.join(root, 'baked_mesh.usdc')
                print_flush(f"Renaming {usdc_path} to {new_usdc_path}")
                os.rename(usdc_path, new_usdc_path)
                usdc_path = new_usdc_path
                break

    # doing th same for the tex0.png in 0 folder
    for root, dirs, files in os.walk(os.path.join(usdz_folder, '0')):
        for file in files:
            if file.startswith('baked_mesh') and file.endswith('tex0.png'):
                tex0_path = os.path.join(root, file)
                new_tex0_path = os.path.join(root, 'baked_mesh_tex0.png')
                print_flush(f"Renaming {tex0_path} to {new_tex0_path}")
                os.rename(tex0_path, new_tex0_path)
                break


    # 3. Find the baked_mesh.usdc file
    # for root, dirs, files in os.walk(usdz_folder):
    #     for file in files:
    #         if file == 'baked_mesh.usdc':
    #             usdc_path = os.path.join(root, file)
    #             break

    # file = 'baked_mesh.usda'
    file = 'preview.usdz'
    usdc_path = os.path.join(usdz_folder, file)

    print_flush(usdc_path)

    final_usdz_dir = os.path.join(output_path, "final_usdz_files")

    # 5. Run the Blender Python script called prepUSDZ.py
    print_flush("Running the prepUSDZ.py script...")
    sys.path.append(os.path.dirname(prep_usdz_script_path))
    import prepUSDZ_v3
    result = prepUSDZ_v3.main(scan_ID, output_path, usdc_path)

    if result:
        min_x, max_x, min_y, max_y, min_z, max_z = result
        print_flush("Bounding box values received from prepUSDZ.py script.")
        print_flush(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}, min_z: {min_z}, max_z: {max_z}")

        # 6. Run the groove-mesher app with the bounding box values
        print_flush("Running groove-mesher...")
        newMinY = abs(min_y)
        newMaxY = -(abs(max_y))
        command_list = [
            f'"{groove_mesher_path}"',
            f'"{source_images_path}"',
            f'"{final_usdz_dir}"',
            "--create-final-model",
            # "--enable-object-masking",
            "--feature-sensitivity="+feature_sensitivity,
            "-d=full",
            f"--minX={min_x:.2f}",
            f"--maxX={max_x:.2f}",
            f"--minY={min_z:.2f}",
            f"--maxY={max_z:.2f}",
            f"--minZ={newMaxY:.2f}",
            f"--maxZ={newMinY:.2f}"
        ]

        command_str = ' '.join(command_list)
        run_command_with_realtime_output(command_str)

        rename_files_to_correct_format(final_usdz_dir)
        #move files from final_usdz_dir to output_path
        for file in os.listdir(final_usdz_dir):
            src_file = os.path.join(final_usdz_dir, file)
            dest_file = os.path.join(output_path, file)
            print_flush(f"Moving {src_file} to {dest_file}")
            shutil.move(src_file, dest_file)

    else:
        print_flush("Bounding box values not received from prepUSDZ.py script. Skipping groove-mesher execution.")

def get_args():
    # Remove Blender specific arguments
    argv = sys.argv[sys.argv.index("--") + 1:]

    parser = argparse.ArgumentParser(description='Process USDZ file and run a Blender script.')
    parser.add_argument('scan_id', type=str, help='Scan ID')
    parser.add_argument('usdz_path', type=str, help='Path to the preview.usdz file.')
    parser.add_argument('prep_usdz_script_path', type=str, help='Path to the prepUSDZ.py script.')
    parser.add_argument('groove_mesher_path', type=str, help='Path to the groove-mesher app.')
    parser.add_argument('source_images_path', type=str, help='Path to the scanner source images.')
    parser.add_argument('output_path', type=str, help='Path to the photogrammetry output.')
    parser.add_argument('feature_sensitivity', type=str, choices=['normal', 'high'], default='normal', help='Feature sensitivity for groove-mesher (default: normal).')

    return parser.parse_args(argv)

if __name__ == "__main__":
    args = get_args()
    main(args.scan_id, args.usdz_path, args.prep_usdz_script_path, args.groove_mesher_path, args.source_images_path, args.output_path, args.feature_sensitivity)


# previous working version
# import os
# import subprocess
# import bpy
# import argparse
# import sys
# import shutil

# def main(usdz_path, prep_usdz_script_path):
#     # 1. Rename a file from preview.usdz to preview.zip
#     usdz_folder = os.path.dirname(usdz_path)
#     usdz_filename = os.path.basename(usdz_path)
#     zip_path = os.path.join(usdz_folder, 'preview.zip')

#     print("Copying and renaming the USDZ file to a ZIP file...")
#     shutil.copy(usdz_path, zip_path)  # Use shutil.copy() instead of os.rename()

#     # 2. Unzip the file
#     print("Unzipping the file...")
#     subprocess.run(['unzip', zip_path, '-d', usdz_folder])

#     # 3. Find the baked_mesh.usdc file
#     for root, dirs, files in os.walk(usdz_folder):
#         for file in files:
#             if file == 'baked_mesh.usdc':
#                 usdc_path = os.path.join(root, file)
#                 break

#     # 4. Import the baked_mesh.usdc file
#     bpy.ops.wm.usd_import(filepath=usdc_path)

#     # 5. Run the Blender Python script called prepUSDZ.py
#     print("Running the prepUSDZ.py script...")
#     sys.path.append(os.path.dirname(prep_usdz_script_path))
#     import prepUSDZ
#     result = prepUSDZ.main()

#     if result:
#         min_x, max_x, min_y, max_y, min_z, max_z = result
#         print("Bounding box values received from prepUSDZ.py script.")
#         print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}, min_z: {min_z}, max_z: {max_z}")

#         # Run the groove-mesher program with the bounding box values
#         command = f'groove-mesher --minX {min_x} --maxX {max_x} --minY {min_y} --maxY {max_y} --minZ {min_z} --maxZ {max_z}'
#         subprocess.run(command, shell=True)
#     else:
#         print("Bounding box values not received from prepUSDZ.py script. Skipping groove-mesher execution.")

# def get_args():
#     # Remove Blender specific arguments
#     argv = sys.argv[sys.argv.index("--") + 1:]

#     parser = argparse.ArgumentParser(description='Process USDZ file and run a Blender script.')
#     parser.add_argument('usdz_path', type=str, help='Path to the preview.usdz file.')
#     parser.add_argument('prep_usdz_script_path', type=str, help='Path to the prepUSDZ.py script.')

#     return parser.parse_args(argv)

# if __name__ == "__main__":
#     args = get_args()
#     main(args.usdz_path, args.prep_usdz_script_path)