import os

os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata\\'

import pytesseract
import pyautogui
from PIL import Image
import time
import numpy as np
import cv2
import tkinter as tk
from tkinter import messagebox

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

previous_text = ""

def capture_text_from_screen(area):
    screenshot = pyautogui.screenshot(region=area)
    
    if screenshot is None:
        raise ValueError("Не удалось захватить скриншот. Скриншот пуст.")
    
    screenshot = np.array(screenshot)
    
    if screenshot.size == 0:
        raise ValueError("Скриншот пустой или недействителен.")
    
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    
    text = pytesseract.image_to_string(screenshot, lang='rus')
    return text.strip()

def compare_texts(text1, text2):
    return text1 != text2

class ScreenAreaSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Выберите область для OCR")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.attributes("-alpha", 0.5)
        self.root.overrideredirect(True)
        
        self.canvas = tk.Canvas(self.root, bg="white", width=screen_width, height=screen_height)
        self.canvas.pack()

        self.rect = None
        self.start_x = None
        self.start_y = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.area = None

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x = event.x
        end_y = event.y
        self.area = (min(self.start_x, end_x), min(self.start_y, end_y), abs(end_x - self.start_x), abs(end_y - self.start_y))

        self.canvas.delete(self.rect)

        if self.area[2] == 0 or self.area[3] == 0:
            messagebox.showerror("Ошибка", "Неверная область. Попробуйте снова.")
            self.root.quit()
        else:
            self.root.quit()

    def get_area(self):
        self.root.mainloop()
        return self.area

def select_area():
    selector = ScreenAreaSelector()
    area = selector.get_area()

    if area is None:
        print("Ошибка при выборе области.")
        exit(1)
    
    print(f"Вы выбрали область: {area}")
    return area

area = select_area()

while True:
    try:
        current_text = capture_text_from_screen(area)

        if current_text != previous_text:
            print("Текст изменился!")
            print(f"Новый текст: {current_text}")
        
        previous_text = current_text

    except ValueError as e:
        print(f"Ошибка: {e}")
        break

    time.sleep(6)
