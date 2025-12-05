import os
if not os.path.exists('input.txt'):
    print("ОШИБКА: Файл 'input.txt' не найден!")
    print("Создайте файл input.txt в той же папке")
    exit()
try:
    with open('input.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        lines = content.split('\n')
    
    print(f"✓ Найдено строк: {len(lines)}")
    results = []
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        print(f"Обрабатываю строку {i}: '{line}'")
        
        if line == "": 
            results.append(f"Строка {i}: (пустая)")
            continue
        
        words = line.split()
        
        longest = ""
        for word in words:
            if len(word) > len(longest):
                longest = word
        
        results.append(f"Строка {i}: '{longest}' ({len(longest)} букв)")
    
    with open('output.txt', 'w', encoding='utf-8') as file:
        for result in results:
            file.write(result + '\n')
    
    print("\n" + "." * 30)
    print("Результат:")
    print("." * 30)
    for result in results:
        print(f" {result}")
    
    print(f"\nРезультаты сохранены в файл 'output.txt'")
    
except Exception as e:
    print(f"ОШИБКА при обработке файла: {e}")

print("\n" + "." * 50)