import sys

def wagnerFischerDistance(string1: str, string2: str, replaceCost: int, insertCost: int, deleteCost: int, doubleDeleteCost: int) -> int:
    """Ищет минимальное редакционное расстояние с учетом правила треугольника и операции удаления двух символов"""
    n, m = len(string1), len(string2)
    
    # Проверяем правило треугольника для весов операций
    if replaceCost > deleteCost + insertCost:
        replaceCost = deleteCost + insertCost
    
    # Матрица динамического программирования
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    # Инициализация первой строки и столбца
    for i in range(n + 1):
        dp[i][0] = i * deleteCost
    for j in range(m + 1):
        dp[0][j] = j * insertCost
    
    # Заполнение матрицы
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            operations = []
            
            # Удаление одного символа из string1
            operations.append(dp[i-1][j] + deleteCost)
            
            # Вставка одного символа в string1
            operations.append(dp[i][j-1] + insertCost)
            
            # Замена или совпадение символов
            if string1[i-1] == string2[j-1]:
                operations.append(dp[i-1][j-1])  # Совпадение
            else:
                operations.append(dp[i-1][j-1] + replaceCost)  # Замена
            
            # Операция удаления двух последовательных символов (4-я операция)
            if i >= 2 and string1[i-1] == string1[i-2]:
                operations.append(dp[i-2][j] + doubleDeleteCost)
            
            dp[i][j] = min(operations)
    
    return dp[n][m]

def wagnerFisherEditorialPrescription(string1: str, string2: str, replaceCost: int, insertCost: int, deleteCost: int, doubleDeleteCost: int) -> str:
    """Определяет редакционное предписание с учетом операции удаления двух символов"""
    n, m = len(string1), len(string2)
    
    if replaceCost > deleteCost + insertCost:
        replaceCost = deleteCost + insertCost
    
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    prescript = [[""] * (m + 1) for _ in range(n + 1)]
    
    # Инициализация
    for i in range(n + 1):
        dp[i][0] = i * deleteCost
        prescript[i][0] = "D" * i
    
    for j in range(m + 1):
        dp[0][j] = j * insertCost
        prescript[0][j] = "I" * j
    
    # Заполнение матриц
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            min_cost = float('inf')
            best_prescript = ""
            
            # Удаление одного символа
            cost_del = dp[i-1][j] + deleteCost
            if cost_del < min_cost:
                min_cost = cost_del
                best_prescript = prescript[i-1][j] + "D"
            
            # Вставка одного символа
            cost_ins = dp[i][j-1] + insertCost
            if cost_ins < min_cost:
                min_cost = cost_ins
                best_prescript = prescript[i][j-1] + "I"
            
            # Замена или совпадение
            if string1[i-1] == string2[j-1]:
                cost_rep = dp[i-1][j-1]
                if cost_rep < min_cost:
                    min_cost = cost_rep
                    best_prescript = prescript[i-1][j-1] + "M"
            else:
                cost_rep = dp[i-1][j-1] + replaceCost
                if cost_rep < min_cost:
                    min_cost = cost_rep
                    best_prescript = prescript[i-1][j-1] + "R"
            
            # Удаление двух символов (4-я операция со своей стоимостью)
            if i >= 2 and string1[i-1] == string1[i-2]:
                cost_dd = dp[i-2][j] + doubleDeleteCost
                if cost_dd < min_cost:
                    min_cost = cost_dd
                    best_prescript = prescript[i-2][j] + "DD"
            
            dp[i][j] = min_cost
            prescript[i][j] = best_prescript
    
    return prescript[n][m]

def printMatrix(string1: str, string2: str, replaceCost: int, insertCost: int, deleteCost: int, doubleDeleteCost: int):
    """Выводит матрицу редакционных расстояний"""
    n, m = len(string1), len(string2)
    
    if replaceCost > deleteCost + insertCost:
        replaceCost = deleteCost + insertCost
    
    # Создаем матрицу
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    # Инициализация
    for i in range(n + 1):
        dp[i][0] = i * deleteCost
    for j in range(m + 1):
        dp[0][j] = j * insertCost
    
    # Заполнение матрицы
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            operations = []
            operations.append(dp[i-1][j] + deleteCost)
            operations.append(dp[i][j-1] + insertCost)
            
            if string1[i-1] == string2[j-1]:
                operations.append(dp[i-1][j-1])
            else:
                operations.append(dp[i-1][j-1] + replaceCost)
            
            if i >= 2 and string1[i-1] == string1[i-2]:
                operations.append(dp[i-2][j] + doubleDeleteCost)
            
            dp[i][j] = min(operations)
    
    # Вывод матрицы
    print("\nМатрица редакционных расстояний:")
    print("       ", end="")
    for j in range(m + 1):
        if j == 0:
            print("ε    ", end="")
        else:
            print(f"{string2[j-1]:<4} ", end="")
    print()
    
    for i in range(n + 1):
        if i == 0:
            print("ε  ", end="")
        else:
            print(f"{string1[i-1]}  ", end="")
        
        for j in range(m + 1):
            print(f"{dp[i][j]:<4} ", end="")
        print()

def main():
    try:
        # Чтение входных данных (4 числа!)
        print("Введите стоимости операций (замена вставка удаление двойное_удаление):")
        costs = list(map(int, input().split()))
        if len(costs) != 4:
            print("Ошибка: нужно ввести четыре числа (стоимости операций)")
            return
        
        replaceCost, insertCost, deleteCost, doubleDeleteCost = costs
        print("Введите первую строку:")
        string1 = input().strip()
        print("Введите вторую строку:")
        string2 = input().strip()
        
        # Вычисление расстояния
        distance = wagnerFischerDistance(string1, string2, replaceCost, insertCost, deleteCost, doubleDeleteCost)
        print(f"\nМинимальное редакционное расстояние: {distance}")
        
        # Получение редакционного предписания
        prescription = wagnerFisherEditorialPrescription(string1, string2, replaceCost, insertCost, deleteCost, doubleDeleteCost)
        print(f"Редакционное предписание: {prescription}")
        
        # Вывод матрицы
        printMatrix(string1, string2, replaceCost, insertCost, deleteCost, doubleDeleteCost)
        
        # Дополнительная информация
        print(f"\nДополнительная информация:")
        print(f"Длина первой строки: {len(string1)}")
        print(f"Длина второй строки: {len(string2)}")
        print(f"Стоимости операций: замена={replaceCost}, вставка={insertCost}, удаление={deleteCost}, двойное_удаление={doubleDeleteCost}")
        
    except ValueError as e:
        print(f"Ошибка ввода: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()