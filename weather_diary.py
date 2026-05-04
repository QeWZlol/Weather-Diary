import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Имя файла для хранения данных
DATA_FILE = "weather_data.json"

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary (Дневник погоды)")
        self.root.geometry("800x600")

        # Список для хранения записей в памяти
        self.records = []

        # --- Интерфейс ввода ---
        input_frame = tk.LabelFrame(root, text="Новая запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_date = tk.Entry(input_frame, width=15)
        self.entry_date.grid(row=0, column=1, padx=5, pady=2)
        # Установка текущей даты по умолчанию
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))

        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_temp = tk.Entry(input_frame, width=10)
        self.entry_temp.grid(row=0, column=3, padx=5, pady=2)

        # Описание
        tk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_desc = tk.Entry(input_frame, width=40)
        self.entry_desc.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="ew")

        # Осадки
        tk.Label(input_frame, text="Осадки:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.var_precipitation = tk.BooleanVar()
        self.check_precipitation = tk.Checkbutton(input_frame, variable=self.var_precipitation, text="Да")
        self.check_precipitation.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Кнопка добавления
        btn_add = tk.Button(input_frame, text="Добавить запись", command=self.add_record, bg="#4CAF50", fg="white")
        btn_add.grid(row=2, column=3, padx=5, pady=5, sticky="e")

        # --- Интерфейс фильтрации ---
        filter_frame = tk.LabelFrame(root, text="Фильтры", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по дате (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", padx=5)
        self.entry_filter_date = tk.Entry(filter_frame, width=15)
        self.entry_filter_date.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Мин. температура (> °C):").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_filter_temp = tk.Entry(filter_frame, width=10)
        self.entry_filter_temp.grid(row=0, column=3, padx=5)

        btn_filter = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=4, padx=10)
        
        btn_reset = tk.Button(filter_frame, text="Сброс", command=self.load_data)
        btn_reset.grid(row=0, column=5, padx=5)

        # --- Таблица записей ---
        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Темп. (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")

        self.tree.column("date", width=100, anchor="center")
        self.tree.column("temp", width=80, anchor="center")
        self.tree.column("desc", width=300, anchor="w")
        self.tree.column("precip", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Загрузка данных при старте
        self.load_data()

    def validate_input(self, date_str, temp_str, desc_str):
        """Проверка корректности ввода"""
        # Проверка даты
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
            return False

        # Проверка температуры
        try:
            float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом.")
            return False

        # Проверка описания
        if not desc_str.strip():
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым.")
            return False

        return True

    def add_record(self):
        date_str = self.entry_date.get().strip()
        temp_str = self.entry_temp.get().strip()
        desc_str = self.entry_desc.get().strip()
        is_precip = self.var_precipitation.get()

        if not self.validate_input(date_str, temp_str, desc_str):
            return

        record = {
            "date": date_str,
            "temperature": float(temp_str),
            "description": desc_str,
            "precipitation": is_precip
        }

        self.records.append(record)
        self.save_to_json()
        self.refresh_table(self.records)
        
        # Очистка полей (кроме даты, иногда удобно оставлять)
        self.entry_temp.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.var_precipitation.set(False)
        messagebox.showinfo("Успех", "Запись добавлена!")

    def save_to_json(self):
        """Сохранение списка записей в JSON файл"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл: {e}")

    def load_data(self):
        """Загрузка данных из JSON файла"""
        self.records = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                messagebox.showwarning("Предупреждение", f"Ошибка чтения файла данных: {e}")
        
        # Очистка полей фильтра
        self.entry_filter_date.delete(0, tk.END)
        self.entry_filter_temp.delete(0, tk.END)
        
        self.refresh_table(self.records)

    def refresh_table(self, data_list):
        """Обновление отображения таблицы"""
        # Очистка текущих строк
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление новых строк
        for record in data_list:
            precip_text = "Да" if record["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                record["date"],
                record["temperature"],
                record["description"],
                precip_text
            ))

    def apply_filter(self):
        """Фильтрация записей"""
        filter_date = self.entry_filter_date.get().strip()
        filter_temp_str = self.entry_filter_temp.get().strip()

        filtered_records = self.records[:]

        # Фильтр по дате
        if filter_date:
            try:
                # Проверка формата даты фильтра
                datetime.strptime(filter_date, "%d.%m.%Y")
                filtered_records = [r for r in filtered_records if r["date"] == filter_date]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Неверный формат даты в фильтре.")
                return

        # Фильтр по температуре
        if filter_temp_str:
            try:
                min_temp = float(filter_temp_str)
                filtered_records = [r for r in filtered_records if r["temperature"] > min_temp]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Минимальная температура должна быть числом.")
                return

        self.refresh_table(filtered_records)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
