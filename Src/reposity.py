"""
Репозиторий данных
"""
class reposity:
    __data = {}

    @property
    def data(self):
        return self.__data
    
    """
    Ключ для единц измерений
    """
    @staticmethod
    def range_key():
        return "range_model"
    

    """
    Ключ для категорий
    """
    @staticmethod
    def group_key():
        return "group_model"
    

    """
    Ключ для номенклатуры
    """
    @staticmethod
    def nomenclature_key():
        return "nomenclature_model"
    

    """
    Ключ для рецептов
    """
    @staticmethod
    def receipt_key():
        return "receipt_model"


    """
    Инициализация
    """
    def initalize(self):
        for method_name in dir(self):
            if method_name.endswith('_key') and hasattr(getattr(self, method_name), '__call__'):
                key = getattr(self, method_name)()
                self.__data[key] = []