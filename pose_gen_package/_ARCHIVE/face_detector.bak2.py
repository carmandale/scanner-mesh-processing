import dlib
import cv2
import argparse
import os
import subprocess
import sys
import shutil
import time
import socket


print('_______________________________________')
print('_______________________________________')
print('______________FACE DETECT______________')
print('________________4.01.23________________')
print('_______________________________________')

# USAGE python3 pose_gen_package/face_detector.py -- --scan 3a08a611-ca46-2b5f-9658-9528fa4301f9

def get_args():
  parser = argparse.ArgumentParser()
  # get all script args
  _, all_arguments = parser.parse_known_args()
  double_dash_index = all_arguments.index('--')
  script_args = all_arguments[double_dash_index + 1: ]
 
  # add parser rules
  parser.add_argument('-n', '--scan', help="scan name")
  parser.add_argument('-m', '--path', help="directory", default = "/Users/administrator/groove-test/takes/") 
  parser.add_argument('-s', '--shape_predictor', help="shape predictor path", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/pose_gen_package/shape_predictor_68_face_landmarks.dat")
  parser.add_argument("-b", "--blender", help="Enter the path Blender Executable", dest="blender_path", default = "/Applications/Blender.app/Contents/MacOS/Blender")
  parser.add_argument("-r", "--rotmesh", help="Enter the path to Rotate Mesh Script", dest="rotmesh_path", default = "/Users/administrator/groove-test/software/scannermeshprocessing-2023/rotate_mesh.py")
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args

args = get_args()
scan = str(args.scan)
path = str(args.path)
blender = str(args.blender_path)
rotmesh = str(args.rotmesh_path)
blend_file = os.path.join(path, scan, "photogrammetry", f"{scan}.blend")
png_file = os.path.join(path, scan, "photogrammetry", f"{scan}.png")
software = "/Users/administrator/groove-test/software/scannermeshprocessing-2023"

shape_predictor_path = str(args.shape_predictor)


# Load the image
image_path = os.path.join(path, scan, "photogrammetry", f"{scan}.png")
# image = cv2.imread(image_path)
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# # Initialize Dlib's face detector (HOG-based) and facial landmark predictor
# face_detector = dlib.get_frontal_face_detector()
# landmark_predictor = dlib.shape_predictor(shape_predictor_path)

    # # Detect faces in the grayscale image
    # faces = face_detector(gray)

    # # Loop through the detected faces
    # faceFound = False
    # for rect in faces:
    #     # Get facial landmarks for each detected face
    #     landmarks = landmark_predictor(gray, rect)
    #     faceFound = True

    #     # Loop through the 68 facial landmarks and draw them on the image
    #     for i in range(0, landmarks.num_parts):
    #         x = landmarks.part(i).x
    #         y = landmarks.part(i).y
    #         cv2.circle(image, (x, y), 2, (0, 255, 0), -1)

def write_log(scan, path, message):
    log_file_path = os.path.join(path, scan, "photogrammetry", "face_detection_log.txt")
    machine_name = socket.gethostname()
    current_time = time.strftime("%I:%M:%S %p", time.localtime())

    with open(log_file_path, "a") as log_file:  # Changed mode from "w" to "a"
        log_file.write("\n\n")  # Add two newline characters to separate log entries
        log_file.write(f"Machine name: {machine_name}\n")
        log_file.write(f"Scan ID: {scan}\n")
        log_file.write(f"Time: {current_time}\n")
        log_file.write(message)


def detect_face(image_path):
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

def pose_generator(image_path):
    pose_gen_script = os.path.join(software, "pose_gen_package", "pose_generator.py")
    subprocess.run(["python3", pose_gen_script, "-i", image_path])

def rotate_mesh(scan, path, blender, rotmesh, new_blend_file):
    subprocess.run([blender, "-b", new_blend_file, "-P", rotmesh,"--", "--scan", scan, "--facing 0.5", "--path", path ])

def copy_and_rename_files(src, dst):
    if os.path.exists(src):
        shutil.copy(src, dst)

def move_and_rename_files(src, dst):
    if os.path.exists(src):
        shutil.move(src, dst)

faceFound = detect_face(image_path)

        
if faceFound:
    print("Face found")
    log_message = "Face detection: SUCCESS"
    write_log(scan, path, log_message)
    # cv2.imshow("Facial Landmarks", image)
    # Call pose_generator.py script
    print('calling pose_generator.py')
    pose_generator(image_path)
    # sys.exit(0)
else:
    print("No face found")
    # cv2.imshow("Facial Landmarks", image)

    # Copy and rename the blend file
    old_blend_file = blend_file
    new_blend_file = os.path.join(path, scan, "photogrammetry", f"{scan}-bak.blend")
    old_png_file = png_file
    new_png_file = os.path.join(path, scan, "photogrammetry", f"{scan}-bak.png")
    move_and_rename_files(old_blend_file, new_blend_file)
    move_and_rename_files(old_png_file, new_png_file)
    
    # Wait for 5 seconds before calling the function
    # print('waiting 5 seconds')
    # time.sleep(5)
    # Launch blender and rotate the mesh
    print('calling rotate_mesh.py')
    rotate_mesh(scan, path, blender, rotmesh, new_blend_file)

    print('running face detection again')
    faceFound = detect_face(image_path)

    if faceFound:
        print("--SUCCESS-- Face found after rotation")
        log_message = "Face detection after rotation: SUCCESS"
        write_log(scan, path, log_message)
        # Call pose_generator.py script
        print('calling pose_generator.py')
        pose_generator(image_path)
    else:
        print("No face found even after rotation")
        log_message = "Face detection after rotation: FAILED"
        write_log(scan, path, log_message)

    # cv2.imshow("Rotated Image", rotated_image)
    # sys.exit(1)
    
# cv2.imshow("Facial Landmarks", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


