import  re


class RegExp:
    """
    Класс для упрощения работы с регулярными выражениями
    """
    @staticmethod
    def search(find_pattern, text) -> str:
        """
        Выполняет поиск первого вхождения
        :param find_pattern: Регулярное выражение для поиска
        :param text: Строка в которой искать
        :param group_id: Номер группы для вывода
        :return:
        :return: найденная строка
        """
        pattern = re.compile(find_pattern)
        result = pattern.search(text)
        if result:
            return result.group(result.lastindex)
        return ''
