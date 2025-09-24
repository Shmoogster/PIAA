import sys

def compute_lps(B):
    """Вычисляет префикс-функцию (LPS - Longest Prefix Suffix) для строки B"""
    m = len(B)
    if m == 0:
        return []
    
    lps = [0] * m
    j = 0
    
    for i in range(1, m):
        while j > 0 and B[i] != B[j]:
            j = lps[j - 1]
        
        if B[i] == B[j]:
            j += 1
            lps[i] = j
        else:
            lps[i] = 0
    
    return lps

def kmp_search(A, B, lps):
    """Ищет вхождение B в удвоенной строке A с помощью алгоритма КМП"""
    j = 0
    n = len(A)
    
    for i in range(2 * n):
        while j > 0 and A[i % n] != B[j]:
            j = lps[j - 1]
        
        if A[i % n] == B[j]:
            j += 1
        
        if j == len(B):
            return i - j + 1
    
    return -1

def main():
    # Надписи при вводе
    print("Введите строку A:")
    A = sys.stdin.readline().rstrip('\n')
    
    print("Введите строку B:")
    B = sys.stdin.readline().rstrip('\n')
    
    # Проверка условий
    if len(A) != len(B):
        print("\nРезультат: -1 (строки разной длины)")
        return
    
    if len(A) == 0:
        print("\nРезультат: 0 (пустые строки)")
        return
    
    # Вычисление префикс-функции и поиск
    lps = compute_lps(B)
    result = kmp_search(A, B, lps)
    
    # Вывод результата
    if result != -1:
        print(f"\nРезультат: {result} (A является циклическим сдвигом B)")
        print(f"Сдвиг: первые {result} символов B становятся суффиксом A")
    else:
        print(f"\nРезультат: -1 (A не является циклическим сдвигом B)")

if __name__ == "__main__":
    main()