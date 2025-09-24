from collections import deque

class TrieNode:
    def __init__(self, node_id: int):
        self.id = node_id
        self.is_terminal = False
        self.pattern_indices = []
        self.pattern_length = 0
        self.children = {}
        self.suffix_link = None
        self.final_link = None

class AhoCorasick:
    def __init__(self, patterns: list):
        self.root = TrieNode(0)
        self.root.suffix_link = self.root
        self.node_count = 1
        self.patterns = patterns
        self.max_arcs = 0  # Максимальное количество дуг из одной вершины

        for index, pattern in enumerate(patterns):
            self._add_pattern(pattern, index)
        self._build_links()
    
    def _add_pattern(self, pattern: str, index: int):
        current = self.root
        for char in pattern:
            if char not in current.children:
                new_node = TrieNode(self.node_count)
                current.children[char] = new_node
                self.node_count += 1
                # Обновляем максимальное количество дуг
                self.max_arcs = max(self.max_arcs, len(current.children))
            current = current.children[char]
        
        current.is_terminal = True
        current.pattern_indices.append(index)
        current.pattern_length = len(pattern)

    def _build_links(self):
        queue = deque([self.root])
        while queue:
            current = queue.popleft()
            for char, child in current.children.items():
                queue.append(child)
                
                if current == self.root:
                    child.suffix_link = self.root
                else:
                    temp = current.suffix_link
                    while temp != self.root and char not in temp.children:
                        temp = temp.suffix_link
                    if char in temp.children:
                        child.suffix_link = temp.children[char]
                    else:
                        child.suffix_link = self.root
                
                if child.suffix_link.is_terminal:
                    child.final_link = child.suffix_link
                else:
                    child.final_link = child.suffix_link.final_link

    def search(self, text: str):
        results = []
        current = self.root
        
        for pos in range(len(text)):
            char = text[pos]
            
            while current != self.root and char not in current.children:
                current = current.suffix_link
            
            if char in current.children:
                current = current.children[char]
            
            if current.is_terminal:
                for pattern_idx in current.pattern_indices:
                    start_pos = pos - current.pattern_length + 1
                    results.append((start_pos, pattern_idx, current.pattern_length))
            
            temp = current.final_link
            while temp:
                for pattern_idx in temp.pattern_indices:
                    start_pos = pos - temp.pattern_length + 1
                    results.append((start_pos, pattern_idx, temp.pattern_length))
                temp = temp.final_link
        
        return sorted(results)

    def get_max_arcs(self):
        """Возвращает максимальное количество дуг из одной вершины"""
        return self.max_arcs

    def get_node_count(self):
        """Возвращает количество узлов в автомате"""
        return self.node_count

def find_pattern_with_wildcards(text, pattern, wildcard):
    """Эффективный поиск шаблона с джокерами"""
    n = len(text)
    m = len(pattern)
    
    if m > n:
        return []
    
    # Разбиваем шаблон на сегменты без джокеров
    segments = []
    current_segment = ""
    segment_start = -1
    
    for i, char in enumerate(pattern):
        if char != wildcard:
            if not current_segment:
                segment_start = i
            current_segment += char
        else:
            if current_segment:
                segments.append((current_segment, segment_start))
                current_segment = ""
    
    if current_segment:
        segments.append((current_segment, segment_start))
    
    # Если весь шаблон состоит из джокеров
    if not segments:
        return list(range(1, n - m + 2))
    
    # Используем Ахо-Корасик для поиска сегментов
    segment_patterns = [seg[0] for seg in segments]
    aho = AhoCorasick(segment_patterns)
    
    # Находим все вхождения сегментов
    segment_matches = []
    for i, (seg, start_in_pattern) in enumerate(segments):
        matches = []
        current = aho.root
        
        for pos in range(len(text)):
            char = text[pos]
            
            while current != aho.root and char not in current.children:
                current = current.suffix_link
            
            if char in current.children:
                current = current.children[char]
            
            if current.is_terminal and i in current.pattern_indices:
                match_pos = pos - len(seg) + 1
                matches.append(match_pos)
            
            temp = current.final_link
            while temp:
                if i in temp.pattern_indices:
                    match_pos = pos - temp.pattern_length + 1
                    matches.append(match_pos)
                temp = temp.final_link
        
        segment_matches.append(set(matches))
    
    # Проверяем полные совпадения
    results = set()
    
    for start_pos in segment_matches[0]:
        # Для каждого вхождения первого сегмента проверяем остальные
        valid = True
        pattern_start = start_pos - segments[0][1]
        
        if pattern_start < 0 or pattern_start + m > len(text):
            continue
        
        # Проверяем все сегменты
        for i, (seg, seg_start) in enumerate(segments):
            text_pos = pattern_start + seg_start
            if text_pos < 0 or text_pos + len(seg) > len(text):
                valid = False
                break
            
            # Проверяем совпадение сегмента
            if text[text_pos:text_pos + len(seg)] != seg:
                valid = False
                break
            
            # Проверяем джокеры между сегментами
            if i > 0:
                prev_seg_end = segments[i-1][1] + len(segments[i-1][0])
                gap = seg_start - prev_seg_end
                if gap > 0:  # Есть джокеры между сегментами
                    gap_start = pattern_start + prev_seg_end
                    if gap_start + gap > len(text):
                        valid = False
                        break
        
        if valid:
            results.add(pattern_start + 1)  # 1-based indexing
    
    return sorted(results), aho

