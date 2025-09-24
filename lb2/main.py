import random
import sys
import heapq

def generateWeightMatrix(n: int, symmetric: bool = True):
    matrix = [[0] * n for _ in range(n)]

    for y in range(n):
        for x in range(n):
            if x == y:
                matrix[y][x] = 0
            elif symmetric:
                if x > y:
                    weight = random.randint(1, 10)
                    matrix[y][x] = weight
                    matrix[x][y] = weight
            else:
                if x != y:
                    matrix[y][x] = random.randint(1, 10)

    return matrix

def saveWeightMatrix(fileName: str, matrix: list):
    with open(fileName, "w") as file:
        for line in matrix:
            file.write(" ".join(map(str, line)) + "\n")

def loadWightMatrix(fileName: str):
    with open(fileName, "r") as file:
        matrix = [list(map(int, line.split(" "))) for line in file.readlines()]
    return matrix

def printMatrix(matrix: list, title: str = ""):
    if title:
        print(f"\n{title}")
    n = len(matrix)
    print("   ", end="")
    for i in range(n):
        print(f"{i:3}", end="")
    print()
    for i in range(n):
        print(f"{i:2} ", end="")
        for j in range(n):
            print(f"{matrix[i][j]:3}", end="")
        print()

def primMST(matrix: list, vertices: set) -> float:
    if not vertices:
        return 0
    
    n = len(matrix)
    visited = set()
    mst_weight = 0
    
    start = next(iter(vertices))
    visited.add(start)
    
    while len(visited) < len(vertices):
        min_edge = float('inf')
        next_vertex = -1
        
        for v in visited:
            for u in vertices - visited:
                if matrix[v][u] > 0 and matrix[v][u] < min_edge:
                    min_edge = matrix[v][u]
                    next_vertex = u
        
        if next_vertex == -1:
            break
            
        mst_weight += min_edge
        visited.add(next_vertex)
    
    return mst_weight

def lowerBound1(matrix: list, path: list, visited: set) -> float:
    n = len(matrix)
    bound = 0

    parts = [path] + [[i] for i in range(n) if i not in visited]

    for part in parts:
        start = part[0]
        end = part[-1]

        incoming = []
        outgoing = []

        for otherPart in parts:
            if otherPart != part:
                otherPartStart = otherPart[0]
                otherPartEnd = otherPart[-1]

                if matrix[otherPartEnd][start] != 0:
                    incoming.append(matrix[otherPartEnd][start])

                if matrix[end][otherPartStart] != 0:
                    outgoing.append(matrix[end][otherPartStart])

        incomingMin = min(incoming) if incoming else 0
        outgoingMin = min(outgoing) if outgoing else 0

        bound += (incomingMin + outgoingMin) / 2

    return bound

def lowerBound2(matrix: list, path: list, visited: set) -> float:
    unvisited = set(range(len(matrix))) - visited
    return primMST(matrix, unvisited)

def heuristicPriority(S: float, k: int, L: float, N: int) -> float:
    if k == 0:
        return float('inf')
    return (S/k + L/N) * (4*N/(3*N + k))

def branchAndBoundV4(matrix: list, start: int):
    n = len(matrix)
    bestPath = None
    bestCost = float('inf')
    
    print("\nМетод ветвей и границ (вариант 4)")
    print(f"Начальная вершина: {start}")
    print(f"Размер графа: {n}")
    
    total_edges = 0
    total_weight = 0
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                total_edges += 1
                total_weight += matrix[i][j]
    
    S = total_weight / total_edges if total_edges > 0 else 0
    L = sum(matrix[start][j] for j in range(n) if matrix[start][j] > 0) / n
    
    priority_queue = []
    
    initial_path = [start]
    initial_visited = set([start])
    initial_cost = 0
    
    initial_priority = heuristicPriority(S, 1, L, n)
    
    heapq.heappush(priority_queue, (initial_priority, initial_cost, initial_path, initial_visited))
    
    iteration = 0
    
    while priority_queue:
        iteration += 1
        
        priority, cost, path, visited = heapq.heappop(priority_queue)
        
        print(f"\nИтерация {iteration}: путь {path}, стоимость {cost}")
        
        if len(path) == n:
            if matrix[path[-1]][start] > 0:
                total_cost = cost + matrix[path[-1]][start]
                if total_cost < bestCost:
                    bestCost = total_cost
                    bestPath = path + [start]
                    print(f"Найден новый лучший путь: стоимость {bestCost}")
            continue
        
        lb1 = lowerBound1(matrix, path, visited)
        lb2 = lowerBound2(matrix, path, visited)
        lb = max(lb1, lb2)
        
        print(f"Нижние оценки: LB1={lb1:.2f}, LB2={lb2:.2f}, максимум={lb:.2f}")
        
        if cost + lb >= bestCost:
            print(f"Отсечение: {cost + lb:.2f} >= {bestCost}")
            continue
        
        last_vertex = path[-1]
        
        candidates = []
        for next_vertex in range(n):
            if next_vertex not in visited and matrix[last_vertex][next_vertex] > 0:
                candidates.append(next_vertex)
        
        candidates.sort(key=lambda v: matrix[last_vertex][v])
        
        for next_vertex in candidates:
            new_path = path + [next_vertex]
            new_visited = visited | {next_vertex}
            new_cost = cost + matrix[last_vertex][next_vertex]
            
            k = len(new_path)
            L_new = sum(matrix[last_vertex][j] for j in range(n) if matrix[last_vertex][j] > 0) / n
            new_priority = heuristicPriority(S, k, L_new, n)
            
            heapq.heappush(priority_queue, (new_priority, new_cost, new_path, new_visited))
            print(f"  Добавлен путь: {new_path}, стоимость: {new_cost}")
    
    return bestPath, bestCost

