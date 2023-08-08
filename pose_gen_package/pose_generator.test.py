import argparse
import cv2
import mediapipe as mp
import numpy as np
from colorama import init, Fore, Style
init(autoreset=True)  # initializes colorama
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


print('\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬ POSE GENERATOR ▬▬▬▬▬▬▬▬▬▬▬')
print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ 08.07.23 ▬▬▬▬▬▬▬▬▬▬▬▬▬▬')
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


def run_pose_estimation(in_img, out_txt):
    BG_COLOR = (192, 192, 192) # gray
    top_left = np.array([-0.651281, 2.0272])
    bottom_right = np.array([0.647502, -0.276031])
    diff = np.abs(top_left - bottom_right)

    # Load image
    image = cv2.imread(in_img)

    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5) as pose:
        
        image_height, image_width, _ = image.shape
        # Convert the BGR image to RGB before processing.
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            return
        
        # nose_coords_x, noose_coords_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width, results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height
        # print_enhanced(f"x: {nose_coords_x} y: {noose_coords_y}", label="NOSE COORDS", label_color="cyan")

        # Draw pose skeleton
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
        )

        # Draw landmark points
        for landmark in results.pose_landmarks.landmark:
            x = int(landmark.x * image_width)
            y = int(landmark.y * image_height)
            cv2.circle(image, (x, y), 2, (0, 0, 255), thickness=2)

        # Display image
        # cv2.imshow('Pose Detection Results', image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Write landmarks to output file

        print_decorated("RESULTS")
        with open(out_txt, "w") as results_file:
            for ID in mp_pose.PoseLandmark:
                x = (results.pose_landmarks.landmark[ID].x * diff[0]) + top_left[0]
                y = ((1-results.pose_landmarks.landmark[ID].y) * diff[1]) + bottom_right[1]
                print_enhanced(f"x: {x} | y: {y}", label=f"{ID.name}", label_color="cyan")

                result_line = f"{ID.name} {x} {y}\n"
                results_file.write(result_line)


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


