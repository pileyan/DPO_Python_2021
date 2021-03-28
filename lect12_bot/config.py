from enum import Enum

token = '' #Вставить сюда токен
db_file = 'database.vdb'


class States(Enum):
    S_START = "1"
    S_ENTER_DAY = "2"
    S_COUNTRY_OR_REGION = "3"
    S_ENTER_COUNTRY_OR_REGION = "4"
    S_ENTER_FIELDS_LIST = "5"
