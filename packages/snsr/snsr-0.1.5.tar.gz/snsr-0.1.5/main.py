import pyautogui
import random
import time

def run_screensaver():
    pyautogui.FAILSAFE = False
    screen_width, screen_height = pyautogui.size()

    while True:
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        pyautogui.moveTo(x, y, duration=random.uniform(0.5, 2))
        random_key = random.choice(['a', 's', 'd', 'f', 'j', 'k', 'l'])
        pyautogui.press(random_key)
        time.sleep(random.uniform(1, 5))

if __name__ == "__main__":
    run_screensaver()
