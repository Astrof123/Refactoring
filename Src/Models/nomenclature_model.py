from Src.Core.entity_model import entity_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.validator import validator


"""
Модель номенклатуры
"""
class nomenclature_model(entity_model):
    __group: group_model = None
    __range: range_model = None

   
    """
    Группа номенклатуры
    """
    @property
    def group(self) -> group_model:
        return self.__group

    @group.setter
    def group(self, value: group_model):
        validator.validate(value,entity_model )
        self.__group = value    

    """
    Единица измерения
    """
    @property
    def range(self) -> range_model:
        return self.__range
    
    @range.setter
    def range(self, value: range_model):
        validator.validate(value, range_model)
        self.__range = value


    """
    Универсальный фабричный метод
    """
    def create(name:str, group:group_model, range:range_model):
        validator.validate(name, str)
        item = nomenclature_model()
        item.name = name
        item.group = group
        item.range = range
        return item
        
    