import argparse
import cv2
import mediapipe as mp
import numpy as np
mp_pose = mp.solutions.pose

USE = "Program for running mediapipe pose estimation on an image, and creating a text file output."

def argument_parser():
    """
        Handles command-line arguments provided to the script
    """
    parser = argparse.ArgumentParser(description=USE, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-i", "--img", help="Enter the path to input image", required=True, dest="image_path")
    parser.add_argument("-o", "--out", help="Enter the path to output txt", dest="txt_path")

    return parser.parse_args()

def run_pose_estimation(in_img, out_txt):
    BG_COLOR = (192, 192, 192) # gray
    top_left = np.array([-0.651281, 2.0272])
    bottom_right = np.array([0.647502, -0.276031])
    diff = np.abs(top_left - bottom_right)

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

        writeFile.close()

if __name__ == '__main__':
    args = vars(argument_parser())

    in_img = args["image_path"]
    out_txt = args["txt_path"]

    if not out_txt:
        in_img_list = in_img.split('.')
        in_img_list[-2] += "_results"
        in_img_list[-1] = "txt"
        out_txt = '.'.join(in_img_list)

    print(in_img, out_txt)

    run_pose_estimation(in_img, out_txt)