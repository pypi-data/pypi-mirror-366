import re

from .numbers_list import *


def decimal_and_real_number(inp):
    decimal_number = ''
    if inp.count(".") > 1:
        inp = inp.replace(".", "")
    elif inp.count(".") == 1:
        point_pos = inp.index(".")
        decimal_number = inp[point_pos + 1:]
        inp = re.sub(r"\..*", "", inp)
    elif inp.count(".") > 1:
        inp.replace(".", "")
    return inp, decimal_number
def eng_IND_above_1000(number, length):
    groups = []
    result = ''
    if length % 2 == 0:
        number = number.zfill(length+1)
    tail = number[-3:]
    head = number[:-3]
    head = [head[i:i+2] for i in range(0,len(head),2)]
    while(len(head)>0):
        groups.insert(0,head[-1:][0])
        head = head[:-1]
    groups.append(tail)
    group_length = len(groups)
    for i in groups:
        temp = eng_numbers_to_words_0_to_999(i,True)
        denomination = 0
        if group_length >= 1:
            denomination = group_length - 1
            group_length -= 1
            if temp == 'zero':
                continue
        result += temp +" " +indian_eng_above_thousand[denomination] + " "

    return result
def eng_SI_above_1000(number,length):
    groups = []
    result = ''
    zfill_num = [0,2,1]
    if length % 3 != 0:
        number = number.zfill(length + (zfill_num[length%3]))
    groups = [number[i:i+3] for i in range(0,len(number),3)]
    group_length = len(groups)
    for i in groups:
        temp = eng_numbers_to_words_0_to_999(i,True)
        denomination = 0
        if group_length >= 1:
            denomination = group_length - 1
            group_length -= 1
            if temp == 'zero':
                continue
        result += temp +" " +standard_international_eng_above_thousand[denomination] + " "

    return result
    pass
def eng_numbers_to_words_0_to_99(number, ispaise=None):
    if not ispaise:
        number = re.sub(r"^0+(?!$)", "", number)
    length = len(number)
    if length == 1:
        if ispaise:
            return eng_10_to_90[str(number)+"0"]
        return eng_0_to_9[str(number)]
    elif length == 2:
        if ispaise:
            number = re.sub(r"^0+(?!$)", "", number)
            if len(number) == 1:
                return eng_0_to_9[str(number)]
            elif int(number) < 20:
                return eng_10_to_19[str(number)]
            elif int(number) > 19:
                temp_number = str(number)[0] + '0'
                if int(str(number)[1]) > 0:
                    result = eng_10_to_90[temp_number] + ' ' + eng_0_to_9[str(number)[1]]
                else:
                    result = eng_10_to_90[temp_number]
                return result
        elif int(number) < 20:
            return eng_10_to_19[str(number)]
        elif int(number) > 19:
            temp_number = str(number)[0] + '0'
            if int(str(number)[1]) > 0:
                result = eng_10_to_90[temp_number] + ' ' + eng_0_to_9[str(number)[1]]
            else:
                result = eng_10_to_90[temp_number]
            return result

def eng_numbers_to_words_0_to_999(number,flag):
    number = re.sub(r"^0+(?!$)", "", number)
    length = len(str(number))
    temp_number = ''
    if length < 3:
        result = eng_numbers_to_words_0_to_99(number)
        return result
    if length == 3:
        if int(str(number)[1]) == 0 and int(str(number)[2]) == 0:
            return eng_100_to_900[str(number)]

        elif int(str(number)[1]) == 0 and int(str(number)[2]) != 0:
            result = eng_100_to_900[str(number)[0] + "00"] + " " + "and" + " " + eng_0_to_9[str(number)[2]]
            return result

        elif int(str(number)[1]) != 0 and int(str(number)[2]) == 0:


            result = eng_100_to_900[str(number)[0] + "00"] + ' ' + "and" + " " + eng_10_to_90[str(number)[1] + "0"]
            return result
        else:
            if int(str(number)[1]) == 1:
                result = eng_100_to_900[str(number)[0] + "00"] + ' ' + "and" + " " + eng_10_to_19[str(number)[1] + str(number)[1]]
                return result
            else:
                result = eng_100_to_900[str(number)[0] + "00"] + ' '+ "and" + " " + eng_10_to_90[str(number)[1] + "0"] + " " + eng_0_to_9[str(number)[2]]
            return result
    if length > 3:
        if flag:
            result = eng_IND_above_1000(number, length)
        else:
            result = eng_SI_above_1000(number,length)
        return result