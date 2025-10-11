
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
    

    # TODO: Внимание! Тут можно сделать универсально

    """
    Инициализация
    """
    def initalize(self):
        self.__data[ reposity.range_key() ] = []
        self.__data[ reposity.group_key() ] = []
        self.__data[ reposity.nomenclature_key() ] = []
        self.__data[ reposity.receipt_key() ] = []
    
    
