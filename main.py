import json
import logging
import os
import customtkinter as ctk
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.neighbors import NearestNeighbors

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


class RecommenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {
                "app_name": "SmartRec",
                "version": "1.1",
                "data_file": "data/purchases.csv"
            }

        self.title(f"{self.config['app_name']} v{self.config['version']}")
        self.geometry("550x670")
        ctk.set_appearance_mode("dark")

        self.current_recommendations = None
        self.current_user_id = None
        self.current_neighbor = None

        # Елементи інтерфейсу
        self.label = ctk.CTkLabel(self, text="Система рекомендацій товарів", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Введіть ID користувача...", width=250)
        self.user_entry.pack(pady=10)

        self.btn_rec = ctk.CTkButton(self, text="Отримати рекомендації", command=self.recommend, fg_color="#1f538d")
        self.btn_rec.pack(pady=10)

        # НОВА КНОПКА ЕКСПОРТУ
        self.btn_export = ctk.CTkButton(self, text="Експортувати звіт у JSON", command=self.export_to_json,
                                        fg_color="#d97706")
        self.btn_export.pack(pady=10)

        self.btn_plot = ctk.CTkButton(self, text="Аналітика покупок", command=self.show_plot, fg_color="#2b733f")
        self.btn_plot.pack(pady=10)

        self.result_text = ctk.CTkTextbox(self, width=450, height=200)
        self.result_text.pack(pady=20)

        logging.info("Application started. Version 1.1 updated.")

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
            neighbor_idx = int(matrix.index[indices[0][1]])

            user_goods = set(df[df['user_id'] == user_id]['product_id'])
            neighbor_goods = set(df[df['user_id'] == neighbor_idx]['product_id'])

            recommendations = [int(x) for x in list(neighbor_goods - user_goods)]

            self.current_user_id = user_id
            self.current_neighbor = neighbor_idx
            self.current_recommendations = recommendations

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
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "Помилка при обробці даних.")

    def export_to_json(self):
        """Експортує останні згенеровані дані у файл report_[id].json"""
        if self.current_user_id is None:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "ПОМИЛКА: Спочатку сформуйте рекомендації!")
            return

        report_data = {
            "app": self.config['app_name'],
            "version": self.config['version'],
            "target_user_id": self.current_user_id,
            "similar_user_id": self.current_neighbor,
            "recommended_products": self.current_recommendations
        }

        filename = f"report_user_{self.current_user_id}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)

            self.result_text.insert("end", f"\n\n[УСПІХ] Звіт збережено у файл: {filename}")
            logging.info(f"Report exported successfully for user {self.current_user_id}")
        except Exception as e:
            logging.error(f"Export error: {e}")
            self.result_text.insert("end", f"\n\n[ПОМИЛКА] Не вдалося зберегти файл.")

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