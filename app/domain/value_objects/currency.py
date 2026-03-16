from decimal import Decimal
import re

REGEX_BRL_FORMAT = re.compile(r"^R\$\s?\d{1,3}(\.\d{3})*,\d{2}$")

def clean_brl_format_to_decimal(amount: str) -> Decimal:
    if not REGEX_BRL_FORMAT.match(amount):
        raise ValueError(
            "Formato incorreto para o valor. Deve ter o formato R$ 1.000,00"
        )
    
    clean_value = re.sub(r'[R$\s.]', '', amount).replace(',', '.')
    return Decimal(clean_value)