import os
import cv2
import sys
import argparse
import numpy as np
import mediapipe as mp
from colorama import init, Fore, Style
init(autoreset=True)  # initializes colorama


print('\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬ POSE GENERATOR ▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 07.18.25 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n')


USE = "Program for running mediapipe pose estimation on an image, and creating a text file output."


def argument_parser():
    """
        Handles command-line arguments provided to the script
    """
    parser = argparse.ArgumentParser(description=USE, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-i", "--img", help="Enter the path to input image", required=True, dest="image_path")
    parser.add_argument("-o", "--out", help="Enter the path to output txt", dest="txt_path")
    parser.add_argument("-s", "--save", help="Use Save Landmarks image", default="1")

    return parser.parse_args()


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


def save_landmarks_image(mp_pose, in_img, image, results):
    image_height, image_width, _ = image.shape

    # Draw pose skeleton
    MP_DRAWING_UTILS = mp.solutions.drawing_utils
    MP_DRAWING_UTILS.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=MP_DRAWING_UTILS.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        connection_drawing_spec=MP_DRAWING_UTILS.DrawingSpec(color=(255, 0, 0), thickness=2)
    )

    # Draw landmark points
    for landmark in results.pose_landmarks.landmark:
        x = int(landmark.x * image_width)
        y = int(landmark.y * image_height)
        cv2.circle(image, (x, y), 2, (0, 0, 255), thickness=2)

    image_name = os.path.splitext(os.path.abspath(in_img))[0] + "_landmarks.jpg"
    print_enhanced(f"{image_name}", label="OUTPUT DEBUG IMAGE", label_color="cyan")
    cv2.imwrite(image_name, image)  # Save the output image


def run_pose_estimation(in_img, out_txt, cam_corners=None, use_save_landmarks_image=False):
    top_left = np.array([-0.651281, 2.0272])
    bottom_right = np.array([0.647502, -0.276031])

    if cam_corners is not None:
        # print cam_corners
        print_enhanced("Using camera corners from file", label="INFO", label_color="yellow")
        print_enhanced(f"{cam_corners}", label="CAM CORNERS", label_color="cyan")
        top_left_tuple = cam_corners['top_left']
        top_left = np.array([top_left_tuple[0], top_left_tuple[2]])

        bottom_right_tuple = cam_corners['bottom_right']
        bottom_right = np.array([bottom_right_tuple[0], bottom_right_tuple[2]])

    SCALING_FACTOR = np.abs(top_left - bottom_right) # Calculate difference between top left and bottom right corners to get the scaling factor
    IMAGE = cv2.imread(in_img)
    MP_POSE = mp.solutions.pose

    with MP_POSE.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5) as pose:

        # Convert the BGR image to RGB before processing.
        RESULTS = pose.process(cv2.cvtColor(IMAGE, cv2.COLOR_BGR2RGB))

        if not RESULTS.pose_landmarks:
            print_enhanced("No pose landmarks detected!", text_color="red", label="ERROR")
            return sys.exit(1)

        # Save Image
        if use_save_landmarks_image:
            save_landmarks_image(MP_POSE, in_img, IMAGE, RESULTS)

        # Write landmarks to output file
        print_decorated("RESULTS")
        with open(out_txt, "w") as results_file:
            for ID in MP_POSE.PoseLandmark:
                x = (RESULTS.pose_landmarks.landmark[ID].x * SCALING_FACTOR[0]) + top_left[0]
                y = ((1-RESULTS.pose_landmarks.landmark[ID].y) * SCALING_FACTOR[1]) + bottom_right[1]
                print_enhanced(f"x: {x} | y: {y}", label=f"{ID.name}", label_color="cyan")

                result_line = f"{ID.name} {x} {y}\n"
                results_file.write(result_line)


def main():
    ARGS = vars(argument_parser())

    IN_IMAGE = ARGS["image_path"]
    IN_IMAGE_NAME = os.path.splitext(IN_IMAGE)[0]
    out_txt = ARGS["txt_path"]
    CAM_CORNERS_FILENAME = f"{IN_IMAGE_NAME}_camera_corners.txt"
    USE_SAVE_LANDMARKS_IMAGE = True if ARGS["save"] == "1" else False

    if not os.path.exists(IN_IMAGE):
        print_enhanced(f"Input image {IN_IMAGE} does not exist!", text_color="red", label="ERROR")
        sys.exit(1)

    if not out_txt:
        out_txt = f"{IN_IMAGE_NAME}_results.txt"

    print_enhanced(f"{IN_IMAGE}", label="INPUT IMAGE FILEPATH", label_color="cyan")
    print_enhanced(f"{out_txt}", label="OUTPUT TXT FILEPATH", label_color="cyan")
    print_enhanced(f"{CAM_CORNERS_FILENAME}", label="CAM CORNERS FILEPATH", label_color="cyan")
    print_enhanced(f"{USE_SAVE_LANDMARKS_IMAGE}", label="USE SAVE LANDMARKS IMAGE", label_color="cyan")

    cam_corners = None
    if os.path.exists(CAM_CORNERS_FILENAME):
        print_enhanced(f"Camera corners file found: {CAM_CORNERS_FILENAME}", label="INFO", label_color="yellow")
        with open(CAM_CORNERS_FILENAME, "r") as file:
            cam_corners = {}
            for line in file:
                parts = line.strip().split()
                if parts:
                    cam_corners[parts[0]] = tuple(map(float, parts[1:]))

    run_pose_estimation(IN_IMAGE, out_txt, cam_corners, USE_SAVE_LANDMARKS_IMAGE)


if __name__ == '__main__':
    main()