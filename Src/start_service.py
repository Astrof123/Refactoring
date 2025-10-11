from Src.reposity import reposity
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator, argument_exception, operation_exception
import os
import json
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_item_model import receipt_item_model

class start_service:
    # Репозиторий
    __repo: reposity = reposity()

    # Рецепт по умолчанию
    __default_receipt: receipt_model

    # Словарь который содержит загруженные и инициализованные инстансы нужных объектов
    # Ключ - id записи, значение - abstract_model
    __default_receipt_items = {}

    # Наименование файла (полный путь)
    __full_file_name:str = ""

    def __init__(self):
        self.__repo.initalize()

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(start_service, cls).__new__(cls)
        return cls.instance 

    # Текущий файл
    @property
    def file_name(self) -> str:
        return self.__full_file_name

    # Полный путь к файлу настроек
    @file_name.setter
    def file_name(self, value:str):
        validator.validate(value, str)
        full_file_name = os.path.abspath(value)        
        if os.path.exists(full_file_name):
            self.__full_file_name = full_file_name.strip()
        else:
            raise argument_exception(f'Не найден файл настроек {full_file_name}')

    # Загрузить настройки из Json файла
    def load(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не найден файл настроек!")

        try:
            with open( self.__full_file_name, 'r') as file_instance:
                settings = json.load(file_instance)

                if "default_receipt" in settings.keys():
                    data = settings["default_receipt"]
                    return self.convert(data)

            return False
        except:
            return False
        
    # TODO: Внимание! Все методы __convert можно сделать универсально
        
    # Загрузить единицы измерений    
    def __convert_ranges(self, data: dict) -> bool:
        validator.validate(data, dict)
        ranges =     data['ranges'] if 'ranges' in data else []     
        for range in ranges:
            name = range['name'] if 'name' in range else ""
            base_id =  range['base_id'] if 'base_id' in range else ""
            value =  range['value'] if 'value' in range else 1
            id = range['id'] if 'id' in range else ""

            if id.strip() != "":
                base  = self.__default_receipt_items[base_id] if base_id in self.__default_receipt_items else None
                item = range_model.create(name, value, base)
                item.unique_code = id
                self.__default_receipt_items.setdefault(id, item)
                self.__repo.data[ reposity.range_key() ].append(item)

        return True

    # Загрузить группы номенклатуры
    def __convert_groups(self, data: dict) -> bool:
        validator.validate(data, dict)
        categories =  data['categories'] if 'categories' in data else []    
        for category in  categories:
            name = category['name'] if 'name' in category else ""
            id = category['id'] if 'id' in category else ""

            if id.strip() != "":
                item = group_model.create(name)
                item.unique_code = id
                self.__default_receipt_items.setdefault(id, item)
                self.__repo.data[ reposity.group_key() ].append(item)

        return True

    # Загрузить номенклатуру
    def __convert_nomenclatures(   self, data: dict) -> bool:
        validator.validate(data, dict)      
        nomenclatures = data['nomenclatures'] if 'nomenclatures' in data else []   
        for nomenclature in   nomenclatures:
            name = nomenclature['name'] if 'name' in nomenclature else ""
            id = nomenclature['id'] if 'id' in nomenclature else ""
            range_id = nomenclature['range_id'] if 'range_id' in nomenclature else ""
            category_id = nomenclature['category_id'] if 'category_id' in nomenclature else ""

            if id.strip() != "":
                range =  self.__default_receipt_items[range_id] if range_id in self.__default_receipt_items else None
                category =  self.__default_receipt_items[category_id] if category_id in self.__default_receipt_items else None
                item  = nomenclature_model.create(name, category, range)
                item.unique_code = id
                self.__default_receipt_items.setdefault(id, item)
                self.__repo.data[ reposity.nomenclature_key() ].append(item)

        return True        


    # TODO: Внимание! Тут нужно проверки добавить и обработку исключений чтобы возвращать False

    # Обработать полученный словарь    
    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        # 1 Созданим рецепт
        cooking_time = data['cooking_time'] if 'cooking_time' in data else ""
        portions = int(data['portions']) if 'portions' in data else 0
        name =  data['name'] if 'name' in data else "НЕ ИЗВЕСТНО"
        self.__default_receipt = receipt_model.create(name, cooking_time, portions  )

        # Загрузим шаги приготовления
        steps =  data['steps'] if 'steps' in data else []
        for step in steps:
            if step.strip() != "":
                self.__default_receipt.steps.append( step )

        self.__convert_ranges(data)
        self.__convert_groups(data)
        self.__convert_nomenclatures(data)        


        # Собираем рецепт
        compositions =  data['composition'] if 'composition' in data else []      
        for composition in compositions:
            namnomenclature_id = composition['nomenclature_id'] if 'nomenclature_id' in composition else ""
            range_id = composition['range_id'] if 'range_id' in composition else ""
            value  = composition['value'] if 'value' in composition else ""
            nomenclature = self.__default_receipt_items[namnomenclature_id] if namnomenclature_id in self.__default_receipt_items else None
            range = self.__default_receipt_items[range_id] if range_id in self.__default_receipt_items else None
            item = receipt_item_model.create(  nomenclature, range, value)
            self.__default_receipt.composition.append(item)
            
        # Сохраняем рецепт
        self.__repo.data[ reposity.receipt_key() ].append(self.__default_receipt)
        return True

    """
    Стартовый набор данных
    """
    @property
    def data(self):
        return self.__repo.data   

    """
    Основной метод для генерации эталонных данных
    """
    def start(self):
        self.file_name = "settings.json"
        result = self.load()
        if result == False:
            raise operation_exception("Невозможно сформировать стартовый набор данных!")
        


