import re
import os
from utility.deploy.CreateDeployFIle import CreateDeployFile
from utility.gitlab.Controller import Controller as GitLabController
from utility.model.DeployFileModel import DeployFileParam
from utility.regexp.Pattern import Pattern
from utility.regexp.RegExp import RegExp
from utility.transliterate import transliterate


class CreateDeployFileSql(CreateDeployFile):
    """
    Формирует файл деплоя sql
    """

    def __init__(self, file_list, project, merge_request_id, private_token):
        """
        Конструтор
        :param file_list: список названий файлов для создания скрипта
        :param project: Объект проекта
        :param merge_request_id: Номер выбранного merge request'a
        """
        super(CreateDeployFileSql, self).__init__(file_list)
        self.__project = project
        self.__merge_request_id = merge_request_id
        self.__use_database = ''
        self.__private_token = private_token

    def file_list_get(self):
        """
        Возвращает список файлов для создания скрипта
        :return:
        """
        return super().file_list_get()

    def create(self):
        """
        Создает файл sql и репозитория, по списку переданных объектов
        :return:
        """
        mr = self.__project.mergerequests.get(self.__merge_request_id)
        cd = os.getcwd()
        script_name = mr.title.replace(' ', '_').replace('"', '').replace('\t', '_').replace('.', '')[:20] + '.sql'
        script_name = transliterate(script_name)
        lnk = self.__project._links
        gitlab_controller = GitLabController(lnk['self'], self.__private_token, self.get_sha_commit(mr))
        file_list = self.file_list_get()
        objects = []
        if len(file_list) > 0:
            with open('tmp/' + script_name, 'w', encoding='utf-8') as f:
                f.write('SET NOCOUNT ON;\n')
                for file in file_list:
                    if file.get('state') == 'is-deleted':
                        obj_param = self.get_file_param(file.get('name'))
                        f.write(self.get_file_delimiter(obj_param.name))
                        drop = self.script_drop_object(*obj_param)
                        f.write(drop)
                        continue

                    raw = gitlab_controller.get_raw(file.get('name')).decode("utf-8")

                    # Пока используем этот метод, так как регулярк не универсально выдает совпадение
                    object_type = CreateDeployFileSql.find_current_object_type(raw)
                    if object_type == '':
                        continue

                    start = 0
                    if object_type.lower() not in ('table', 'query', 'job'):
                        start = self.get_start_script(raw)
                        
                    use = self.find_current_db(raw)
                    if use and use != self.__use_database:
                        self.__use_database = use
                        f.write('\nGO\nUSE {0}\n'.format(self.__use_database))
                        
                    object_name = self.find_current_object_name(raw)
                    objects.append(object_name.replace('[', '').replace(']', ''))
                    f.write(self.get_file_delimiter(object_name))
                    f.write(raw[start:].replace('\r\n', '\n'))

        result = dict(status=200,
                      type='deploy',
                      filename=script_name,
                      objects=objects)
        return result

    def rollback(self):
        """
        Создает файл отката sql и репозитория, по списку переданных объектов
        :return:
        """
        mr = self.__project.mergerequests.get(self.__merge_request_id)
        cd = os.getcwd()
        script_name = 'rollback_' + mr.title.replace(' ', '_').replace('"', '').replace('\t', '_').replace('.', '')[:20] + '.sql'
        script_name = transliterate(script_name)
        branch = self.__project.branches.get('master')
        gitlab_controller = GitLabController(self.__project.id, self.__private_token, branch.commit.get("id"))
        file_list = self.file_list_get()
        objects = []
        if len(file_list) > 0:
            with open('tmp/' + script_name, 'w', encoding='utf-8') as f:
                f.write('SET NOCOUNT ON;\n')
                for file in file_list:
                    if file.get('state') == 'is-added':
                        obj_param = self.get_file_param(file.get('name'))
                        f.write(self.get_file_delimiter(obj_param.name))
                        drop = self.script_drop_object(*obj_param)
                        f.write(drop)
                        continue

                    raw = gitlab_controller.get_raw(file.get('name')).decode("utf-8")

                    # Пока используем этот метод, так как регулярк не универсально выдает совпадение
                    object_type = CreateDeployFileSql.find_current_object_type(raw)
                    if object_type == '':
                        continue

                    start = 0
                    if object_type.lower() not in ('table', 'query', 'job'):
                        start = self.get_start_script(raw)

                    use = self.find_current_db(raw)
                    if use and use != self.__use_database:
                        self.__use_database = use
                        f.write('\nGO\nUSE {0}\n'.format(self.__use_database))

                    object_name = self.find_current_object_name(raw)
                    objects.append(object_name.replace('[', '').replace(']', ''))
                    f.write(self.get_file_delimiter(object_name))
                    f.write(raw[start:].replace('\r\n', '\n'))

        result = dict(status=200,
                      type='deploy',
                      filename=script_name,
                      objects=objects)
        return result

    @staticmethod
    def get_sha_commit(merge_requests):
        """
            Возващает хэш коммита
        :param merge_requests: Объект merge request'a
        :return:
        """
        if merge_requests.state == 'merged':
            return merge_requests.merge_commit_sha
        return merge_requests.sha

    @staticmethod
    def get_object_type(obj):
        """
        Определение типа файла по пути
        :param obj: путь
        :return: тип объекта
        """
        obj_list = obj.split('/')
        obj_type = obj_list[len(obj_list) - 2] if len(obj_list) >= 2 else ""
        return obj_type

    @staticmethod
    def find_current_db(raw):
        """
        Поиск текущей базы данных по скрипту
        :param raw: Текст скрипта
        :return: Текущую БД или None
        """
        return RegExp.search(Pattern.CURRENT_DATABASE, raw)

    @staticmethod
    def find_current_object_type(raw):
        """
        Поиск типа объекта в скрипте
        :param raw: Текст скрипта
        :return: Имя объекта или пустую строку
        """
        return RegExp.search(Pattern.OBJECT_TYPE, raw)

    @staticmethod
    def find_current_object_name(raw):
        """
        Поиск названия объекта в скрипте
        :param raw: Текст скрипта
        :return: Имя объекта или None
        """
        return RegExp.search(Pattern.OBJECT_NAME, raw)

    @staticmethod
    def clear_name(name):
        words = ('create', 'alter', 'procedure', 'function', 'table', 'view')
        for word in words:
            pattern = re.compile(r"\b" + word + "\\b", re.I)
            name = re.sub(pattern, '', name)
        return name.lstrip()

    @staticmethod
    def get_start_script(raw):
        """
        Поиск названия объекта в скрипте
        :param raw: Текст скрипта
        :return: Имя объекта или None
        """
        pattern = re.compile(Pattern.OBJECT_FIRST_LINE)
        fnd = pattern.search(raw)
        if fnd:
            return fnd.start()
        return None

    @staticmethod
    def get_file_delimiter(file_name):
        """
        Добавляет текст разделителя файлов
        :param file_name: Имя файла
        :return: Разделитель
        """
        return "\nGO\nPRINT 'Скрипт для объекта: {0}'\nGO\n".format(file_name)

    @staticmethod
    def replace_create(raw):
        """
        Замена создания объекта на обновление
        :param raw: Текст скрипта
        :return: Обновленный скрипт
        """
        pattern = re.compile(Pattern.REPLACE_CREATE)
        result = pattern.sub('CREATE OR ALTER', raw, 1)
        return result

    @staticmethod
    def script_drop_object(obj_name, obj_type, obj_base):
        return '\nGO\nUSE {0}\nDROP {1} IF EXISTS {2}'.format(obj_base, obj_type, obj_name)

    @staticmethod
    def get_file_param(filename):
        """
        Возвращает тип объекта по его полному имени(специфичный метод)
        :param filename: Полное имя объекта
        :return: DeployFileParam(Имя, Тип, База)
        """
        obj_list = filename.split('/')
        obj_type = obj_list[len(obj_list) - 2] if len(obj_list) >= 2 else ""
        obj_name = obj_list[len(obj_list) - 1].replace('.sql', '') if len(obj_list) >= 1 else ""
        obj_base = obj_list[len(obj_list) - 1].split('.')[0]
        return DeployFileParam(obj_name, obj_type, obj_base)

