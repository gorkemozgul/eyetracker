
import cv2
import numpy as np
import pyttsx3
from gtts import gTTS
import pygame
import tempfile
from textblob import TextBlob
import enchant


engine = pyttsx3.init()
d = enchant.Dict("en_US")

mouse_x, mouse_y = 0, 0
selected_language = None  # Language selection
typed_text = ""
words=""
suggestions = []
suggestion_areas = []
def select_language():
    global selected_language

    def on_mouse(event, x, y, flags, param):
        global selected_language
        if event == cv2.EVENT_LBUTTONDOWN:
            if 50 < x < 180 and 50 < y < 100:  # English button
                selected_language = 'en'
                cv2.destroyAllWindows()
            elif 220 < x < 350 and 50 < y < 100:  # Turkish button
                selected_language = 'tr'
                cv2.destroyAllWindows()


    lang_img = np.zeros((200, 400, 3), dtype=np.uint8)
    cv2.putText(lang_img, 'Select Keyboard Language:', (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Draw buttons for English and Turkish
    cv2.rectangle(lang_img, (50, 50), (180, 100), (255, 0, 0), -1)
    cv2.putText(lang_img, 'English', (60, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.rectangle(lang_img, (220, 50), (350, 100), (0, 255, 0), -1)
    cv2.putText(lang_img, 'Turkish', (230, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.namedWindow("Language Selection")
    cv2.setMouseCallback("Language Selection", on_mouse)

    while selected_language is None:
        cv2.imshow("Language Selection", lang_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

select_language()

def speak_text(text, language):
    tts = gTTS(text=text, lang=language)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        filename = fp.name
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def draw_keys(img, key, color):
    global mouse_x, mouse_y

    x, y, w, h = key['pos']
    if x < mouse_x < x + w and y < mouse_y < y + h:
        highlight_color = (255, 200, 200)
    elif key['text'] == 'Speak':
        highlight_color = (0, 255, 0)
    else:
        if key['text'].isdigit():
            highlight_color = (0, 0, 200)
        else:
            highlight_color = color

    cv2.rectangle(img, (x, y), (x + w, y + h), highlight_color, cv2.FILLED)
    text_size = cv2.getTextSize(key['text'], cv2.FONT_HERSHEY_PLAIN, 2, 2)[0]
    text_x = x + (w - text_size[0]) // 2
    text_y = y + (h + text_size[1]) // 2
    cv2.putText(img, key['text'], (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

def on_mouse(event, x, y, flags, params):
    global mouse_x, mouse_y, typed_text, suggestions, suggestion_areas
    mouse_x, mouse_y = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        for idx, area in enumerate(suggestion_areas):
            ax, ay, aw, ah = area
            if ax < x < ax + aw and ay < y < ay + ah:
                if idx < len(suggestions):
                    #suggestion
                    words = typed_text.rsplit(' ', 1)
                    if len(words) > 1:
                        typed_text = words[0] + ' ' + suggestions[idx] + ' '
                    else:
                        typed_text = suggestions[idx] + ' '
                    return

    if event == cv2.EVENT_LBUTTONDOWN:
        for key in keys:
            kx, ky, kw, kh = key['pos']
            if kx < x < kx + kw and ky < y < ky + kh:
                if key['text'] == 'Speak':
                    speak_text(typed_text, selected_language)
                elif key['text'] == 'Space':
                    typed_text += ' '
                elif key['text'] == 'Backspace':
                    typed_text = typed_text[:-1]
                elif key['text'] == 'Clear':
                    typed_text = ''
                else:
                    typed_text += key['text']
                break

keys = []
key_width, key_height = 170,160
x_start, y_start = 20, 320
numeric_keys = "0123456789"
qwerty_keys = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
turkish_keys = ["FGIODRNHPQ", "UIEATKMLY", "JOVCZSB"]

#numeric keys
for col, key_char in enumerate(numeric_keys):
    x = x_start + (key_width + 10) * col
    y = y_start - 170
    keys.append({'text': key_char, 'pos': (x, y, key_width, key_height)})

#qwerty keyboard
if selected_language=='en':
    for row, key_row in enumerate(qwerty_keys):
        for col, key_char in enumerate(key_row):
            x = x_start + (key_width + 10) * col
            y = y_start + (key_height + 10) * row
            keys.append({'text': key_char, 'pos': (x, y, key_width, key_height)})
# f keyboard keys
if selected_language=='tr':
    for row, key_row in enumerate(turkish_keys):
        for col, key_char in enumerate(key_row):
            x = x_start + (key_width + 10) * col
            y = y_start + (key_height + 10) * row
            keys.append({'text': key_char, 'pos': (x, y, key_width, key_height)})


spacebar_width = key_width * 5 + 40
keys.append({'text': 'Space', 'pos': (x_start, y_start + (key_height + 10) * 3, spacebar_width, key_height)})


backspace_x_start = x_start + (key_width + 10) * (len("ZXCVBNM"))
backspace_width = key_width * 2 + 10
keys.append({'text': 'Backspace', 'pos': (backspace_x_start, y_start + (key_height + 10) * 2, backspace_width, key_height)})

speak_x_start = x_start + (key_width + 10) * (len("ASDFGHJKL"))
speak_width = key_width + 100
keys.append({'text': 'Speak', 'pos': (speak_x_start, y_start + (key_height + 10) * 1, speak_width, key_height*2+10)})


clear_key_width = key_width * 3
keys.append({'text': 'Clear', 'pos': (x_start-360 + (key_width + 10) * 7, y_start + (key_height + 10) * 3, clear_key_width, key_height)})


img = np.zeros((1080,1920, 3), np.uint8)

cv2.namedWindow("Virtual Keyboard")
cv2.setMouseCallback("Virtual Keyboard", on_mouse)

while True:
    img_copy = img.copy()
    cv2.rectangle(img_copy, (20, 20), (2300, 120), (200, 200, 200), cv2.FILLED)
    cv2.putText(img_copy, typed_text, (30, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

    # Get suggestions
    last_word = typed_text.split(' ')[-1]
    if last_word and not last_word.isspace():
        suggestions = d.suggest(last_word)[:6]  # Get top 3 suggestions
    else:
        suggestions = []

    # Constants
    suggestion_font_size = 2
    suggestion_width = 200
    suggestion_height = 50
    suggestion_x_start = 700
    suggestion_y = 50


    for i, suggestion in enumerate(suggestions):
        x = suggestion_x_start + suggestion_width * i
        cv2.putText(img_copy, suggestion, (x, suggestion_y), cv2.FONT_HERSHEY_PLAIN, suggestion_font_size, (0, 0, 255), 2)
        suggestion_areas.append((x, suggestion_y - suggestion_height, suggestion_width, suggestion_height))


    for key in keys:
        draw_keys(img_copy, key, (0, 0, 255))

    cv2.imshow("Virtual Keyboard", img_copy)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
