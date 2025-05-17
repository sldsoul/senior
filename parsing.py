import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import nltk
import logging
# Скачиваем словарь для анализа тональности 
nltk.download('vader_lexicon')

# ------------------ Часть 1: Веб-парсинг ------------------

def setup_webdriver():
    try:
        options = Options()
        options.add_argument("--headless")  # запуск без графического интерфейса
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        messagebox.showerror("Ошибка драйвера", f"Не удалось запустить ChromeDriver: {str(e)}")
        return None

def open_wildberries_site(driver, url):
    try:
        driver.get(url)
        time.sleep(3)  # подождать загрузки страницы
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть сайт: {str(e)}")

def get_reviews_html(driver):
    try:
        # Прокручиваем страницу вниз для загрузки отзывов
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Ищем блоки с отзывами 
        reviews = driver.find_elements(By.CLASS_NAME, 'feedback__item')
        if not reviews:
            reviews = driver.find_elements(By.CSS_SELECTOR, '[data-tag="feedbackItem"]')
        
        html_reviews = [review.get_attribute('innerHTML') for review in reviews]
        return html_reviews if html_reviews else []
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить отзывы: {str(e)}")
        return []

def save_reviews_to_csv(reviews, filename='reviews.csv'):
    try:
        df = pd.DataFrame({'review_html': reviews})
        df.to_csv(filename, index=False)
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить отзывы: {str(e)}")

# ------------------ Часть 2: Анализ тональности ------------------

def load_reviews_from_csv(filename='reviews.csv'):
    try:
        df = pd.read_csv(filename)
        return df['review_html'].tolist()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить отзывы: {str(e)}")
        return []

def preprocess_review(html_review):
    try:
        soup = BeautifulSoup(html_review, 'html.parser')
        # Удаляем все HTML-теги и лишние пробелы
        text = ' '.join(soup.stripped_strings)
        return text if text else "Нет текста"
    except:
        return "Нет текста"

def analyze_sentiment(texts):
    try:
        sia = SentimentIntensityAnalyzer()
        results = []
        for text in texts:
            if not text or text == "Нет текста":
                results.append({'text': text, 'sentiment': 'Нет данных', 'scores': {}})
                continue
                
            polarity = sia.polarity_scores(text)
            compound = polarity['compound']
            if compound >= 0.05:
                sentiment = 'Позитивный'
            elif compound <= -0.05:
                sentiment = 'Негативный'
            else:
                sentiment = 'Нейтральный'
            results.append({'text': text, 'sentiment': sentiment, 'scores': polarity})
        return results
    except Exception as e:
        messagebox.showerror("Ошибка анализа", f"Ошибка при анализе тональности: {str(e)}")
        return []

def save_sentiment_results(results, filename='reviews_sentiment.csv'):
    try:
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить результаты: {str(e)}")

def categorize_reviews(results):
    categories = {'Позитивный': 0, 'Негативный': 0, 'Нейтральный': 0, 'Нет данных': 0}
    for r in results:
        categories[r['sentiment']] += 1
    return categories

# ------------------ Часть 3: Визуализация ------------------

def plot_sentiment_distribution(categories):
    try:
        labels = list(categories.keys())
        counts = list(categories.values())

        plt.figure(figsize=(8, 6))
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, 
                colors=['#4CAF50', '#FF5252', '#FFC107', '#9E9E9E'])
        plt.title('Распределение отзывов по тональности')
        plt.show()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось построить график: {str(e)}")

# ------------------ Часть 4: Интерфейс ------------------

