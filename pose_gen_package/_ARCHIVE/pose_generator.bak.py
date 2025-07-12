import argparse
import cv2,os
import mediapipe as mp
import numpy as np
import subprocess
mp_pose = mp.solutions.pose

USE = "Program for running mediapipe pose estimation on an image, and creating a text file output."

def argument_parser():
    """
        Handles command-line arguments provided to the script
    """
    parser = argparse.ArgumentParser(description=USE, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-i", "--img", help="Enter the path to input image", required=True, dest="image_path")
    parser.add_argument("-o", "--out", help="Enter the path to output txt", dest="txt_path")
    parser.add_argument("-b", "--blender", help="Enter the path Blender Executable", dest="blender_path")
    parser.add_argument("-m", "--rotmesh", help="Enter the path to Rotate Mesh Script", dest="rotmesh_path")

    return parser.parse_args()

def run_pose_estimation(in_img, out_txt,blender_exe,blend_file,rotmesh_py,scan,rot_the_mesh_path):
    BG_COLOR = (192, 192, 192) # gray
    top_left = np.array([-0.651281, 2.0272])
    bottom_right = np.array([0.647502, -0.276031])
    diff = np.abs(top_left - bottom_right)


    #Detecting Face
    load_img = cv2.imread(in_img)
    faces = face_detector.detectMultiScale(load_img, 1.1, 4)
    if (len(faces) <= 0):
        print('DONT have Face')
        flag_face = False
    else:
        print('HAVE Face')
        flag_face = True

    
    img_gray = cv2.cvtColor(load_img, cv2.COLOR_BGR2GRAY)
    eyes = eye_detector.detectMultiScale(img_gray, 1.1, 6)

	# pair of eyes

    if len(eyes) >= 2:
        print('HAVE Eyes', str(len(eyes)))
        flag_eye = True
        # print('flag_eye: ',flag_eye)

    else:
        print('DONT have Eyes')
        flag_eye = False
        # print('flag_eye: ',flag_eye)

    nose = nose_detector.detectMultiScale(img_gray)

    if (len(nose) <= 0):
        print('DONT have Nose')
        flag_nose = False
    else:
        print('HAVE Nose')
        flag_nose = True





    #Add Subprocess to rotate the character if no face and no eyes
    print('\nblender_exe: ', blender_exe,'\n')
    print('\nblend_file: ', blend_file,'\n')
    print('\nrotmesh_py: ', rotmesh_py,'\n')
    print('\nrot_the_mesh_path: ', rot_the_mesh_path,'\n')

    print('flag_face: ',flag_face)
    print('flag_eye: ',flag_eye)
    print('flag_nose: ',flag_nose)


    if (not flag_face and not flag_eye):
        not_face_eye = True
        not_face_nose = False
        not_eye_nose = False
    elif (not flag_face and not flag_nose):
        not_face_eye = False
        not_face_nose = True
        not_eye_nose = False
    elif (not flag_eye and not flag_nose):
        not_face_eye = False
        not_face_nose = False
        not_eye_nose = True
    else:
        not_face_eye = False
        not_face_nose = False
        not_eye_nose = False

    if not_face_eye or not_face_nose or not_eye_nose:
        print("Didnt find Eyes, rotating the mesh.")
        print('not_face_eye: ',not_face_eye)
        print('not_face_nose: ',not_face_nose)
        print('not_eye_nose: ',not_eye_nose)
        result = subprocess.run([os.path.normpath(blender_exe), "-b", os.path.normpath(blend_file), "-P", os.path.normpath(rotmesh_py),"--", "--scan", scan, "--facing 0.5", "--path", os.path.normpath(rot_the_mesh_path) ])
        print("Result: ",result)

    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5) as pose:
        image = cv2.imread(in_img)
        image_height, image_width, _ = image.shape
        # Convert the BGR image to RGB before processing.
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            return
        print(
            f'Nose coordinates: ('
            f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width}, '
            f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height})'
        )

        writeFile = open(out_txt, "w")
        for i in mp_pose.PoseLandmark:
            print("{0} {1} {2}".format(str(i).split('.')[1], (results.pose_landmarks.landmark[i].x * diff[0]) + top_left[0], ((1-results.pose_landmarks.landmark[i].y) * diff[1]) + bottom_right[1]), file=writeFile)
            # print("{0} {1} {2} {3} {4}".format(str(i).split('.')[1], (results.pose_landmarks.landmark[i].x * diff[0]) + top_left[0], ((1-results.pose_landmarks.landmark[i].y) * diff[1]) + bottom_right[1],results.pose_landmarks.landmark[i].visibility,results.pose_landmarks.landmark[i].presence), file=writeFile)
        
        #add line on the result text, informing if the picture have a face or not
        # print(str_face, file=writeFile)
        # print(str_eyes, file=writeFile)
        
        writeFile.close()

if __name__ == '__main__':
    args = vars(argument_parser())

    in_img = args["image_path"]
    out_txt = args["txt_path"]
    blender_exe = args["blender_path"]
    rotmesh_py = args["rotmesh_path"]

    if not out_txt:
        in_img_list = in_img.split('.')
        in_img_list[-2] += "_results"
        in_img_list[-1] = "txt"
        out_txt = '.'.join(in_img_list)

    in_img_list = in_img.split('.')
    in_img_list[-1] = "blend"
    blend_file = '.'.join(in_img_list)

    scan = os.path.splitext(os.path.split(in_img)[1])[0]

    rot_the_mesh_path = os.path.split(os.path.split(os.path.split(in_img)[0])[0])[0]
    

    print(in_img, out_txt)
    print('\nblend_file: ', blend_file,'\n')

    #Get opencv path location
    opencv_home = cv2.__file__
    folders = opencv_home.split(os.path.sep)[0:-1]
    path = folders[0]
    for folder in folders[1:]:
        path = path + "/" + folder
    path_for_face = path+"/data/haarcascade_frontalface_default.xml"
    path_for_eyes = path+"/data/haarcascade_eye.xml"
    # path_for_nose = path+"/data/haarcascade_mcs_nose.xml"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path_for_nose = dir_path+"/haarcascade_mcs_nose.xml"

    print('path_for_nose:', path_for_nose)
    
    if os.path.isfile(path_for_face) != True:
        raise ValueError(
            "opencv is not installed pls install using pip install opencv ", 
        path, " violated.")
    
    face_detector = cv2.CascadeClassifier(path_for_face)
    eye_detector = cv2.CascadeClassifier(path_for_eyes)
    nose_detector = cv2.CascadeClassifier(path_for_nose)

    run_pose_estimation(in_img, out_txt,blender_exe,blend_file,rotmesh_py,scan,rot_the_mesh_path)