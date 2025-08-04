from .eng_numbers_to_words import *
from .tam_numbers_to_words import *


def num2wordsIND(inp):
    inp = str(inp)
    inp = inp.replace(",", "")
    try:
        if isinstance(float(inp), (int, float)):
            pass
    except Exception as e:
        return e, ""
    inp, decimal_number = decimal_and_real_number(inp)
    if len(inp) > 17:
        return "Maximum support is upto 17 digits", "maximum limit is 2 digits"
    if inp == '':
        inp = '0'
    rupee = eng_numbers_to_words_0_to_999(inp, True)
    rupee = rupee.rstrip()
    paise = '' or decimal_number
    if paise:
        if len(paise) > 2:
            paise = paise[:2]
        paise = eng_numbers_to_words_0_to_99(paise, True)
        return rupee, paise
    else:
        return rupee, ""


def num2wordsSI(inp):
    inp = str(inp)
    inp = inp.replace(",", "")
    try:
        if isinstance(float(inp), (int, float)):
            pass
    except Exception as e:
        return e, ""
    inp, decimal_number = decimal_and_real_number(inp)
    if len(inp) > 18:
        return "Maximum support is upto 18 digits", "maximum limit is 2 digits"
    if inp == '':
        inp = '0'
    amount = eng_numbers_to_words_0_to_999(inp, False)

    amount = amount.rstrip()
    cents = '' or decimal_number
    if cents:
        if len(cents) > 2:
            cents = cents[:2]
        cents = eng_numbers_to_words_0_to_99(cents, True)
        return amount, cents
    else:
        return amount, ""


def num2wordsTA(inp):
    inp = str(inp)
    inp = inp.replace(",", "")

    try:
        if isinstance(float(inp), (int, float)):
            pass
    except Exception as e:
        return e, ""
    inp, decimal_number = decimal_and_real_number(inp)
    if len(inp) > 18:
        return "Maximum support is upto 18 digits", "maximum limit is 2 digits"
    if inp == '':
        inp = '0'

    amount = tam_numbers_to_words_0_to_999(inp)
    amount = amount.rstrip()
    amount = re.sub(r'(ஒன்று)(?!\s*[\.\?!…“”"\'’»]*\s*$)', 'ஒரு', amount)
    cents = '' or decimal_number
    if cents:
        if len(cents) > 2:
            cents = cents[:2]
        cents = tam_numbers_to_words_0_to_99(cents, True)
        return amount, cents
    else:
        return amount, ""




