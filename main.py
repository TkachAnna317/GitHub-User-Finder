import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле поиска
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(search_frame, text="Поиск пользователя GitHub:").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_user).pack(side="left")

        # Результаты поиска
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска")
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.results_tree = ttk.Treeview(results_frame, columns=("Login", "Name", "Location"), show="headings", height=10)
        self.results_tree.heading("Login", text="Логин")
        self.results_tree.heading("Name", text="Имя")
        self.results_tree.heading("Location", text="Локация")
        self.results_tree.column("Login", width=150)
        self.results_tree.column("Name", width=200)
        self.results_tree.column("Location", width=150)
        self.results_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5, padx=20, fill="x")

        ttk.Button(button_frame, text="Добавить в избранное",
                   command=self.add_to_favorites).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Показать избранное",
                   command=self.show_favorites).pack(side="left", padx=5)

        # Список избранного
        favorites_frame = ttk.LabelFrame(self.root, text="Избранное")
        favorites_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.favorites_tree = ttk.Treeview(favorites_frame,
                                          columns=("Login", "Name", "Location"),
                                          show="headings", height=5)
        self.favorites_tree.heading("Login", text="Логин")
        self.favorites_tree.heading("Name", text="Имя")
        self.favorites_tree.heading("Location", text="Локация")
        self.favorites_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def search_user(self):
        username = self.search_entry.get().strip()

        # Валидация ввода
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"https://api.github.com/users/{username}")
            if response.status_code == 200:
                user_data = response.json()
                self.display_search_result(user_data)
            else:
                messagebox.showerror("Ошибка", f"Пользователь не найден (код: {response.status_code})")
        except requests.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к API: {e}")

    def display_search_result(self, user_data):
        # Очистка предыдущих результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Добавление нового результата
        self.results_tree.insert("", "end", values=(
            user_data.get("login", "N/A"),
            user_data.get("name", "N/A"),
            user_data.get("location", "N/A")
        ))

    def add_to_favorites(self):
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска!")
            return

        user_data = self.results_tree.item(selection[0])["values"]
        login = user_data[0]

        if login in self.favorites:
            messagebox.showinfo("Информация", "Пользователь уже в избранном!")
            return

        self.favorites[login] = {
            "name": user_data[1],
            "location": user_data[2]
        }
        self.save_favorites()
        self.refresh_favorites_display()
        messagebox.showinfo("Успех", f"Пользователь {login} добавлен в избранное!")

    def show_favorites(self):
        self.refresh_favorites_display()

    def refresh_favorites_display(self):
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)

        for login, data in self.favorites.items():
            self.favorites_tree.insert("", "end", values=(login, data["name"], data["location"]))

    def load_favorites(self):
        if os.path.exists("users.json"):
            try:
                with open("users.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_favorites(self):
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
