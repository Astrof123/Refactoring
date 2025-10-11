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
            with open( self.__full_file_name, 'r', encoding='utf-8') as file_instance:
                settings = json.load(file_instance)

                if "default_receipt" in settings.keys():
                    data = settings["default_receipt"]
                    return self.convert(data)

            return False
        except:
            return False

        
    # Загрузить единицы измерений    
    def __convert_items(self, data: dict, config: dict) -> bool:
        """
        Универсальная функция для конвертации различных типов данных

        Args:
            data: исходные данные
            config: конфигурация обработки:
                - data_key: ключ в data для получения списка элементов
                - repo_key: ключ для сохранения в репозитории
                - model_class: класс модели для создания
                - fields: маппинг полей из JSON в параметры конструктора
                - ref_fields: поля, которые являются ссылками на другие объекты
        """
        validator.validate(data, dict)
        validator.validate(config, dict)

        items_data = data.get(config['data_key'], [])
        repo_key = config['repo_key']
        model_class = config['model_class']

        for item_data in items_data:
            item_id = item_data.get('id', '').strip()
            if not item_id:
                continue

            # Подготавливаем аргументы для создания модели
            args = []
            for field in config.get('fields', []):
                args.append(item_data.get(field, ''))

            # Обрабатываем ссылочные поля
            kwargs = {}
            for ref_field in config.get('ref_fields', []):
                ref_id = item_data.get(ref_field[1], '')
                kwargs[ref_field[0]] = self.__default_receipt_items.get(ref_id)

            # Создаем объект
            item = model_class.create(*args, **kwargs)
            item.unique_code = item_id
            self.__default_receipt_items.setdefault(item_id, item)
            self.__repo.data[repo_key].append(item)

        return True


    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        # Создаем рецепт (оставляем как есть)
        cooking_time = data.get('cooking_time', '')
        portions = int(data.get('portions', 0))
        name = data.get('name', 'НЕ ИЗВЕСТНО')
        self.__default_receipt = receipt_model.create(name, cooking_time, portions)

        # Шаги приготовления
        steps = data.get('steps', [])
        for step in steps:
            if step.strip():
                self.__default_receipt.steps.append(step)

        # Конвертируем данные через универсальную функцию
        conversion_configs = [
            {
                'data_key': 'ranges',
                'repo_key': reposity.range_key(),
                'model_class': range_model,
                'fields': ['name', 'value'],
                'ref_fields': [("base", 'base_id')],
            },
            {
                'data_key': 'categories',
                'repo_key': reposity.group_key(),
                'model_class': group_model,
                'fields': ['name'],
                'ref_fields': []
            },
            {
                'data_key': 'nomenclatures',
                'repo_key': reposity.nomenclature_key(),
                'model_class': nomenclature_model,
                'fields': ['name'],
                'ref_fields': [("group", 'category_id'), ("range", 'range_id')]
            }
        ]

        for config in conversion_configs:
            self.__convert_items(data, config)

        # Остальная логика составления рецепта...
        compositions = data.get('composition', [])
        for composition in compositions:
            nomenclature_id = composition.get('nomenclature_id', '')
            range_id = composition.get('range_id', '')
            value = composition.get('value', '')
            nomenclature = self.__default_receipt_items.get(nomenclature_id)
            range_obj = self.__default_receipt_items.get(range_id)
            item = receipt_item_model.create(nomenclature, range_obj, value)
            self.__default_receipt.composition.append(item)

        self.__repo.data[reposity.receipt_key()].append(self.__default_receipt)
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
        


