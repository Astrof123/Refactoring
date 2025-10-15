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

    __all_dtos = []

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
            with open( self.__full_file_name, 'r', encoding="utf-8") as file_instance:
                settings = json.load(file_instance)

                if "default_receipt" in settings.keys():
                    data = settings["default_receipt"]
                    return self.convert(data)

            return False
        except:
            return False

    # Cобирание DTO
    def __collect_dto(self, items_data, fields, ref_fields):
        dtos = []
        for item_data in items_data:
            item_id = (item_data.get('id') or '').strip()
            if not item_id:
                continue

            dto = {
                'id': item_id,
                'pos_args': [item_data.get(f, '') for f in fields],
                'refs': {attr_name: (item_data.get(json_field) or '') for attr_name, json_field in ref_fields}
            }
            dtos.append(dto)

        self.__all_dtos.append(dtos)
        return dtos

    # Cоздание реальных объектов, разрешая ссылки по id
    def __creating_objects(self, dtos, model_class, repo_key):
        for dto in dtos:
            create_kwargs = {}
            for attr_name, ref_id in dto['refs'].items():
                if not ref_id:
                    create_kwargs[attr_name] = None
                else:
                    create_kwargs[attr_name] = self.__default_receipt_items.get(ref_id)

            pos_args = dto['pos_args']

            item = model_class.create(*pos_args, **create_kwargs)
            item.unique_code = dto['id']

            self.__default_receipt_items.setdefault(dto['id'], item)
            self.__repo.data[repo_key].append(item)


    # Загрузить единицы измерений
    def __convert_items(self, data: dict, config: dict) -> bool:
        """
        Универсальная функция для конвертации различных типов данных в две фазы:
        1) Сбор DTO (не создаём реальные модели, только собираем поля и id ссылок)
        2) Создание моделей из DTO с разрешением ссылок


        Args:
            data: исходные данные
            config содержит:
                - data_key: ключ в data для получения списка элементов
                - repo_key: ключ для сохранения в репозитории
                - model_class: класс модели для создания
                - fields: список полей (порядок соответствует позиционным аргументам create)
                - ref_fields: список кортежей (attr_name, json_field_name) для ссылок
        """
        validator.validate(data, dict)
        validator.validate(config, dict)

        items_data = data.get(config['data_key'], [])
        repo_key = config['repo_key']
        model_class = config['model_class']
        fields = config.get('fields', [])
        ref_fields = config.get('ref_fields', [])

        dtos = self.__collect_dto(items_data, fields, ref_fields)
        self.__creating_objects(dtos, model_class, repo_key)

        return True

    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        cooking_time = data.get('cooking_time', '')
        portions = int(data.get('portions', 0))
        name = data.get('name', 'НЕ ИЗВЕСТНО')
        self.__default_receipt = receipt_model.create(name, cooking_time, portions)

        steps = data.get('steps', [])
        for step in steps:
            if step.strip():
                self.__default_receipt.steps.append(step)

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



