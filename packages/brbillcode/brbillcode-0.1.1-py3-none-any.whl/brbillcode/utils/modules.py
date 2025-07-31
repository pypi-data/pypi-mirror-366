def module10(code: str) -> int:
    total = 0
    multiplicator = 2
    for digit in reversed(code):
        product = int(digit) * multiplicator
        total += sum(int(d) for d in str(product))
        multiplicator = 1 if multiplicator == 2 else 2
    remainder = total % 10
    return 0 if remainder == 0 else 10 - remainder

def module11_bank(code: str) -> int:
    total = 0
    multiplicator = 2
    for element in reversed(code):
        total += int(element) * multiplicator
        multiplicator = 9 if multiplicator == 9 else multiplicator + 1
    remainder = total % 11
    if remainder == 0 or remainder == 1:
        return 0
    elif remainder == 10:
        return 1
    return 11 - remainder

def module11_collection(code: str) -> int:
    weights = [4, 3, 2, 9, 8, 7, 6, 5]
    total = 0
    for i, digito in enumerate(reversed(code)):
        peso = weights[i % len(weights)]
        total += int(digito) * peso
    remainder = total % 11
    if remainder in (0, 1):
        return 0
    elif remainder == 10:
        return 1
    return 11 - remainder
