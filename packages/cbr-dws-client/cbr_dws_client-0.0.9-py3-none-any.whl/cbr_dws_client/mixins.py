from datetime import datetime
from decimal import Decimal

from zeep.helpers import serialize_object


class ParseResponseCbrMixin:
    """Миксин для методов парсинга ответа от сервиса ЦБ."""

    def parse_result_to_list(self, data: dict) -> list:
        return data["_value_1"]["_value_1"]

    def parse_currency_on_date_dict(self, data: dict, detail_currency_char_code: int | str | None = None):
        """Метод обработки ответа от сервиса ЦБ на дату.

        :param data: Изначальный ответ.
        :param detail_currency_char_code: Код валюты.
        :return: Список значений или значение в зависимости от detail_currency_char_code.
        """
        parsed_data = self.parse_result_to_list(data=data)
        result = parsed_data
        if detail_currency_char_code is not None:
            for elem in parsed_data:
                break_elements = False
                for _, v in elem.items():
                    if (getattr(v, "VchCode", None) == detail_currency_char_code) | (
                        getattr(v, "VcharCode", None) == detail_currency_char_code
                    ):
                        result = v
                        break_elements = True
                        break
                if break_elements:
                    break
        return result

    def parse_currency_on_period_dict(self, data: dict, drg_met_code: int | None = None):
        """Метод обработки ответа от сервиса ЦБ для периода.

        :param data: Изначальный ответ.
        :param drg_met_code: Код.
        :return: Список значений или значение в зависимости от drg_met_code.
        """
        parsed_data = self.parse_result_to_list(data=data)
        result = parsed_data
        if drg_met_code is not None:
            result = []
            for elem in parsed_data:
                for _, v in elem.items():
                    if getattr(v, "CodMet", None) == drg_met_code:
                        result.append(v)
                        break
        return result

    def parse_bi_cur_base(self, data: list[dict[str, dict[str, datetime | Decimal]]]):
        """Метод обработки ответа от сервиса ЦБ для бивалютной корзины.

        :param data: Изначальный ответ.
        :return: Список кортежей.
        """
        result = []
        for item in data:
            result.append((item["BCB"]["D0"], item["BCB"]["VAL"]))
        return result

    def parse_with_dict(
        self, data: list[dict[str, dict[str, datetime | Decimal]]], variable_name: str, date_name: str, value_name: str
    ):
        """Метод обработки ответа от сервиса ЦБ ввиде словарей.

        :param data: Изначальный ответ.
        :param variable_name: Название переменной.
        :param date_name: Название в словаре даты.
        :param value_name: Назввание в словаре значения.
        :return: Список кортежей.
        """
        result = []
        for item in data:
            result.append((item[variable_name][date_name], item[variable_name][value_name]))
        return result

    def parse_bliquidity(self, data: list[dict[str, dict[str, datetime | Decimal]]]):
        """Метод обработки ответа от сервиса ЦБ для динамики ликвидности банковского сектора.

        :param data: Изначальный ответ.
        :return: Список словарей.
        """
        return [item["BL"] for item in data]

    def parse_mono_dict(self, data: list[dict[str, dict[str, datetime | Decimal]]], field_name: str):
        """Метод обработки списка словарей с одним вложенным ключом.

        :param data: Список словарей
        :param field_name: Ключ.
        :return: Список списков.
        """
        return [serialize_object(item[field_name]).values() for item in data]