def improvedNearestInsertion(matrix: list, start: int):
    n = len(matrix)
    path = [start]
    cost = 0
    visited = set([start])
    
    print("\nУлучшенный алгоритм включения ближайшего города")
    print(f"Начальный путь: {path}")
    
    step = 0
    
    while len(path) < n:
        step += 1
        
        best_improvement = float('inf')
        best_vertex = -1
        best_position = -1
        best_cost_change = 0
        
        for candidate in range(n):
            if candidate in visited:
                continue
                
            for pos in range(len(path)):
                current_vertex = path[pos]
                next_vertex = path[(pos + 1) % len(path)]
                
                current_edge_cost = matrix[current_vertex][next_vertex]
                new_edges_cost = matrix[current_vertex][candidate] + matrix[candidate][next_vertex]
                cost_change = new_edges_cost - current_edge_cost
                
                if cost_change < best_improvement:
                    best_improvement = cost_change
                    best_vertex = candidate
                    best_position = pos
                    best_cost_change = cost_change
        
        if best_vertex != -1:
            cost += best_cost_change
            path.insert(best_position + 1, best_vertex)
            visited.add(best_vertex)
            print(f"Шаг {step}: добавлена вершина {best_vertex} в позицию {best_position}, стоимость {cost}")
        else:
            return None, float('inf')
    
    if matrix[path[-1]][start] > 0:
        closing_cost = matrix[path[-1]][start]
        cost += closing_cost
        path.append(start)
        print(f"Замыкание цикла: стоимость {cost}")
        return path, cost
    
    return None, float('inf')

def main():
    fileName = "matrix.txt"
    startVertex = 0

    while True:
        print("\nМеню:")
        print("1 - Сгенерировать несимметричную матрицу")
        print("2 - Сгенерировать симметричную матрицу")
        print("3 - Выбрать начальную вершину")
        print("4 - Загрузить матрицу и запустить алгоритмы")
        print("5 - Выход")
        
        option = input("Выберите опцию: ").strip()
        
        if option == "1":
            numberOfVertices = int(input("Количество вершин: "))
            matrix = generateWeightMatrix(numberOfVertices, False)
            saveWeightMatrix(fileName, matrix)
            print(f"Матрица сохранена в {fileName}")
            
        elif option == "2":
            numberOfVertices = int(input("Количество вершин: "))
            matrix = generateWeightMatrix(numberOfVertices, True)
            saveWeightMatrix(fileName, matrix)
            print(f"Матрица сохранена в {fileName}")
            
        elif option == "3":
            startVertex = int(input("Начальная вершина: "))
            print(f"Установлена вершина {startVertex}")
            
        elif option == "4":
            try:
                matrix = loadWightMatrix(fileName)
                n = len(matrix)
                print(f"Загружена матрица {n}x{n}")
                break
            except FileNotFoundError:
                print(f"Файл {fileName} не найден")
                
        elif option == "5":
            return
            
        else:
            print("Неверная опция")

    bbPath, bbCost = branchAndBoundV4(matrix, startVertex)
    niPath, niCost = improvedNearestInsertion(matrix, startVertex)

    print("\nРезультаты:")
    
    if bbPath is not None and bbCost != float('inf'):
        print(f"Метод ветвей и границ: путь {bbPath}, стоимость {bbCost}")
    else:
        print("МВиГ: путь не найден")

    if niPath is not None and niCost != float('inf'):
        print(f"Улучшенный АВБГ: путь {niPath}, стоимость {niCost}")
        
        if bbPath is not None:
            difference = niCost - bbCost
            if difference > 0:
                print(f"АВБГ хуже на {difference:.2f}")
            elif difference < 0:
                print(f"АВБГ лучше на {abs(difference):.2f}")
            else:
                print(f"Результаты одинаковы")
    else:
        print("АВБГ: путь не найден")

if __name__ == "__main__":
    main()