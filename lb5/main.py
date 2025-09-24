from collections import deque
import graphviz

class TrieNode:
    """Класс узла бора"""
    def __init__(self, nodeId: int):
        self.id = nodeId            # уникальный идентификатор узла
        
        self.isTerminal = False     # флаг, является ли вершина терминалом
        self.patternIndices = []    # номера шаблонов, заканчивающихся в этом узле
        self.patternLength = 0      # длина шаблона

        self.childrens = {}         # указатели на дочерние узлы
        self.suffixLink = None      # суффиксная ссылка
        self.finalLink = None       # конечная ссылка


class AhoCorasicAlgorithm:
    """Класс, реализующий алгоритм Ахо-Корасика"""
    def __init__(self, patterns: list):
        """Инициализирует алгоритм, создает автомат"""
        
        self.root = TrieNode(0)             # корневой узел       
        self.root.suffixLink = self.root    # суффиксная ссылка корня
        self.nodeCount = 1                  # счетчик узлов
        self.patterns = patterns            # сохраняем шаблоны
        self.max_arcs = 0                   # максимальное количество дуг из одной вершины

        # строим бор
        for index in range(len(patterns)):
            self.__add(patterns[index], index)

        # создаем ссылки, строим автомат
        self.__makeLinks()
    
    def __add(self, pattern: str, index: int):
        """Добавляет новый шаблон в бор"""
        currentNode = self.root
        # перебираем символы шаблона 
        for char in pattern:                            
            if char not in currentNode.childrens:
                newNode = TrieNode(self.nodeCount)
                currentNode.childrens[char] = newNode
                self.nodeCount += 1
                # Обновляем максимальное количество дуг
                self.max_arcs = max(self.max_arcs, len(currentNode.childrens))
            currentNode = currentNode.childrens[char]
        
        currentNode.isTerminal = True
        currentNode.patternIndices.append(index)
        currentNode.patternLength = len(pattern)

    def __makeLinks(self):
        """Создает суффиксные и конечные ссылки"""
        queue = deque()
        queue.append(self.root)

        while queue:
            currentNode = queue.popleft()
            
            for char, childNode in currentNode.childrens.items():
                queue.append(childNode)
                
                # для детей корня суффиксная ссылка ведет в корень
                if currentNode == self.root:
                    childNode.suffixLink = self.root
                else:
                    # ищем первую возможную суффиксную ссылку
                    temp = currentNode.suffixLink
                    while (temp != self.root) and (char not in temp.childrens):
                        temp = temp.suffixLink
                    
                    # устанавливаем найденную ссылку или ссылку на корень
                    if char in temp.childrens:
                        childNode.suffixLink = temp.childrens[char]
                    else:
                        childNode.suffixLink = self.root
                
                # построение конечной ссылки
                if childNode.suffixLink.isTerminal:
                    childNode.finalLink = childNode.suffixLink
                else:
                    childNode.finalLink = childNode.suffixLink.finalLink

    def search(self, text):
        """Ищет все вхождения шаблонов в тексте"""
        results = []
        currentNode = self.root
        
        for position in range(len(text)):
            char = text[position]
            
            # используем суффиксные ссылки при отсутствии перехода
            while (currentNode != self.root) and (char not in currentNode.childrens):
                currentNode = currentNode.suffixLink
            
            # переходим по символу, если переход существует
            if char in currentNode.childrens:
                currentNode = currentNode.childrens[char]
            
            # проверяем терминальные узлы
            if currentNode.isTerminal:
                for patternIndex in currentNode.patternIndices:
                    startPosition = position - currentNode.patternLength + 1
                    results.append((startPosition, patternIndex, currentNode.patternLength))
            
            # проверяем конечные ссылки для нахождения всех вложенных шаблонов
            temp = currentNode.finalLink
            while temp:
                for patternIndex in temp.patternIndices:
                    startPosition = position - temp.patternLength + 1
                    results.append((startPosition, patternIndex, temp.patternLength))
                temp = temp.finalLink
        
        return sorted(results)

    def getNodeCount(self):
        """Позволяет получить число узлов в автомате"""
        return self.nodeCount

    def getMaxArcs(self):
        """Возвращает максимальное количество дуг из одной вершины"""
        return self.max_arcs

    def visualizeBOR(self, filename="bor_tree"):
        """Визуализирует бор в PNG файл"""
        dot = graphviz.Digraph(comment='BOR Tree')
        dot.attr('node', shape='circle')
        
        queue = deque([self.root])
        visited = set([self.root])
        
        # Добавляем корневой узел
        root_label = "0"
        if self.root.isTerminal:
            root_label += "\\n" + ",".join(str(i+1) for i in self.root.patternIndices)
        dot.node('0', root_label, style='filled', fillcolor='lightblue')
        
        while queue:
            node = queue.popleft()
            
            for char, child in node.childrens.items():
                if child not in visited:
                    visited.add(child)
                    queue.append(child)
                
                # Создаем метку для узла
                node_label = f"{child.id}"
                if child.isTerminal:
                    patterns = ",".join(str(i+1) for i in child.patternIndices)
                    node_label += f"\\n{patterns}"
                
                dot.node(str(child.id), node_label)
                
                # Добавляем ребро
                dot.edge(str(node.id), str(child.id), label=char)
        
        # Сохраняем в файл
        dot.render(filename, format='png', cleanup=True)
        print(f"Дерево бора сохранено в файл: {filename}.png")

    def printAutomatInfo(self):
        """Выводит краткую информацию об автомате"""
        print(f"Информация об автомате:")
        print(f"Количество узлов: {self.getNodeCount()}")
        print(f"Количество шаблонов: {len(self.patterns)}")
        print(f"Максимальное количество дуг из одной вершины: {self.getMaxArcs()}")
        
        # Подсчитываем дополнительную статистику
        terminal_count = 0
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            
            if node.isTerminal:
                terminal_count += 1
            
            for child in node.childrens.values():
                queue.append(child)
        
        print(f"Терминальных узлов: {terminal_count}")


