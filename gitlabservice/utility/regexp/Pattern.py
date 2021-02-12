class Pattern:
    """
    Класс для хранения и компиляции паттернов для регулярных выражений
    """
    CURRENT_DATABASE = r'(?:USE)(?:[ ]+[[]*)([a-zA-Z]+)(?:[\]]*)'
    OBJECT_TYPE = r'(?:ALTER[ ]+)(\w+)|(?:CREATE[ ]+)([^O]\w+)'
    OBJECT_NAME = r'(?:ALTER[ ]+(\w+)|(CREATE[ ]+)([^O]\w+))[ ]+([a-zA-Z\[\]._0-9]+)'
    OBJECT_FIRST_LINE = r'(?:CREATE|ALTER)(?:[ ]+)(\w+)'
    REPLACE_CREATE = r'(?:\bCREATE (PROCEDURE|FUNCTION))'



