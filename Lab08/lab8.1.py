import requests
import json
import os

def main():
    # 1. Получаем и фильтруем страны
    print("Получение данных...")
    response = requests.get("https://restcountries.com/v3.1/subregion/Western%20Africa")
    countries = response.json()
    
    filtered = []
    for country in countries:
        if country.get('population', 0) > 10_000_000:
            filtered.append({
                'name': country['name']['common'],
                'capital': country.get('capital', ['-'])[0],
                'area': country.get('area', 0),
                'population': country.get('population', 0),
                'neighbors': country.get('borders', []),
                'neighbors_count': len(country.get('borders', [])),
                'flag_url': country.get('flags', {}).get('png', '')
            })
    
    # 2. Сохраняем
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    
    # 3. Находим топ-3
    top_3 = sorted(filtered, key=lambda x: x['neighbors_count'], reverse=True)[:3]
    
    print("\nТОП-3 страны по количеству соседей:")
    for i, country in enumerate(top_3, 1):
        print(f"{i}. {country['name']} - {country['neighbors_count']} соседей")
    
    # 4. Скачиваем флаги (ПРАВИЛЬНО - без дополнительных запросов)
    os.makedirs('flags', exist_ok=True)
    print("\nСкачивание флагов...")
    
    for country in top_3:
        if country['flag_url']:
            try:
                flag_data = requests.get(country['flag_url']).content
                filename = f"flags/{country['name'].replace(' ', '_')}.png"
                with open(filename, 'wb') as f:
                    f.write(flag_data)
                print(f"✓ Флаг {country['name']} сохранен")
            except:
                print(f"✗ Ошибка с флагом {country['name']}")
        else:
            print(f"✗ Нет флага для {country['name']}")
    
    print(f"\nГотово! Данные в results.json, флаги в папке flags/")

if __name__ == "__main__":
    main()