def removeFoundPatterns(text, results, patterns):
    """Вырезает найденные образцы из строки и возвращает остаток"""
    if not results:
        return text
    
    # Создаем массив для отметки позиций, которые нужно удалить
    remove_mask = [False] * len(text)
    
    # Помечаем позиции, которые попадают в найденные образцы
    for start_pos, pattern_idx, pattern_length in results:
        pattern = patterns[pattern_idx]
        end_pos = start_pos + pattern_length
        
        # Проверяем границы и помечаем позиции для удаления
        for i in range(max(0, start_pos), min(len(text), end_pos)):
            remove_mask[i] = True
    
    # Собираем остаток строки
    remainder = []
    for i, char in enumerate(text):
        if not remove_mask[i]:
            remainder.append(char)
    
    return ''.join(remainder)


def findPatternRanges(results, patterns):
    """Находит диапазоны найденных образцов для наглядного вывода"""
    ranges = []
    for start_pos, pattern_idx, pattern_length in results:
        pattern = patterns[pattern_idx]
        end_pos = start_pos + pattern_length
        ranges.append((start_pos, end_pos, pattern))
    return sorted(ranges)


def main():
    # ввод данных
    text = input("Введите текст: ")
    num = int(input("Введите количество шаблонов: "))
    patterns = [input(f"Введите шаблон {i + 1}: ") for i in range(num)]
    
    # Создаем автомат Ахо-Корасика
    ahoCorasicAlgorithm = AhoCorasicAlgorithm(patterns)
    
    # Визуализируем бор (опционально)
    try:
        ahoCorasicAlgorithm.visualizeBOR("bor_visualization")
    except:
        print("Для визуализации бора установите graphviz: pip install graphviz")
    
    # Выводим информацию об автомате
    ahoCorasicAlgorithm.printAutomatInfo()
    
    # Пункт 1 варианта 5: Максимальное количество дуг из одной вершины
    max_arcs = ahoCorasicAlgorithm.getMaxArcs()
    print(f"\n=== РЕЗУЛЬТАТЫ ДЛЯ ВАРИАНТА 5 ===")
    print(f"1. Максимальное количество дуг, исходящих из одной вершины: {max_arcs}")
    
    # Поиск вхождений
    results = ahoCorasicAlgorithm.search(text)
    
    # Вывод результатов поиска
    print(f"\nНайдено вхождений: {len(results)}")
    if results:
        print("Найденные вхождения:")
        ranges = findPatternRanges(results, patterns)
        for start_pos, end_pos, pattern in ranges:
            print(f"  Позиции {start_pos}-{end_pos-1}: '{pattern}'")
        
        # Пункт 2 варианта 5: Вырезаем найденные образцы
        remainder = removeFoundPatterns(text, results, patterns)
        print(f"\n2. Результат вырезания найденных образцов:")
        print(f"   Исходный текст: '{text}'")
        print(f"   Остаток строки:  '{remainder}'")
        
        # Дополнительная информация о вырезании
        original_length = len(text)
        remainder_length = len(remainder)
        removed_length = original_length - remainder_length
        print(f"   Статистика: удалено {removed_length} символов из {original_length}")
        
        if remainder:
            print(f"   Сохранено: {remainder_length} символов")
        else:
            print(f"   Весь текст был удален (состоит только из шаблонов)")
    else:
        print("Шаблоны не найдены в тексте")
        print(f"Остаток строки: '{text}'")


if __name__ == "__main__":
    main()