def remove_found_patterns(text, results, patterns):
    """Вырезает найденные образцы из строки и возвращает остаток"""
    if not results:
        return text
    
    # Создаем массив для отметки позиций, которые нужно удалить
    remove_mask = [False] * len(text)
    
    # Помечаем позиции, которые попадают в найденные образцы
    for start_pos, pattern_idx, pattern_length in results:
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

def find_pattern_ranges(results, patterns):
    """Находит диапазоны найденных образцов для наглядного вывода"""
    ranges = []
    for start_pos, pattern_idx, pattern_length in results:
        pattern = patterns[pattern_idx]
        end_pos = start_pos + pattern_length
        ranges.append((start_pos, end_pos, pattern))
    return sorted(ranges)

def main():
    # Ввод данных согласно варианту 5
    text = input("Введите текст: ")
    num = int(input("Введите количество шаблонов: "))
    patterns = [input(f"Введите шаблон {i + 1}: ") for i in range(num)]
    wildcard = input("Введите символ джокера: ").strip()
    
    if not wildcard:
        wildcard = '?'  # значение по умолчанию
    
    # Создаем отдельный автомат Ахо-Корасика для статистики
    aho_stats = AhoCorasick(patterns)
    max_arcs = aho_stats.get_max_arcs()
    
    print(f"1. Максимальное количество дуг, исходящих из одной вершины: {max_arcs}")
    
    # Поиск вхождений с джокерами
    results, aho_segments = find_pattern_with_wildcards(text, patterns[0] if patterns else "", wildcard)
    
    # Для варианта 5 ищем все шаблоны (включая без джокеров)
    all_results = []
    for i, pattern in enumerate(patterns):
        if wildcard in pattern:
            # Для шаблонов с джокерами используем специальную функцию
            wildcard_results, _ = find_pattern_with_wildcards(text, pattern, wildcard)
            for pos in wildcard_results:
                all_results.append((pos - 1, i, len(pattern)))  # Convert to 0-based
        else:
            # Для обычных шаблонов используем стандартный поиск
            aho_standard = AhoCorasick([pattern])
            standard_results = aho_standard.search(text)
            for start_pos, pattern_idx, pattern_length in standard_results:
                if pattern_idx == 0:  # Так как мы ищем один шаблон
                    all_results.append((start_pos, i, pattern_length))
    
    # Убираем дубликаты и сортируем
    all_results = sorted(set(all_results))
    
    # Вывод результатов поиска
    print(f"\nНайдено вхождений: {len(all_results)}")
    if all_results:
        print("Найденные вхождения:")
        ranges = find_pattern_ranges(all_results, patterns)
        for start_pos, end_pos, pattern in ranges:
            print(f"  Позиции {start_pos}-{end_pos-1}: '{pattern}'")
        
        # Пункт 2 варианта 5: Вырезаем найденные образцы
        remainder = remove_found_patterns(text, all_results, patterns)
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