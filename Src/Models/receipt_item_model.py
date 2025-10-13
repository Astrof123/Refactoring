from Src.Core.abstract_model import abstact_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Core.validator import validator

# Модель элемента рецепта
class receipt_item_model(abstact_model):
    __nomenclature:nomenclature_model
    __range:range_model
    __value:int

    # Фабричный метод
    def create(nomenclature:nomenclature_model, range:range_model,  value:int):
        item = receipt_item_model()
        item.__nomenclature = nomenclature
        item.__range = range
        item.__value = value



    """
    Номенклатура
    """
    @property
    def nomenclature(self) -> nomenclature_model:
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model):
        validator.validate(value, nomenclature_model)
        self.__nomenclature = value

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
    Количество (в единицах измерения)
    """
    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, value_: int):
        validator.validate(value_, int)
        self.__value = value_