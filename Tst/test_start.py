
import unittest
from Src.start_service import start_service
from Src.reposity import reposity

# Набор тестов для проверки работы статового сервиса
class test_start(unittest.TestCase):

    # Проверить создание start_service и заполнение данными
    def test_notThow_start_service_load(self):
        # Подготовка
        start = start_service()

        # Действие
        start.start()

        # Проверка
        assert len(start.data[ reposity.range_key()]) > 0

    # Проверить уникальность элемиентов
    def test_checkUnique_start_service_load(self):
        # Подготовка
        start = start_service()

        # Действие
        start.start()

        # Проверка
        gramm =  list(filter(lambda x: x.name == "Грамм", start.data[ reposity.range_key()])) 
        kg =  list(filter(lambda x: x.name == "Киллограмм", start.data[ reposity.range_key()])) 
        assert gramm[0].unique_code == kg[0].base.unique_code

        