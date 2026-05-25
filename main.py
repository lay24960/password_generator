import random
import string
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Файл для хранения истории
        self.history_file = "password_history.json"
        self.history = self.load_history()

        # Создание интерфейса
        self.create_widgets()

        # Загрузка истории в таблицу
        self.refresh_history_table()

    def create_widgets(self):
        # Рамка для настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(settings_frame, from_=4, to=32, orient="horizontal",
                                       variable=self.length_var, command=self.update_length_label)
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)

        # Чекбоксы
        self.use_lower = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Строчные буквы (a-z)", variable=self.use_lower).grid(row=1, column=0,
                                                                                                   sticky="w", pady=2)

        self.use_upper = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Заглавные буквы (A-Z)", variable=self.use_upper).grid(row=2, column=0,
                                                                                                    sticky="w", pady=2)

        self.use_digits = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=3, column=0, sticky="w",
                                                                                           pady=2)

        self.use_special = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_special).grid(row=4, column=0,
                                                                                                       sticky="w",
                                                                                                       pady=2)

        # Кнопка генерации
        generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        generate_btn.grid(row=5, column=0, columnspan=3, pady=10)

        # Отображение сгенерированного пароля
        ttk.Label(settings_frame, text="Сгенерированный пароль:").grid(row=6, column=0, sticky="w", pady=(5, 0))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(settings_frame, textvariable=self.password_var, state="readonly", width=40)
        self.password_entry.grid(row=7, column=0, columnspan=2, sticky="ew", pady=2)
        copy_btn = ttk.Button(settings_frame, text="Копировать", command=self.copy_to_clipboard)
        copy_btn.grid(row=7, column=2, padx=5)

        # Рамка для истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица истории
        columns = ("password", "length", "timestamp")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("timestamp", text="Дата/Время")
        self.tree.column("password", width=250)
        self.tree.column("length", width=50)
        self.tree.column("timestamp", width=150)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка очистки истории
        clear_btn = ttk.Button(history_frame, text="Очистить историю", command=self.clear_history)
        clear_btn.pack(pady=5)

    def update_length_label(self, value):
        self.length_label.config(text=str(int(float(value))))

    def generate_password(self):
        # Проверка, что хотя бы один тип символов выбран
        if not any([self.use_lower.get(), self.use_upper.get(), self.use_digits.get(), self.use_special.get()]):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return

        length = int(self.length_var.get())

        # Проверка минимальной и максимальной длины
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа!")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 32 символа!")
            return

        # Формирование пула символов
        char_pool = ""
        if self.use_lower.get():
            char_pool += string.ascii_lowercase
        if self.use_upper.get():
            char_pool += string.ascii_uppercase
        if self.use_digits.get():
            char_pool += string.digits
        if self.use_special.get():
            char_pool += "!@#$%^&*"

        # Генерация пароля
        password = ''.join(random.choice(char_pool) for _ in range(length))
        self.password_var.set(password)

        # Сохранение в историю
        self.save_to_history(password, length)
        self.refresh_history_table()

    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")

    def save_to_history(self, password, length):
        """Сохранение пароля в историю (JSON)"""
        entry = {
            "password": password,
            "length": length,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
        self.save_history()

    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_history(self):
        """Сохранение истории в JSON файл"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def refresh_history_table(self):
        """Обновление таблицы истории"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление записей (сначала новые)
        for entry in reversed(self.history):
            self.tree.insert("", "end", values=(entry["password"], entry["length"], entry["timestamp"]))

    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()







