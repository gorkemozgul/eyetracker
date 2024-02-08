import cv2
import numpy as np
import os
import shutil
from pynput.mouse import Listener
from pathlib import Path


def setup_dir_path(dir_path):
    dir_path = Path(dir_path)
    if dir_path.exists():
        resp = input(f"The Directory '{dir_path}' already exists. Overwrite it? (Y/N): ").strip().upper()
        if resp == "Y":
            try:
                shutil.rmtree(dir_path)
                print(f"Old Directory '{dir_path}' removed.")
            except OSError as e:
                print(f"Error: {e}")
                return False
        else:
            print("Calibration Cancelled")
            return False

    try:
        dir_path.mkdir(parents=True)
        print(f"dir_path '{dir_path}' created successfully.")
        return True
    except OSError as e:
        print(f"Error: {e}")
        return False

dir_path = input("Enter the Directory to store the images: ")
setup_dir_path(dir_path)


def normalize(x):
    min, max = x.min(), x.max()
    return (x - min) / (max - min)

#Scanning eyes
def scan(video_capture, cascade):
    ret, frame = video_capture.read()
    if not ret:
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    boxes = cascade.detectMultiScale(gray, 1.3, 10)

    if len(boxes) == 2:
        eyes = []
        for box in boxes:
            x, y, w, h = box
            eye = frame[y:y + h, x:x + w]
            eye = cv2.resize(eye, (32, 32))
            eye = normalize(eye)
            eye = eye[10:-10, 5:-5]
            eyes.append(eye)
        return (np.hstack(eyes) * 255).astype(np.uint8)
    else:
        return None



# Calibration Points
dot_positions = []
dots_horizontal = 6
dots_vertical = 6
for i in range(dots_horizontal):
    for j in range(dots_vertical):
        x = i * 1920 // (dots_horizontal - 1)
        y = j * 1080 // (dots_vertical - 1)
        dot_positions.append((x, y))

letter_coordinates = {
    '1': (20, 150), '2': (200, 150), '3': (380, 150), '4': (560, 150),
    '5': (740, 150), '6': (920, 150), '7': (1100, 150), '8': (1280, 150),
    '9': (1460, 150), '0': (1640, 150), 'Q': (20, 320), 'W': (200, 320),
    'E': (380, 320), 'R': (560, 320), 'T': (740, 320), 'Y': (920, 320),
    'U': (1100, 320), 'I': (1280, 320), 'O': (1460, 320), 'P': (1640, 320),
    'A': (20, 490), 'S': (200, 490), 'D': (380, 490), 'F': (560, 490),
    'G': (740, 490), 'H': (920, 490), 'J': (1100, 490), 'K': (1280, 490),
    'L': (1460, 490), 'Z': (20, 660), 'X': (200, 660), 'C': (380, 660),
    'V': (560, 660), 'B': (740, 660), 'N': (920, 660), 'M': (1100, 660),
    'Space': (200, 830), 'Backspace': (1200, 660), 'Speak': (1640, 600),
    'Clear': (920, 830)
}


for position in letter_coordinates.values():
    dot_positions.append(position)


def create_black_screen_with_dot(dot_position, counter, screen_size=(1920,1080), dot_size=20):
    screen = np.zeros((screen_size[1], screen_size[0], 3), dtype=np.uint8)
    cv2.circle(screen, dot_position, dot_size, (0, 255, 0), -1)
    counter_text = str(counter)
    text_size = cv2.getTextSize(counter_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
    text_x = dot_position[0] - text_size[0] // 2
    text_y = dot_position[1] + text_size[1] // 2
    cv2.putText(screen, counter_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
    return screen

cv2.namedWindow("Screen", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Screen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
counter = len(dot_positions)


cascade = cv2.CascadeClassifier("haarcascade_eye.xml")
video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)


current_dot_index = 0


for dot_position in dot_positions:
    while True:
        # Display the black screen with a green dot
        screen = create_black_screen_with_dot(dot_position, counter)
        cv2.imshow("Screen", screen)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            eyes = scan(video_capture,cascade)
            if eyes is not None:
                filename = "{} {} eyeimage.jpeg".format(dot_position[0], dot_position[1])
                cv2.imwrite(os.path.join(dir_path, filename), eyes)
                print("Eye image captured successfully.")
                counter -= 1
                break
            else:
                print("Eye capture failed, try again.")

cv2.destroyAllWindows()
video_capture.release()
