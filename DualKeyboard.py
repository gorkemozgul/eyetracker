import cv2
import numpy as np
import dlib
from math import hypot

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def draw_letters(keyboard, letter_index, text, letter_light):
    x, y = (letter_index % 5) * 200, (letter_index // 5) * 200
    cv2.rectangle(keyboard, (x + 3, y + 3), (x + 197, y + 197), (255, 255, 255) if letter_light else (51, 51, 51), -1)
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, 10, 4)[0]
    cv2.putText(keyboard, text, (x + int((200 - text_size[0]) / 2), y + int((200 + text_size[1]) / 2)),
                cv2.FONT_HERSHEY_PLAIN, 10, (51, 51, 51) if letter_light else (255, 255, 255), 4)

def get_blinking_ratio(landmarks, eye_points):
    def midpoint(p1, p2): return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)
    left_point = (landmarks.part(eye_points[0]).x, landmarks.part(eye_points[0]).y)
    right_point = (landmarks.part(eye_points[3]).x, landmarks.part(eye_points[3]).y)
    center_top = midpoint(landmarks.part(eye_points[1]), landmarks.part(eye_points[2]))
    center_bottom = midpoint(landmarks.part(eye_points[5]), landmarks.part(eye_points[4]))
    return hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1])) / hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

def get_gaze_ratio(eye_points, landmarks, gray):
    eye_region = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in eye_points], np.int32)
    mask = np.zeros(gray.shape, np.uint8)
    cv2.polylines(mask, [eye_region], True, 255, 2)
    cv2.fillPoly(mask, [eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)
    min_x, max_x = np.min(eye_region[:, 0]), np.max(eye_region[:, 0])
    min_y, max_y = np.min(eye_region[:, 1]), np.max(eye_region[:, 1])
    gray_eye = eye[min_y: max_y, min_x: max_x]
    _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    height, width = threshold_eye.shape
    left_side_white = cv2.countNonZero(threshold_eye[0: height, 0: int(width / 2)])
    right_side_white = cv2.countNonZero(threshold_eye[0: height, int(width / 2): width])
    return left_side_white / right_side_white if right_side_white != 0 else 1

frames, letter_index, blinking_frames = 0, 0, 0
keyboard_selected, last_keyboard_selected = "left", "left"
select_keyboard_menu, keyboard_selection_frames = True, 0
text = ""
keys_set_1 = "QWERTASDFGZXCVV<"
keys_set_2 = "YUIOPHJKL_VBNM."

while True:
    ret, frame = cap.read()
    if not ret: break
    rows, cols, _ = frame.shape
    keyboard = np.zeros((600, 1000, 3), np.uint8)
    frames += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if select_keyboard_menu:
        cv2.line(keyboard, (cols // 2, 0), (cols // 2, rows), (51, 51, 51), 4)
        cv2.putText(keyboard, "LEFT", (80, 300), cv2.FONT_HERSHEY_PLAIN, 6, (255, 255, 255), 5)
        cv2.putText(keyboard, "RIGHT", (cols // 2 + 80, 300), cv2.FONT_HERSHEY_PLAIN, 6, (255, 255, 255), 5)
    
    keys_set = keys_set_1 if keyboard_selected == "left" else keys_set_2
    active_letter = keys_set[letter_index]
    
    for face in detector(gray):
        landmarks = predictor(gray, face)
        left_eye_ratio = get_blinking_ratio(landmarks, range(36, 42))
        right_eye_ratio = get_blinking_ratio(landmarks, range(42, 48))
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        if select_keyboard_menu:
            gaze_ratio = (get_gaze_ratio(range(36, 42), landmarks, gray) + get_gaze_ratio(range(42, 48), landmarks, gray)) / 2
            keyboard_selected = "right" if gaze_ratio <= 0.9 else "left"
            keyboard_selection_frames += 1
            if keyboard_selection_frames == 15:
                select_keyboard_menu = False
                frames, keyboard_selection_frames = 0, 0
            if keyboard_selected != last_keyboard_selected:
                last_keyboard_selected, keyboard_selection_frames = keyboard_selected, 0
        elif blinking_ratio > 5:
            blinking_frames += 1
            frames -= 1
            if blinking_frames == 5:
                text += " " if active_letter == "_" else active_letter if active_letter != "<" else ""
                select_keyboard_menu, blinking_frames = True, 0
        else:
            blinking_frames = 0
    
    if not select_keyboard_menu:
        if frames == 9:
            letter_index, frames = (letter_index + 1) % 15, 0
        for i in range(15):
            draw_letters(keyboard, i, keys_set[i], i == letter_index)

    cv2.putText(frame, text, (80, 100), cv2.FONT_HERSHEY_PLAIN, 9, 0, 3)
    cv2.rectangle(frame, (0, rows - 50), (int(cols * (blinking_frames / 5)), rows), (51, 51, 51), -1)
    cv2.imshow("Frame", frame)
    cv2.imshow("Virtual keyboard", keyboard)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
