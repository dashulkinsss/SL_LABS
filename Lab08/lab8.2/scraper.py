import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://worldathletics.org/records/toplists/middlelong/{distance}/all/{gender}/senior/{year}"
DISCIPLINES = ["800-metres", "1500-metres", "5000-metres", "10000-metres"]
GENDERS = ["men", "women"]
YEARS = range(2001, 2025)
OUTPUT_FILE = "top_results.csv"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def safe_extract(element, default=""):
    return element.text.strip() if element else default

print("Начинаю сбор данных с World Athletics...")
print("Дисциплины:", ", ".join(DISCIPLINES))
print("Годы: с 2001 по 2024")
print("=" * 60)
total_pages = len(YEARS) * len(GENDERS) * len(DISCIPLINES)
processed = 0

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Year", "Gender", "Discipline", "Name", "Country", "Result", "Date"])
    
    for year in YEARS:
        for gender in GENDERS:
            for distance in DISCIPLINES:
                processed += 1
                progress = (processed / total_pages) * 100
                
                url = BASE_URL.format(distance=distance, gender=gender, year=year)
                
                print(f"Обрабатываю: {year}, {gender}, {distance} [{processed}/{total_pages}, {progress:.1f}%]")
                print(f"URL: {url}")
                
                try:
                    response = requests.get(url, headers=HEADERS, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    table = soup.find('table', class_='records-table')
                    
                    if not table:
                        print(f"Таблица не найдена, пропускаю...")
                        continue
                    
                    tbody = table.find('tbody')
                    if not tbody:
                        print(f"Тело таблицы не найдено, пропускаю...")
                        continue
                    
                    first_row = tbody.find('tr')
                    if not first_row:
                        print(f"Нет строк с данными, пропускаю...")
                        continue
                    
                    mark_cell = first_row.find('td', {'data-th': 'Mark'})
                    competitor_cell = first_row.find('td', {'data-th': 'Competitor'})
                    nat_cell = first_row.find('td', {'data-th': 'Nat'})
                    date_cell = first_row.find('td', {'data-th': 'Date'})
                    
                    time_result = safe_extract(mark_cell)
                    name = safe_extract(competitor_cell)
                    country = safe_extract(nat_cell)
                    competition_date = safe_extract(date_cell)
                    
                    print(f"Найден результат: {name} ({country}) - {time_result} на {competition_date}")
                    
                    writer.writerow([
                        str(year),
                        gender,
                        distance.replace("-metres", "m"),
                        name,
                        country,
                        time_result,
                        competition_date
                    ])
                    
                    time.sleep(0.5)
                    
                except requests.exceptions.RequestException as e:
                    print(f"Ошибка при запросе: {e}")
                except Exception as e:
                    print(f"Неожиданная ошибка: {e}")
                
                print("-" * 40)

print("\n" + "=" * 60)
print(f"Результаты сохранены в файл: {OUTPUT_FILE}")

try:
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) > 1:
            print(f"Сохранено записей: {len(lines) - 1} (без учета заголовка)")
        else:
            print("В файле нет данных, кроме заголовка")
except Exception as e:
    print(f"Не удалось проверить файл результатов: {e}")