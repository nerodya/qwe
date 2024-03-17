import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ServerSettingsGUI:
    def __init__(self, root):

        self.time_limit = 60
        self.period_update = 200

        self.root = root
        self.root.title("Настройки")
        self.root.geometry("1920x1080")
        self.tab_control = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text='Настройки сервера')
        self.tab_control.add(self.tab2, text='График значений от времени')
        self.tab_control.pack(expand=1, fill="both")
        self.create_settings_tab()
        self.create_chart_tab()

        # Запуск генерации случайных значений и обновление графика
        self.values = []
        self.times = []
        self.update_graph = False
        self.generate_value()

    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.tab1)
        settings_frame.pack(padx=10, pady=10)

        time_period_label = ttk.Label(settings_frame, text="Период времени (мс):")
        time_period_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.time_period_entry = ttk.Entry(settings_frame)
        self.time_period_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        min_value_label = ttk.Label(settings_frame, text="Минимальное значение:")
        min_value_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.min_value_entry = ttk.Entry(settings_frame)
        self.min_value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        max_value_label = ttk.Label(settings_frame, text="Максимальное значение:")
        max_value_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        self.max_value_entry = ttk.Entry(settings_frame)
        self.max_value_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        apply_button = ttk.Button(settings_frame, text="Применить", command=self.apply_settings)
        apply_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # self.update_graph_var = tk.BooleanVar()
        # self.update_graph_checkbox = ttk.Checkbutton(settings_frame, text="Обновлять график",
        #                                              variable=self.update_graph_var)
        # self.update_graph_checkbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.update_graph_button = ttk.Button(settings_frame, text="Включить/выключить обновление графика", command=self.toggle_graph_update)
        self.update_graph_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def apply_settings(self):
        try:
            time_period = int(self.time_period_entry.get())
            min_value = int(self.min_value_entry.get())
            max_value = int(self.max_value_entry.get())
            if min_value >= max_value:
                raise ValueError("Минимальное значение должно быть меньше максимального")

            # self.generate_value()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def create_chart_tab(self):
        self.figure, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], marker='o')
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Время (с)")
        self.ax.set_ylabel("Значение")
        self.ax.grid(True)  # Добавляем сетку
        # Увеличиваем количество значений по осям X и Y
        self.ax.set_xticks(np.arange(0, 61, 5))  # Установим значения от 0 до 10
        self.ax.set_yticks(np.arange(0, 101, 10))  # Установим значения от 0 до 100

        self.canvas = FigureCanvasTkAgg(self.figure, self.tab2)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()

    def toggle_graph_update(self):
        self.update_graph = not self.update_graph
        if self.update_graph:
            self.generate_value()

    def generate_value(self):
        if self.update_graph:
            if len(self.times) != self.time_limit:
                self.times.append(len(self.values))
            self.values.append(random.randint(0, 100))
            if len(self.values) > self.time_limit:
                # self.times.pop(0)
                self.values.pop(0)

            print('times: ')
            print(self.times)
            print('values: ')
            print(self.values)

            self.line.set_data(self.times, self.values)
            self.ax.set_xlim(0, max(10, len(self.values)))
            self.ax.set_ylim(0, max(100, max(self.values) + 10))
            self.canvas.draw()
            self.root.after(self.period_update, self.generate_value)  # Вызываем generate_value() каждую секунду


root = tk.Tk()
app = ServerSettingsGUI(root)
root.mainloop()
