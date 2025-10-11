from Src.Models.company_model import company_model
from Src.Core.validator import validator

######################################
# Модель настроек приложения
class settings_model:
    __company: company_model = None

    # Текущая организация
    @property
    def company(self) -> company_model:
        return self.__company
    
    @company.setter
    def company(self, value: company_model):
        validator.validate(value, company_model)
        self.__company = value


