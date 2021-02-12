import os
import requests
import urllib3


class Controller:
    """
    Класс получения данных из гитлаб
    """
    def __init__(self, project_url, private_token, commit_sha):
        self.__project_url = project_url
        self.__private_token = private_token
        self.__commit_sha = commit_sha
        self.__url = self.__project_url + '/repository/files/{0}/raw?ref={1}'

    def get_raw(self, filename):
        """
        Возвращает текст файла
        :param filename: Имя файла
        :return: Текст файла
        """
        urllib3.disable_warnings()
        filename = filename.replace('/', '%2F')
        raw_url = self.__url.format(filename, self.__commit_sha)
        r = requests.get(raw_url, headers={'PRIVATE-TOKEN': self.__private_token}, verify=False)
        if r.status_code == 200:
            return r.content
        return ''
