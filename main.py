import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import json
import logging
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class RecommenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {"app_name": "SmartRec", "version": "1.0", "data_file": "module_1/data/purchases.csv"}

        self.title(f"{self.config['app_name']} v{self.config['version']} (Fixed)")
        self.geometry("550x600")
        ctk.set_appearance_mode("dark")

        self.label = ctk.CTkLabel(self, text="Система рекомендацій (Версія з фіксом)", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Введіть ID користувача...", width=250)
        self.user_entry.pack(pady=10)

        self.btn_rec = ctk.CTkButton(self, text="Отримати рекомендації", command=self.recommend)
        self.btn_rec.pack(pady=10)

        self.btn_plot = ctk.CTkButton(self, text="Аналітика покупок", command=self.show_plot)
        self.btn_plot.pack(pady=10)

        self.result_text = ctk.CTkTextbox(self, width=450, height=200)
        self.result_text.pack(pady=20)

    def recommend(self):
        # ФІКС БАГУ: Перевірка наявності файлу перед читанням
        if not os.path.exists(self.config['data_file']):
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "КРИТИЧНА ПОМИЛКА: Файл бази даних не знайдено!")
            logging.error("Data file missing during recommendation attempt.")
            return

        user_input = self.user_entry.get()
        if not user_input.isdigit():
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "ПОМИЛКА: Введіть числове ID!")
            return

        user_id = int(user_input)
        try:
            df = pd.read_csv(self.config['data_file'])
            matrix = df.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)

            if user_id not in matrix.index:
                self.result_text.insert("0.0", "Користувач не знайдений.")
                return

            model = NearestNeighbors(metric='cosine', n_neighbors=2).fit(matrix)
            distances, indices = model.kneighbors(matrix.loc[[user_id]])
            neighbor_idx = matrix.index[indices[0][1]]

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"Успішно! Схожість з користувачем {neighbor_idx}")
            logging.info(f"Rec success for user {user_id}")
        except Exception as e:
            logging.error(f"Error: {e}")

    def show_plot(self):
        if not os.path.exists(self.config['data_file']):
            logging.error("Cannot plot: file missing.")
            return
        df = pd.read_csv(self.config['data_file'])
        df['product_id'].value_counts().plot(kind='bar')
        plt.show()


if __name__ == "__main__":
    app = RecommenderApp()
    app.mainloop()