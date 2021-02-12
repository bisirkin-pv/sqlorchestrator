from gitlabservice.utility import CreateDeployFile
from gitlabservice.utility import DeployFileObject


class CreateDeployFileXml(CreateDeployFile):
    """
    Формирует файл деплоя xml
    """

    def __init__(self, file_list, deploy_file_header):
        super(CreateDeployFileXml, self).__init__(file_list)
        self.__deploy_file_header = deploy_file_header
        self.__deploy_objects = []

    def file_list_get(self):
        return super().file_list_get()

    def create_objects_list(self):
        for files in self.file_list_get():
            self.__deploy_objects.append(DeployFileObject(
                self.get_object_name(files.get('name')),
                self.get_object_type(files.get('name')),
                self.get_obj_action(files.get('state')),
            )
            )

    def create(self):
        self.create_objects_list()
        xml = '<?xml version="1.0" encoding="utf8"?>'
        xml += '\n<deploy group="{0}" profile="{1}">'.format(self.__deploy_file_header.group,
                                                             self.__deploy_file_header.profile,
                                                             )
        for obj in self.__deploy_objects:
            xml += '\n\t<object name="{0}" type="{1}" action="{2}"/>'.format(
                obj.name,
                obj.type[0],
                obj.action[0],
            )
        xml += '\n</deploy>'
        return xml

    @staticmethod
    def get_object_type(obj):
        obj_list = obj.split('/')
        obj_type = obj_list[len(obj_list) - 2] if len(obj_list) >= 2 else ""
        return obj_type

    @staticmethod
    def get_object_name(obj):
        obj_list = obj.split('/')
        obj_type = obj_list[len(obj_list) - 1].replace('.sql', '') if len(obj_list) >= 1 else ""
        return obj_type

    @staticmethod
    def get_obj_action(obj):
        if obj == 'is-added':
            return 'Create'
        if obj == 'is-deleted':
            return 'Delete'
        if obj == 'is-rename':
            return 'Rename'
        if obj == 'is-modified':
            return 'Alter'
