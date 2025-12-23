import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import csv

class WorldAthleticsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.all_results = []
    
    def get_url(self, discipline, gender, year):
        """Генерирует URL для средних и длинных дистанций"""
        discipline_map = {
            '800': '800-metres',
            '1500': '1500-metres', 
            '5000': '5000-metres',
            '10000': '10000-metres'
        }
        
        if discipline in discipline_map:
            discipline_url = discipline_map[discipline]
            return f"https://worldathletics.org/records/toplists/middle-long/{discipline_url}/{gender}/{year}"
        
        return None
    
    def parse_table(self, html):
        """Парсит таблицу с результатами"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Находим таблицу результатов
        table = soup.find('table', class_='records-table')
        if not table:
            # Альтернативный поиск
            table = soup.find('table')
        
        if not table:
            return results
        
        # Получаем все строки таблицы
        rows = table.find_all('tr')
        
        # Пробуем найти первую строку с данными
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 5:  # Минимум 5 колонок
                # Проверяем, что первая колонка - это Rank (может быть "1" или "1.")
                rank_text = cells[0].get_text(strip=True)
                if rank_text.replace('.', '') == '1':  # Проверяем на "1" или "1."
                    # Извлекаем данные (структура может отличаться)
                    mark = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    
                    # Имя спортсмена (обычно в 3-й колонке)
                    name = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                    
                    # Страна (обычно в 4-й или 5-й колонке)
                    country = ""
                    date = ""
                    
                    # Ищем страну (обычно 3 заглавные буквы)
                    for i in range(3, min(6, len(cells))):
                        text = cells[i].get_text(strip=True)
                        if re.match(r'^[A-Z]{3}$', text):
                            country = text
                            break
                    
                    # Ищем дату (содержит месяц как JAN, FEB, MAR...)
                    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                             'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    for i in range(4, min(8, len(cells))):
                        text = cells[i].get_text(strip=True).upper()
                        if any(month in text for month in months):
                            date = cells[i].get_text(strip=True)
                            break
                    
                    # Если дата не найдена, берем последнюю колонку
                    if not date and len(cells) > 4:
                        date = cells[-1].get_text(strip=True)
                    
                    result = {
                        'rank': '1',
                        'mark': mark,
                        'name': name,
                        'country': country,
                        'date': date
                    }
                    
                    results.append(result)
                    break  # Нашли топ-1, выходим
        
        return results
    
    def scrape_discipline(self, discipline, gender, year):
        """Собирает данные для одной дисциплины, пола и года"""
        url = self.get_url(discipline, gender, year)
        
        if not url:
            print(f"  ❌ Неправильная дисциплина: {discipline}")
            return False
        
        print(f"  📡 {discipline}m - {gender} - {year}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                results = self.parse_table(response.text)
                
                if results:
                    top_result = results[0]
                    
                    # Формируем финальную запись
                    record = {
                        'Year': year,
                        'Discipline': f"{discipline}m",
                        'Gender': 'Male' if gender == 'men' else 'Female',
                        'Athlete': top_result['name'],
                        'Country': top_result['country'],
                        'Result': top_result['mark'],
                        'Date': top_result['date'],
                        'URL': url
                    }
                    
                    self.all_results.append(record)
                    
                    print(f"    ✅ {top_result['name']} ({top_result['country']}) - {top_result['mark']} - {top_result['date']}")
                    return True
                else:
                    print(f"    ⚠️  Не удалось найти данные")
                    # Попробуем альтернативный метод парсинга
                    return self.alternative_parse(response.text, url, discipline, gender, year)
            else:
                print(f"    ❌ Ошибка HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    ❌ Ошибка: {str(e)[:50]}")
            return False
    
    def alternative_parse(self, html, url, discipline, gender, year):
        """Альтернативный метод парсинга через регулярные выражения"""
        try:
            # Ищем имя спортсмена (обычно в ссылке с /athletes/)
            athlete_match = re.search(r'/athletes/[^"]+">([^<]+)<', html)
            athlete = athlete_match.group(1) if athlete_match else ""
            
            # Ищем результат (время формата x:xx.xx или xx.xx)
            time_match = re.search(r'>(\d{1,2}:\d{2}\.\d{2})<|>(\d+\.\d+)<', html)
            result = time_match.group(1) if time_match else ""
            if not result and time_match:
                result = time_match.group(2)
            
            # Ищем страну (3 заглавные буквы в таблице)
            country_match = re.search(r'<td[^>]*>([A-Z]{3})</td>', html)
            country = country_match.group(1) if country_match else ""
            
            # Ищем дату (формат DD MMM YYYY)
            date_match = re.search(r'>(\d{1,2}\s+[A-Z]{3}\s+\d{4})<', html)
            comp_date = date_match.group(1) if date_match else ""
            
            if athlete and result:
                record = {
                    'Year': year,
                    'Discipline': f"{discipline}m",
                    'Gender': 'Male' if gender == 'men' else 'Female',
                    'Athlete': athlete,
                    'Country': country,
                    'Result': result,
                    'Date': comp_date,
                    'URL': url
                }
                
                self.all_results.append(record)
                print(f"    ✅ [alt] {athlete} ({country}) - {result} - {comp_date}")
                return True
            
            return False
            
        except Exception as e:
            print(f"    ❌ Alt parse error: {str(e)[:50]}")
            return False
    
    def scrape_all(self):
        """Собирает все данные за 2001-2024 годы"""
        disciplines = ['800', '1500', '5000', '10000']
        genders = ['men', 'women']
        years = list(range(2001, 2025))
        
        total = len(disciplines) * len(genders) * len(years)
        current = 0
        
        print(f"Начинаем сбор данных...")
        print(f"Всего запросов: {total}")
        print("=" * 60)
        
        for year in years:
            print(f"\n📅 {year}:")
            
            for discipline in disciplines:
                for gender in genders:
                    current += 1
                    self.scrape_discipline(discipline, gender, year)
                    time.sleep(1.5)  # Пауза между запросами
        
        print("\n" + "=" * 60)
        print(f"✅ Сбор завершен! Собрано {len(self.all_results)} записей")
    
    def save_to_csv(self, filename='top_results.csv'):
        """Сохраняет результаты в CSV файл"""
        if not self.all_results:
            print("Нет данных для сохранения")
            return
        
        # Сортируем
        self.all_results.sort(key=lambda x: (x['Year'], x['Gender'], x['Discipline']))
        
        # Сохраняем в CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Year', 'Gender', 'Discipline', 'Athlete', 'Country', 'Result', 'Date'])
            writer.writeheader()
            writer.writerows(self.all_results)
        
        print(f"\n💾 Данные сохранены в {filename}")
        
        # Также сохраняем в читаемом виде
        self.save_human_readable()
    
    def save_human_readable(self):
        """Сохраняет результаты в читаемом текстовом формате"""
        with open('top_results_readable.txt', 'w', encoding='utf-8') as f:
            f.write("WORLD ATHLETICS - ЛУЧШИЕ РЕЗУЛЬТАТЫ (Топ-1)\n")
            f.write("Дисциплины: 800м, 1500м, 5000м, 10000м\n")
            f.write("Годы: 2001-2024\n")
            f.write("=" * 80 + "\n\n")
            
            current_year = None
            for result in self.all_results:
                if result['Year'] != current_year:
                    current_year = result['Year']
                    f.write(f"\n{' ' + str(current_year) + ' ':=^80}\n\n")
                
                gender_rus = "Мужчины" if result['Gender'] == 'Male' else "Женщины"
                f.write(f"{gender_rus} {result['Discipline']}:\n")
                f.write(f"  {result['Athlete']} ({result['Country']}) - {result['Result']}\n")
                f.write(f"  Дата: {result['Date']}\n\n")
        
        print("📄 Читаемая версия сохранена в top_results_readable.txt")

# Главная функция
def main():
    print("=" * 60)
    print("WORLD ATHLETICS - Сбор лучших результатов")
    print("Дисциплины: 800м, 1500м, 5000м, 10000м")
    print("Годы: 2001-2024")
    print("=" * 60)
    
    # Создаем скрейпер
    scraper = WorldAthleticsScraper()
    
    # Запускаем сбор данных
    scraper.scrape_all()
    
    # Сохраняем результаты
    scraper.save_to_csv()
    
    # Показываем статистику
    if scraper.all_results:
        print("\n📊 Статистика:")
        print(f"Всего записей: {len(scraper.all_results)}")
        
        # Группировка по годам
        years = set(r['Year'] for r in scraper.all_results)
        print(f"Охвачено лет: {len(years)} ({min(years)}-{max(years)})")
        
        # Показываем пример данных
        print("\nПримеры данных (первые 5 записей):")
        for i, result in enumerate(scraper.all_results[:5], 1):
            print(f"{i}. {result['Year']} {result['Gender']} {result['Discipline']}: "
                  f"{result['Athlete']} - {result['Result']}")

# Запуск
if __name__ == "__main__":
    main()