import mss
import numpy as np
from tkinter import Tk, Canvas
from PIL import Image
import json
import os
import time

# Путь к файлу для сохранения области захвата
CONFIG_FILE = "capture_area.json"

# Функция для захвата экрана в указанной области
def capture_screen(region):
    with mss.mss() as sct:
        # Захват изображения в указанный регион
        screenshot = sct.grab(region)
        
        # Конвертируем изображение в формат PIL
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        
        return img

# Класс для создания окна с рамкой выбора региона захвата
class ScreenCapture:
    def __init__(self, master, saved_region=None):
        self.master = master
        self.master.title("Выберите область захвата")
        self.master.geometry("800x600")

        self.canvas = Canvas(master, width=800, height=600)
        self.canvas.pack()

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Если сохраненная область захвата существует, используем её
        if saved_region:
            self.region = saved_region
            self.draw_saved_region()
        else:
            self.region = None
            self.capture_started = False

    def on_click(self, event):
        """ Начало рисования рамки """
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_drag(self, event):
        """ Обновление размера рамки """
        self.end_x = event.x
        self.end_y = event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def on_release(self, event):
        """ Завершение рисования и захват области """
        self.end_x = event.x
        self.end_y = event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)
        
        # Сохраняем координаты области захвата
        self.region = {
            "top": min(self.start_y, self.end_y),
            "left": min(self.start_x, self.end_x),
            "width": abs(self.end_x - self.start_x),
            "height": abs(self.end_y - self.start_y)
        }

        self.capture_started = True
        self.master.quit()  # Закрыть окно после выбора области

    def draw_saved_region(self):
        """ Нарисовать сохраненную область на канвасе """
        self.canvas.create_rectangle(
            self.region["left"], self.region["top"],
            self.region["left"] + self.region["width"], self.region["top"] + self.region["height"],
            outline="red", width=2
        )

# Сохранение области захвата в файл
def save_region(region):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(region, f)

# Загрузка сохраненной области захвата из файла
def load_region():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

# Функция для сравнения двух изображений и поиска отличий
def find_differences(old_img_array, new_img_array):
    diff = np.abs(old_img_array - new_img_array)  # Разница по пикселям
    differing_pixels = np.argwhere(diff != 0)  # Найти все различающиеся пиксели
    return differing_pixels

# Основной блок для запуска и захвата экрана
def main():
    # Загружаем сохраненную область захвата (если есть)
    saved_region = load_region()

    if not saved_region:
        print("Не удалось загрузить область захвата.")
        return

    # Переменная для хранения предыдущего снимка экрана
    prev_img_array = None

    while True:
        # Захватываем экран в указанной области
        img = capture_screen(saved_region)

        # Преобразуем изображение в массив
        img_array = np.array(img)

        if prev_img_array is not None:
            # Сравниваем текущий и предыдущий снимки
            differing_pixels = find_differences(prev_img_array, img_array)

            if len(differing_pixels) > 0:
                print(f"Найдено {len(differing_pixels)} отличающихся пикселей.")
                # Можете добавить код для обработки отличий, например, сохранить их в файл или выводить
            else:
                print("Нет изменений.")

        # Сохраняем текущий снимок как предыдущий
        prev_img_array = img_array

        # Пауза 60 секунд
        time.sleep(5)

if __name__ == "__main__":
    main()
