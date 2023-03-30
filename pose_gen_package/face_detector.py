import dlib
import cv2
import argparse
import os
import subprocess
import sys
import shutil


print('_______________________________________')
print('_______________________________________')
print('______________FACE DETECT______________')
print('________________3.30.23________________')
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
  parser.add_argument('-m', '--path', help="directory", default = "/System/Volumes/Data/mnt/scanDrive/takes/") 
  parser.add_argument('-s', '--shape_predictor', help="shape predictor path", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/pose_gen_package/shape_predictor_68_face_landmarks.dat")
  parser.add_argument("-b", "--blender", help="Enter the path Blender Executable", dest="blender_path", default = "/Applications/Blender.app/Contents/MacOS/Blender")
  parser.add_argument("-r", "--rotmesh", help="Enter the path to Rotate Mesh Script", dest="rotmesh_path", default = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023/rotate_mesh.py")
  parsed_script_args, _ = parser.parse_known_args(script_args)
  return parsed_script_args

args = get_args()
scan = str(args.scan)
path = str(args.path)
blender = str(args.blender_path)
rotmesh = str(args.rotmesh_path)
blend_file = os.path.join(path, scan, "photogrammetry", f"{scan}.blend")
software = "/System/Volumes/Data/mnt/scanDrive/software/scannermeshprocessing-2023"

shape_predictor_path = str(args.shape_predictor)


# Load the image
image_path = os.path.join(path, scan, "photogrammetry", f"{scan}.png")
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Initialize Dlib's face detector (HOG-based) and facial landmark predictor
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor(shape_predictor_path)

# Detect faces in the grayscale image
faces = face_detector(gray)

# Loop through the detected faces
faceFound = False
for rect in faces:
    # Get facial landmarks for each detected face
    landmarks = landmark_predictor(gray, rect)
    faceFound = True

    # Loop through the 68 facial landmarks and draw them on the image
    for i in range(0, landmarks.num_parts):
        x = landmarks.part(i).x
        y = landmarks.part(i).y
        cv2.circle(image, (x, y), 2, (0, 255, 0), -1)

def pose_generator(image_path):
    pose_gen_script = os.path.join(software, "pose_gen_package", "pose_generator.py")
    subprocess.run(["python3", pose_gen_script, "-i", image_path])

def rotate_mesh(scan, path, blender, rotmesh):
    subprocess.run([blender, "-b", blend_file, "-P", rotmesh,"--", "--scan", scan, "--facing 0.5", "--path", path ])

def copy_and_rename_blend_file(src, dst):
    if os.path.exists(src):
        shutil.copy(src, dst)


if faceFound:
    print("Face found")
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
    copy_and_rename_blend_file(old_blend_file, new_blend_file)
    
    # Launch blender and rotate the mesh
    print('calling rotate_mesh.py')
    rotate_mesh(scan, path, blender, rotmesh)
    print('calling pose_generator.py')
    pose_generator(image_path)
    # cv2.imshow("Rotated Image", rotated_image)
    # sys.exit(1)
    
# cv2.imshow("Facial Landmarks", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


