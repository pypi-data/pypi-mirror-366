from brbillcode.utils import module10, module11_bank
from datetime import timedelta, date
from typing import Dict, Union
import re

class BankBill:
    def __init__(self, code: str):
        self.code = code
        self.__code_info = self.__get_info_from_code(self.__identify_code())

    def __identify_code(self) -> Dict[str, str]:
        if len(self.code) == 47:
            return {"type": "line", "value": self.code}
        elif len(self.code) == 44:
            return {"type": "bar", "value": self.code}
        raise ValueError("The code must have 44 (barcode) or 47 (digitable line) digits for Bank Bill")

    def __get_expiry(self, expiry_factor: str, base_date=date(1997, 10, 7)) -> Union[date, None]:
        try:
            days = int(expiry_factor)
            return base_date + timedelta(days=days) if days > 0 else None
        except ValueError:
            return None

    def __convert_value_factor(self, value: str) -> float:
        return float(f"{value[:-2]}.{value[-2:]}")

    def __get_info_from_line(self, line: str) -> Dict[str, Union[str, date, float]]:
        match = re.search(r"(\d{3})(\d{1})(\d{6})(\d{11})(\d{11})(\d{1})(\d{4})(\d{10})", line)
        if not match:
            raise ValueError("invalid digitable line")

        return {
            "bill": "bank",
            "type": "line",
            "bank": match.group(1),
            "currency": match.group(2),
            "field_1": {"info": match.group(3)[:-1], "dv": match.group(3)[-1]},
            "field_2": {"info": match.group(4)[:-1], "dv": match.group(4)[-1]},
            "field_3": {"info": match.group(5)[:-1], "dv": match.group(5)[-1]},
            "dv": match.group(6),
            "expiry_factor": match.group(7),
            "expiry": self.__get_expiry(match.group(7)),
            "value_factor": match.group(8),
            "value": self.__convert_value_factor(match.group(8))
        }

    def __get_info_from_bar(self, bar: str) -> Dict[str, Union[str, date, float]]:
        match = re.search(r"(\d{3})(\d{1})(\d{1})(\d{4})(\d{10})(\d{5})(\d{10})(\d{10})", bar)
        if not match:
            raise ValueError("Invalid barcode")

        return {
            "bill": "bank",
            "type": "bar",
            "bank": match.group(1),
            "currency": match.group(2),
            "dv": match.group(3),
            "expiry_factor": match.group(4),
            "expiry": self.__get_expiry(match.group(4)),
            "value_factor": match.group(5),
            "value": self.__convert_value_factor(match.group(5)),
            "field_1": {"info": match.group(6), "dv": module10(match.group(1) + match.group(2) + match.group(6))},
            "field_2": {"info": match.group(7), "dv": module10(match.group(7))},
            "field_3": {"info": match.group(8), "dv": module10(match.group(8))}
        }

    def __get_info_from_code(self, code: Dict[str, str]) -> Dict[str, Union[str, float, date]]:
        getter = {
            "line": self.__get_info_from_line,
            "bar": self.__get_info_from_bar
        }
        return getter[code["type"]](code["value"])

    def get_code_info(self) -> Dict[str, Union[str, float, date]]:
        return self.__code_info

    def get_bar(self) -> str:
        ci = self.__code_info
        return f"{ci['bank']}{ci['currency']}{ci['dv']}{ci['expiry_factor']}{ci['value_factor']}" \
               f"{ci['field_1']['info']}{ci['field_2']['info']}{ci['field_3']['info']}"

    def get_line(self, formatted=False) -> str:
        ci = self.__code_info
        if formatted:
            return f"{ci['bank']}{ci['currency']}{ci['field_1']['info'][0]}.{ci['field_1']['info'][1:]}{ci['field_1']['dv']} " \
                   f"{ci['field_2']['info'][:5]}.{ci['field_2']['info'][5:]}{ci['field_2']['dv']} " \
                   f"{ci['field_3']['info'][:5]}.{ci['field_3']['info'][5:]}{ci['field_3']['dv']} " \
                   f"{ci['dv']} {ci['expiry_factor']}{ci['value_factor']}"

        return f"{ci['bank']}{ci['currency']}{ci['field_1']['info']}{ci['field_1']['dv']}" \
               f"{ci['field_2']['info']}{ci['field_2']['dv']}" \
               f"{ci['field_3']['info']}{ci['field_3']['dv']}" \
               f"{ci['dv']}{ci['expiry_factor']}{ci['value_factor']}"

    def validate(self) -> bool:
        ci = self.__code_info
        dv1_valid = module10(ci['bank'] + ci['currency'] + ci['field_1']['info']) == int(ci['field_1']['dv'])
        dv2_valid = module10(ci['field_2']['info']) == int(ci['field_2']['dv'])
        dv3_valid = module10(ci['field_3']['info']) == int(ci['field_3']['dv'])
        bar_dv_valid = module11_bank(f"{self.get_bar()[:4]}{self.get_bar()[5:]}") == int(ci['dv'])
        return all([dv1_valid, dv2_valid, dv3_valid, bar_dv_valid])
