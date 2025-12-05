# ПРОГРАММА ДЛЯ РАБОТЫ С ТЕЛЕФОНАМИ
import shelve
phones = {
    "iPhone 14": {"США": 999, "Великобритания": 949, "Германия": 1099, "Франция": 1049},
    "Samsung S23": {"США": 799, "Великобритания": 769, "Германия": 849, "Франция": 819},
    "Google Pixel 7": {"США": 599, "Великобритания": 649, "Германия": 699, "Франция": 679},
    "Xiaomi 13": {"США": 699, "Великобритания": 729, "Германия": 749, "Франция": 739},
}

print("\n1. Все телефоны:")
for name in phones:
    print(f"   - {name}")

print("\n2. Средние цены:")
avg_prices = {}
for name, prices in phones.items():
    avg = sum(prices.values()) / len(prices)
    avg_prices[name] = avg
    print(f"   - {name}: {avg:.0f}")

min_phone = min(avg_prices, key=avg_prices.get)
print(f"\n3. Удалить самый дешевый:")
print(f"{min_phone}")
del phones[min_phone]
del avg_prices[min_phone]

print("\n4. Сохраним в бд")
with shelve.open('phone_db') as db:
    db['телефоны'] = phones
    db['средние_цены'] = avg_prices
    print("Данные сохранены")
print("\n5. Проверим сохранение:")
with shelve.open('phone_db') as db:
    loaded = db['телефоны']
    print(f"Загружено телефонов: {len(loaded)}")
    for phone in loaded:
        print(f"      - {phone}")

print("\n" + "." * 50)
print("Программа завершена")
print("." * 50)