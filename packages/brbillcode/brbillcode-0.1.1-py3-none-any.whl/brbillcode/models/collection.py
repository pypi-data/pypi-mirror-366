from brbillcode.utils import module10, module11_collection
from typing import Dict, Union
import re

class CollectionBill:
    def __init__(self, code: str):
        self.code = code
        self.__code_info = self.__get_info()

    def __get_info(self) -> Dict[str, Union[str, float]]:
        if len(self.code) == 44:
            return self.__get_info_from_bar()
        elif len(self.code) == 48:
            return self.__get_info_from_line()
        else:
            raise ValueError("The code must have 44 (barcode) or 48 (typeable line) digits for Collection Bill")

    def __convert_value(self, value_str: str) -> float:
        return float(f"{value_str[:-2]}.{value_str[-2:]}") if value_str.strip("0") else 0.0

    def __get_module(self):
        currency_code = int(self.code[2])
        if currency_code in (6, 7):
            return module10
        elif currency_code in (8, 9):
            return module11_collection
        else:
            raise ValueError(f"Invalid currency code: {currency_code}")

    def __get_info_from_bar(self) -> Dict[str, Union[str, float]]:
        if not re.fullmatch(r"\d{44}", self.code):
            raise ValueError("Invalid barcode")

        module = self.__get_module()

        return {
            "bill": "collection",
            "type": "bar",
            "collection": self.code[0:3],
            "product": self.code[3:4],
            "currency": self.code[2],
            "field_1": {
                "info": self.code[0:11],
                "dv": str(module(self.code[0:11]))
            },
            "field_2": {
                "info": self.code[11:22],
                "dv": str(module(self.code[11:22]))
            },
            "field_3": {
                "info": self.code[22:33],
                "dv": str(module(self.code[22:33]))
            },
            "field_4": {
                "info": self.code[33:44],
                "dv": str(module(self.code[33:44]))
            },
            "dv": self.code[4:5],
            "value_factor": self.code[4:15],
            "value": self.__convert_value(self.code[4:15]),
        }

    def __get_info_from_line(self) -> Dict[str, Union[str, float]]:
        if not re.fullmatch(r"\d{48}", self.code):
            raise ValueError("Invalid digitable line")

        return {
            "bill": "collection",
            "type": "line",
            "collection": self.code[0:3],
            "product": self.code[3:4],
            "currency": self.code[2],
            "field_1": {
                "info": self.code[0:11],
                "dv": self.code[11]
            },
            "field_2": {
                "info": self.code[12:23],
                "dv": self.code[23]
            },
            "field_3": {
                "info": self.code[24:35],
                "dv": self.code[35]
            },
            "field_4": {
                "info": self.code[36:47],
                "dv": self.code[47]
            },
            "value_factor": self.code[4:15],
            "value": self.__convert_value(self.code[4:15])
        }

    def convert_line_to_barcode(self) -> str:
        if not re.fullmatch(r'\d{48}', self.code) or self.code[0] != '8':
            raise ValueError("Invalid digitable line for collection bill")
        return (
            self.code[0:11] +
            self.code[12:23] +
            self.code[24:35] +
            self.code[36:47]
        )

    def get_bar(self) -> str:
        if self.__code_info["type"] == "line":
            return self.convert_line_to_barcode()
        return self.code

    def get_line(self, formatted: bool = False) -> str:
        if len(self.code) == 48:
            line = self.code
        elif len(self.code) == 44:
            bar = self.code
            module = self.__get_module()
            blocks = [
                (bar[0:11], module),
                (bar[11:22], module),
                (bar[22:33], module),
                (bar[33:44], module),
            ]
            line = "".join(f"{num}{mod(num)}" for num, mod in blocks)
        else:
            raise ValueError("invalid bar code")

        if not formatted:
            return line

        return f"{line[0:11]}{line[11]} {line[12:23]}{line[23]} {line[24:35]}{line[35]} {line[36:47]}{line[47]}"

    def validate(self) -> bool:
        if len(self.code) == 44:
            return self.validate_barcode()
        elif len(self.code) == 48:
            return self.validate_line(validate_blocks=True)
        return False

    def validate_barcode(self) -> bool:
        if not re.fullmatch(r'\d{44}', self.code) or self.code[0] != '8':
            return False

        currency_code = int(self.code[2])
        dv = int(self.code[3])
        block = self.code[:3] + self.code[4:]
        if currency_code in (6, 7):
            return module10(block) == dv
        elif currency_code in (8, 9):
            return module11_collection(block) == dv
        return False

    def validate_line(self, validate_blocks=False) -> bool:
        if not re.fullmatch(r'\d{48}', self.code) or self.code[0] != '8':
            return False
        try:
            cod_barras = self.convert_line_to_barcode()
        except ValueError:
            return False

        valid_dv = CollectionBill(cod_barras).validate_barcode()
        if not validate_blocks:
            return valid_dv

        currency_code = int(self.code[2])
        if currency_code in (6, 7):
            module = module10
        elif currency_code in (8, 9):
            module = module11_collection
        else:
            return False

        blocks = [
            (self.code[0:11], int(self.code[11])),
            (self.code[12:23], int(self.code[23])),
            (self.code[24:35], int(self.code[35])),
            (self.code[36:47], int(self.code[47])),
        ]
        valid_blocks = all(module(num) == dv for num, dv in blocks)
        return valid_dv and valid_blocks

    def get_code_info(self) -> Dict[str, Union[str, float]]:
        return self.__code_info