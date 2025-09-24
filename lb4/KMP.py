import sys

def compute_prefix_function(pattern):
    """Вычисляет префикс-функцию для шаблона"""
    m = len(pattern)
    prefix = [0] * m
    k = 0
    
    for q in range(1, m):
        while k > 0 and pattern[k] != pattern[q]:
            k = prefix[k - 1]
        
        if pattern[k] == pattern[q]:
            k += 1
        
        prefix[q] = k
    
    return prefix

def kmp_search(text, pattern):
    """Находит все вхождения шаблона в текст с помощью алгоритма КМП"""
    if not pattern or not text:
        return []
    
    n = len(text)
    m = len(pattern)
    
    if m > n:
        return []
    
    prefix = compute_prefix_function(pattern)
    occurrences = []
    
    j = 0  # индекс в шаблоне
    for i in range(n):  # индекс в тексте
        while j > 0 and text[i] != pattern[j]:
            j = prefix[j - 1]
        
        if text[i] == pattern[j]:
            j += 1
        
        if j == m:
            # Найдено вхождение
            occurrences.append(i - m + 1)
            j = prefix[j - 1]  # продолжаем поиск следующих вхождений
    
    return occurrences

def main():
    print("=== Алгоритм Кнута-Морриса-Пратта (KMP) ===")
    print("Поиск всех вхождений шаблона P в тексте T")
    print()
    
    print("Введите шаблон P (длина ≤ 25000):")
    pattern = sys.stdin.readline().rstrip('\n')
    
    print("Введите текст T (длина ≤ 5000000):")
    text = sys.stdin.readline().rstrip('\n')
    
    print(f"\nПоиск шаблона '{pattern}' в тексте длиной {len(text)} символов...")
    
    # Поиск вхождений
    occurrences = kmp_search(text, pattern)
    
    # Формирование вывода
    print("\nРезультат поиска:")
    if occurrences:
        print(f"Найдено вхождений: {len(occurrences)}")
        result = ','.join(map(str, occurrences))
        print(f"Индексы начал вхождений: {result}")
    else:
        print("Вхождений не найдено: -1")

if __name__ == "__main__":
    main()