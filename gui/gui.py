# import tkinter as tk
# from tkinter import ttk
#
# class MyClass:
#     def __init__(self):
#         self.data = None
#
# class GUIApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Пример GUI")
#         self.root.geometry("400x200")  # Задаем размер окна
#         self.my_class_instance = MyClass()
#
#         self.create_widgets()
#
#     def create_widgets(self):
#         # Метка
#         label = ttk.Label(self.root, text="Введите данные:")
#         label.pack(pady=10)
#
#         # Поле ввода
#         entry = ttk.Entry(self.root, width=30)
#         entry.pack(pady=10)
#
#         # Кнопка для сохранения данных в объекте класса
#         button = ttk.Button(self.root, text="Сохранить", command=lambda: self.save_data(entry.get()))
#         button.pack(pady=10)
#
#     def save_data(self, data):
#         # Сохранение данных в объекте класса
#         self.my_class_instance.data = data
#         print(f"Данные сохранены: {self.my_class_instance.data}")
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = GUIApp(root)
#     root.mainloop()


import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DynamicHistogram:
    def __init__(self, root):
        self.root = root
        self.root.title("Динамическая гистограмма")
        self.root.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Метка
        label = ttk.Label(self.root, text="Введите данные (через запятую):")
        label.pack(pady=10)

        # Поле ввода
        self.entry_var = tk.StringVar()
        entry = ttk.Entry(self.root, textvariable=self.entry_var, width=50)
        entry.pack(pady=10)

        # Кнопка для генерации гистограммы
        button = ttk.Button(self.root, text="Генерировать гистограмму", command=self.generate_histogram)
        button.pack(pady=10)

        # Область для отображения графика
        self.plot_area = ttk.Frame(self.root)
        self.plot_area.pack(pady=10)

    def generate_histogram(self):
        # Получаем данные из поля ввода и преобразуем их в список
        data_str = self.entry_var.get()
        try:
            data = [int(x.strip()) for x in data_str.split(',')]
        except ValueError:
            tk.messagebox.showerror("Ошибка", "Пожалуйста, введите корректные целочисленные данные.")
            return

        # Создаем фигуру и подграфик
        fig, ax = plt.subplots(figsize=(8, 4))

        # Строим гистограмму
        ax.hist(data, bins=10, color='blue', alpha=0.7)

        # Настройка подписей
        ax.set_title('Динамическая гистограмма')
        ax.set_xlabel('Значения')
        ax.set_ylabel('Частота')

        # Удаляем предыдущий холст, если он существует
        for widget in self.plot_area.winfo_children():
            widget.destroy()

        # Создаем экземпляр FigureCanvasTkAgg для отображения графика в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_area)
        canvas.draw()

        # Размещаем холст в Tkinter окне
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicHistogram(root)
    root.mainloop()
