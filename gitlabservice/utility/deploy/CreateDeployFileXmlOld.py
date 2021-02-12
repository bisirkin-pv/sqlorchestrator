from utility.deploy.CreateDeployFIle import CreateDeployFile

class CreateDeployFileXmlOld(CreateDeployFile):
    """
    Формирует файл деплоя xml
    """

    def __init__(self, file_list, deploy_file_header):
        super(CreateDeployFileXmlOld, self).__init__(file_list)
        self.__deploy_file_header = deploy_file_header
        self.__deploy_objects = []
        self._deploy_template = '<deploy>{}\n</deploy>'
        self._body_template = '\n<row script="{0}" folder="{1}" />'

    def file_list_get(self):
        return super().file_list_get()

    def create(self):
        files = self.file_list_get()
        body = ''
        for file in files:
            fl = file.get('name', '').split('/')
            body += self._body_template.format(fl[-1], '/'.join(fl[:-1]))

        # TODO: Имена привязать к сесии
        script_name = 'tmp/deploy.xml'
        with open(script_name, 'w', encoding='utf-8') as f:
            f.write(self._deploy_template.format(body))

        result = dict(status=200,
                      type='deploy',
                      filename='deploy.xml')
        return result
