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
            self.config = {"app_name": "SmartRec", "version": "1.0", "data_file": "data/purchases.csv"}

        self.title(f"{self.config['app_name']} v{self.config['version']}")
        self.geometry("550x600")
        ctk.set_appearance_mode("dark")

        self.label = ctk.CTkLabel(self, text="Система рекомендацій товарів", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Введіть ID користувача...", width=250)
        self.user_entry.pack(pady=10)

        self.btn_rec = ctk.CTkButton(self, text="Отримати рекомендації", command=self.recommend, fg_color="#1f538d")
        self.btn_rec.pack(pady=10)

        self.btn_plot = ctk.CTkButton(self, text="Аналітика покупок", command=self.show_plot, fg_color="#2b733f")
        self.btn_plot.pack(pady=10)

        self.result_text = ctk.CTkTextbox(self, width=450, height=200)
        self.result_text.pack(pady=20)

        logging.info("Application started.")

    def recommend(self):
        user_input = self.user_entry.get()

        if not user_input.isdigit():
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "ПОМИЛКА: Введіть числове ID!")
            logging.warning(f"Invalid input: {user_input}")
            return

        user_id = int(user_input)

        try:
            df = pd.read_csv(self.config['data_file'])
            matrix = df.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)

            if user_id not in matrix.index:
                self.result_text.delete("0.0", "end")
                self.result_text.insert("0.0", f"Користувач {user_id} відсутній у базі.")
                return

            model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=2)
            model.fit(matrix)

            distances, indices = model.kneighbors(matrix.loc[[user_id]], n_neighbors=2)
            neighbor_idx = matrix.index[indices[0][1]]

            user_goods = set(df[df['user_id'] == user_id]['product_id'])
            neighbor_goods = set(df[df['user_id'] == neighbor_idx]['product_id'])
            recommendations = list(neighbor_goods - user_goods)

            self.result_text.delete("0.0", "end")
            output = f"Результат для користувача {user_id}:\n"
            output += f"Схожість знайдена з користувачем {neighbor_idx}.\n\n"
            if recommendations:
                output += f"Рекомендовані товари: {recommendations}"
            else:
                output += "Нових рекомендацій немає."

            self.result_text.insert("0.0", output)
            logging.info(f"Recommendations generated for user {user_id}")

        except Exception as e:
            logging.error(f"Execution error: {e}")
            self.result_text.insert("0.0", "Помилка при обробці даних.")

    def show_plot(self):
        try:
            df = pd.read_csv(self.config['data_file'])
            df['product_id'].value_counts().sort_index().plot(kind='bar', color='skyblue')
            plt.title("Популярність товарів")
            plt.xlabel("ID")
            plt.ylabel("Кількість")
            plt.tight_layout()
            plt.show()
            logging.info("Chart displayed.")
        except Exception as e:
            logging.error(f"Plot error: {e}")


if __name__ == "__main__":
    app = RecommenderApp()
    app.mainloop()