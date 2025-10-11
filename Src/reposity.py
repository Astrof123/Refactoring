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
    Получить все ключи репозитория
    """
    @classmethod
    def get_all_keys(cls):
        return [
            cls.range_key(),
            cls.group_key(), 
            cls.nomenclature_key(),
            cls.receipt_key()
        ]

    """
    Инициализация
    """
    def initalize(self):
        # Универсальная инициализация всех ключей
        for key in self.get_all_keys():
            self.__data[key] = []