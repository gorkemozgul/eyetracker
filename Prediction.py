import numpy as np
import os
import cv2
import pyautogui
import keras as ks
from collections import deque




def get_valid_directory():
    while True:
        directory = input("Enter the Directory for Dataset: ")
        if os.path.isdir(directory):
            return directory
        else:
            print("Directory does not exist. Please enter a valid directory.")

directory = get_valid_directory()


cascade = cv2.CascadeClassifier("haarcascade_eye.xml")
video_capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)


# Normalization 
def normalize(x):
    minn, maxx = x.min(), x.max()
    return (x - minn) / (maxx - minn)


# Eye scanning 
def scan(image_size=(32, 32)):
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to read from video capture.")
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    boxes = cascade.detectMultiScale(gray, 1.3, 10)

    if len(boxes) != 2:
        print(f"Detected {len(boxes)} eyes, expected 2.")
        return None

    eyes = []
    for box in boxes:
        x, y, w, h = box
        eye = frame[y:y + h, x:x + w]
        eye = cv2.resize(eye, image_size)
        eyes.append(eye)

    eyes = [normalize(eye)[10:-10, 5:-5] for eye in eyes]
    return (np.hstack(eyes) * 255).astype(np.uint8)

# Screen dimensions -1
width, height = 1919, 1079

# dataset
filepaths = os.listdir(directory)
X, Y = [], []
for filepath in filepaths:
    filename, _ = os.path.splitext(filepath)
    x, y = map(float, filename.split(' ')[:2])
    x /= width
    y /= height
    image_path = os.path.join(directory, filepath)
    image = cv2.imread(image_path)
    if image is not None:
        X.append(image)
        Y.append([x, y])
    else:
        print(f"Failed to read {filepath}")

X = np.array(X, dtype=np.float32) / 255.0
Y = np.array(Y, dtype=np.float32)

# Define model
model = ks.models.Sequential([
    ks.layers.Conv2D(32, 3, 2, activation='relu', input_shape=(12, 44, 3)),
    ks.layers.Conv2D(64, 2, 2, activation='relu'),
    ks.layers.Flatten(),
    ks.layers.Dense(32, activation='relu'),
    ks.layers.Dense(2, activation='sigmoid')
])
model.compile(optimizer="adam", loss="mean_squared_error")
model.summary()

# Train 

epochs = 200
for epoch in range(epochs):
    model.fit(X, Y, batch_size=32)
#smoothing cursor movement
history_length = 3
positions_queue = deque(maxlen=history_length)


def get_smoothed_position(new_x, new_y):
    positions_queue.append((new_x, new_y))
    avg_x, avg_y = np.mean(positions_queue, axis=0)
    return avg_x, avg_y


max_move_per_frame = 50


def limit_movement_speed(x, y, last_x, last_y):
    dx, dy = x - last_x, y - last_y
    distance = np.sqrt(dx ** 2 + dy ** 2)
    if distance > max_move_per_frame:
        scale_factor = max_move_per_frame / distance
        dx, dy = dx * scale_factor, dy * scale_factor
    return last_x + dx, last_y + dy


last_x, last_y = 0, 0

while True:
    eyes = scan()
    if eyes is not None:
        eyes = np.expand_dims(eyes / 255.0, axis=0)
        x, y = model.predict(eyes)[0]
        x, y = get_smoothed_position(x * width, y * height)
        x, y = limit_movement_speed(x, y, last_x, last_y)
        pyautogui.moveTo(x, y)
        last_x, last_y = x, y

# Release resources
video_capture.release()
