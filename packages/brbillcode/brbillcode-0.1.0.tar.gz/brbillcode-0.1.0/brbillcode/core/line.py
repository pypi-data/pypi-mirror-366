from brbillcode.models import BankBill, CollectionBill
from typing import Union
import re

class Line:
    """
    Represents a payment slip line or barcode and dispatches
    to the correct bill type: BankBill or CollectionBill.

    Delegates all attribute and method calls to the chosen bill.
    """

    def __init__(self, code: str):
        self.code = code
        self.bill: Union[BankBill, CollectionBill] = self._detect_and_create_bill()

    def _detect_and_create_bill(self) -> Union[BankBill, CollectionBill]:
        """
        Detects the type of bill based on the cleaned code length and prefix,
        and instantiates the corresponding BankBill or CollectionBill.
        """
        clean_code = re.sub(r'\D', '', self.code)
        length = len(clean_code)
        starts_with_8 = clean_code.startswith('8')

        def bank_line():
            if starts_with_8:
                raise ValueError("47-digit line starting with '8' is invalid for BankBill")
            return BankBill(clean_code)

        def collection_line():
            if not starts_with_8:
                raise ValueError("48-digit line must start with '8' for CollectionBill")
            return CollectionBill(clean_code)

        def barcode():
            return CollectionBill(clean_code) if starts_with_8 else BankBill(clean_code)

        dispatch_map = {
            47: bank_line,
            48: collection_line,
            44: barcode,
        }

        if length not in dispatch_map:
            raise ValueError("Code length must be 44, 47, or 48 digits")

        return dispatch_map[length]()

    def __getattr__(self, attr):
        """
        Delegate attribute access to the underlying bill object.
        """
        return getattr(self.bill, attr)
