import tkinter as tk
from tkinter import ttk, messagebox
from parsing import 
def start_gui():
    root = tk.Tk()
    root.title("Анализ отзывов Wildberries")
    root.geometry("800x400")
    
    def run_analysis():
        url = entry_url.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Пожалуйста, введите URL товара на Wildberries.")
            return
        
        # Веб-парсинг
        driver = setup_webdriver()
        if not driver:
            return
            
        try:
            open_wildberries_site(driver, url)
            raw_html_reviews = get_reviews_html(driver)
            
            if not raw_html_reviews:
                messagebox.showwarning("Предупреждение", "Не найдено ни одного отзыва. Проверьте URL или попробуйте другой товар.")
                driver.quit()
                return
                
            save_reviews_to_csv(raw_html_reviews)
            
            # Анализ тональности
            texts_html = load_reviews_from_csv()
            texts = [preprocess_review(html) for html in texts_html]
            sentiment_results = analyze_sentiment(texts)
            
            if not sentiment_results:
                messagebox.showerror("Ошибка", "Не удалось проанализировать отзывы.")
                return
                
            save_sentiment_results(sentiment_results)
            categories = categorize_reviews(sentiment_results)
            
            # Вывод результатов
            result_text = f"Всего отзывов: {len(sentiment_results)}\n"
            result_text += f"Позитивных: {categories['Позитивный']}\n"
            result_text += f"Негативных: {categories['Негативный']}\n"
            result_text += f"Нейтральных: {categories['Нейтральный']}"
            
            lbl_result.config(text=result_text)
            plot_sentiment_distribution(categories)
            
        finally:
            driver.quit()

    # Интерфейс
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="Анализ отзывов Wildberries", font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=10)
    
    ttk.Label(frame, text="Введите URL товара:").grid(row=1, column=0, sticky=tk.W, pady=5)
    entry_url = ttk.Entry(frame, width=60)
    entry_url.grid(row=1, column=1, pady=5, sticky=tk.EW)
    
    btn_start = ttk.Button(frame, text="Запустить анализ", command=run_analysis)
    btn_start.grid(row=2, column=0, columnspan=2, pady=20)
    
    lbl_result = ttk.Label(frame, text="", font=('Arial', 11))
    lbl_result.grid(row=3, column=0, columnspan=2)
    
    # Пример правильного URL
    example_url = "Пример: https://www.wildberries.ru/catalog/12345678/detail.aspx"
    ttk.Label(frame, text=example_url, foreground="gray").grid(row=4, column=0, columnspan=2, pady=10)
    
    root.mainloop()

# ------------------ Основной запуск ------------------

if __name__ == "__main__":
    start_gui()