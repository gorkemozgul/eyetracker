import cv2
import mediapipe as mp
import pyautogui
import keyboard
import time

def initialize_camera():
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    return cam

def detect_blink(landmarks, frame_w, frame_h, frame):
    left = [landmarks[145], landmarks[158]]
    for landmark in left:
        x = int(landmark.x * frame_w)
        y = int(landmark.y * frame_h)
        cv2.circle(frame, (x, y), 3, (0, 255, 255))
    return (left[0].y - left[1].y) < 0.009

def main():
    cam = initialize_camera()
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pyautogui.size()
    pyautogui.FAILSAFE = False
    last_blink_time = 0

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = face_mesh.process(rgb_frame)
            landmark_points = output.multi_face_landmarks
            frame_h, frame_w, _ = frame.shape

            if landmark_points:
                landmarks = landmark_points[0].landmark
                blink_detected = detect_blink(landmarks, frame_w, frame_h, frame)


                if blink_detected:
                    current_time = time.time()
                    if current_time - last_blink_time > 2:
                        pyautogui.sleep(0.5)
                        pyautogui.click()
                        pyautogui.sleep(0.5)
                        last_blink_time = current_time

            cv2.imshow('Blinking Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
