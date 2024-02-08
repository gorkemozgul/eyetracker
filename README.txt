A.1. Overview of Virtual Keyboard

Three keyboard implementations are written on Python. It is recommended for users to
use Python 2.8 or higher version. All three implementations are in separate files and runs
independently from each other. In the files all of the implementations runs with the certain
resolution for user needs. It is suggested that checking the resolution before running the
virtual keyboard is essential for better experience.

A.2. Installation of Virtual Keyboard

The following python packages should be installed in order to run three implementations
of keyboards.

• OpenCV (version 4.8.1 or higher)
• Numpy (version 1.26 or higher)
• pyenchant
• TextBlob
• dlib (version 19.22 required)
• math
• time
• pyglet


A.3. Overview of Eye Tracker

Calibration and Eye Tracking system both written in Python. It is recommended for users
to use Python 2.8 or higher version to run tracking without any problems. The prediction
system runs with keras which is a machine learning algorithm so it is required that correct
versions of packages is so crucial to work without any error. It is important that, calibration
must be completed before prediction algorithm. Blink detection file runs separately from eye
gaze prediction algorithm so the run order should be calibration, prediction and blink capture.

A.4. Installation of Eye Tracker

The following python packages should be installed in order to run calibration, eye track-
ing and blink capture algorithm.

• Numpy (version 1.26 or higher)
• OpenCV (version 4.8.1 or higher)
• shutil
• Listener
• tensorflow (version 2.15.0 required)
• keras (version 3.0 required)
• pyautogui
• collections
• mediapipe (version 0.10 required)
