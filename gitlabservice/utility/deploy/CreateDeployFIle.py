class CreateDeployFile:
    """
    Класс формирования файлов для деплоя
    """
    def __init__(self, file_list):
        self.__file_list = file_list

    def file_list_get(self):
        return self.__file_list
